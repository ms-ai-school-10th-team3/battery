# # services/custom_vision_out.py
# import os
# import requests
# import streamlit as st


# def get_secret(name):
#     value = os.getenv(name)

#     if value:
#         return value.strip()

#     try:
#         return st.secrets[name].strip()
#     except Exception:
#         raise RuntimeError(
#             f"'{name}' 값이 없습니다. Azure 환경 변수 또는 .streamlit/secrets.toml을 확인하세요."
#         )


# def predict_exterior_custom_vision(image_bytes):
#     url = get_secret("EXTERIOR_CUSTOM_VISION_URL")
#     key = get_secret("EXTERIOR_CUSTOM_VISION_KEY")

#     headers = {
#         "Prediction-Key": key,
#         "Content-Type": "application/octet-stream",
#         "Accept": "application/json",
#     }

#     response = requests.post(url, headers=headers, data=image_bytes)

#     if response.status_code != 200:
#         raise Exception(f"Status Code: {response.status_code}\nResponse: {response.text}")

#     if not response.content:
#         raise Exception(
#             "응답은 200인데 내용이 비어있습니다.\n"
#             f"URL: {url}\n"
#             f"Headers: {response.headers}"
#         )

#     return response.json()

# services/custom_vision_out.py
import os
import requests
import streamlit as st


def get_secret(name):
    value = os.getenv(name)

    if value:
        return value.strip()

    try:
        return str(st.secrets[name]).strip()
    except Exception:
        raise RuntimeError(
            f"'{name}' 값이 없습니다. Azure 환경 변수 또는 .streamlit/secrets.toml을 확인하세요."
        )


def call_custom_vision(image_bytes, url):
    key = get_secret("EXTERIOR_CUSTOM_VISION_KEY")

    headers = {
        "Prediction-Key": key,
        "Content-Type": "application/octet-stream",
        "Accept": "application/json",
    }

    response = requests.post(url, headers=headers, data=image_bytes)

    if response.status_code != 200:
        raise Exception(f"Status Code: {response.status_code}\nResponse: {response.text}")

    if not response.content:
        raise Exception(
            "응답은 200인데 내용이 비어있습니다.\n"
            f"URL: {url}\n"
            f"Headers: {response.headers}"
        )

    return response.json()


def find_prediction(raw_result, target_tag):
    target_tag = target_tag.lower()

    for pred in raw_result.get("predictions", []):
        tag_name = pred.get("tagName", "").lower()
        if tag_name == target_tag:
            return pred

    return None


def predict_exterior_custom_vision(image_bytes):
    """
    기존 단일 모델 호출 함수.
    혹시 다른 코드에서 쓰고 있을 수 있으니 유지.
    """
    url = get_secret("EXTERIOR_CUSTOM_VISION_URL")
    return call_custom_vision(image_bytes, url)


def predict_exterior_ensemble(image_bytes):
    """
    2-stage 외관 검사.

    1. Swelling 모델 먼저 호출
    2. Swelling 확률이 threshold 이상이면 Swelling 확정
    3. 아니면 5000장 모델 호출해서 Normal / Pollution / Damaged 판단
    """
    swelling_url = get_secret("EXTERIOR_SWELLING_URL")
    defect_url = get_secret("EXTERIOR_DEFECT_URL")
    threshold = float(get_secret("EXTERIOR_SWELLING_THRESHOLD"))

    # 1차: Swelling 모델 호출
    swelling_result = call_custom_vision(image_bytes, swelling_url)

    swelling_pred = find_prediction(swelling_result, "Swelling")
    swelling_prob = float(swelling_pred.get("probability", 0)) if swelling_pred else 0.0

    # Swelling 확률이 80% 이상이면 바로 Swelling 확정
    if swelling_prob >= threshold:
        return {
            "predictions": [
                {
                    "probability": swelling_prob,
                    "tagId": swelling_pred.get("tagId", "") if swelling_pred else "",
                    "tagName": "Swelling",
                }
            ],
            "ensemble_info": {
                "mode": "2-stage exterior ensemble",
                "selected_model": "SwellingDetector",
                "swelling_probability": swelling_prob,
                "threshold": threshold,
            },
            "raw_swelling_result": swelling_result,
        }

    # 2차: Swelling이 아니면 5000장 모델 호출
    defect_result = call_custom_vision(image_bytes, defect_url)

    defect_result["ensemble_info"] = {
        "mode": "2-stage exterior ensemble",
        "selected_model": "DefectClassifier",
        "swelling_probability": swelling_prob,
        "threshold": threshold,
    }
    defect_result["raw_swelling_result"] = swelling_result

    return defect_result
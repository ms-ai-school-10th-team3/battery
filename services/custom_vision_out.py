# services/custom_vision_out.py
import os
import requests
import streamlit as st


def get_secret(name):
    value = os.getenv(name)

    if value:
        return value.strip()

    try:
        return st.secrets[name].strip()
    except Exception:
        raise RuntimeError(
            f"'{name}' 값이 없습니다. Azure 환경 변수 또는 .streamlit/secrets.toml을 확인하세요."
        )


def predict_exterior_custom_vision(image_bytes):
    url = get_secret("EXTERIOR_CUSTOM_VISION_URL")
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
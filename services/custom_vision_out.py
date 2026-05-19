import requests
import streamlit as st

def predict_exterior_custom_vision(image_bytes):
    url = st.secrets["EXTERIOR_CUSTOM_VISION_URL"].strip()
    key = st.secrets["EXTERIOR_CUSTOM_VISION_KEY"].strip()

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
# services/api.py

import requests

BASE_URL = "http://팀원-api-url"

def predict_exterior(image_file):
    files = {"file": image_file}
    response = requests.post(f"{BASE_URL}/predict/exterior", files=files)
    response.raise_for_status()
    return response.json()

def predict_ct(image_file):
    files = {"file": image_file}
    response = requests.post(f"{BASE_URL}/predict/ct", files=files)
    response.raise_for_status()
    return response.json()

def get_report(report_id):
    response = requests.get(f"{BASE_URL}/reports/{report_id}")
    response.raise_for_status()
    return response.json()

def get_reports():
    response = requests.get(f"{BASE_URL}/reports")
    response.raise_for_status()
    return response.json()
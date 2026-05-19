# services/api.py

import os
import requests


# 나중에 팀원이 API URL 주면 여기만 바꾸면 됨
# 예: BASE_URL = "https://cellguard-api.azurewebsites.net"
BASE_URL = os.getenv("CELLGUARD_API_BASE_URL", "").strip()

TIMEOUT = 30


def _is_api_ready():
    return bool(BASE_URL)


def _post_image(endpoint, image_file):
    """
    이미지 파일을 API로 전송하는 공통 함수
    """
    if not _is_api_ready():
        raise RuntimeError("API_BASE_URL이 설정되지 않았습니다.")

    files = {
        "file": (
            getattr(image_file, "name", "uploaded_image.png"),
            image_file,
            getattr(image_file, "type", "image/png"),
        )
    }

    response = requests.post(
        f"{BASE_URL}{endpoint}",
        files=files,
        timeout=TIMEOUT,
    )

    response.raise_for_status()
    return response.json()


def predict_exterior(image_file):
    """
    외관 검사 API 호출
    API URL이 없으면 mock 데이터 반환
    """
    if not _is_api_ready():
        return mock_exterior_result()

    return _post_image("/predict/exterior", image_file)


def predict_ct(image_file):
    """
    CT 내부검사 API 호출
    API URL이 없으면 mock 데이터 반환
    """
    if not _is_api_ready():
        return mock_ct_result()

    return _post_image("/predict/ct", image_file)


def get_reports():
    """
    전체 보고서 목록 조회
    """
    if not _is_api_ready():
        return []

    response = requests.get(
        f"{BASE_URL}/reports",
        timeout=TIMEOUT,
    )

    response.raise_for_status()
    return response.json()


def get_report(report_id):
    """
    특정 보고서 상세 조회
    """
    if not _is_api_ready():
        return None

    response = requests.get(
        f"{BASE_URL}/reports/{report_id}",
        timeout=TIMEOUT,
    )

    response.raise_for_status()
    return response.json()


def mock_exterior_result():
    """
    API 연결 전 프론트 테스트용 외관 검사 결과
    """
    return {
        "battery_id": "B-001",
        "inspection_type": "외관 검사",
        "result": "불량",
        "risk_score": 82,
        "operator": "1",
        "line": "전체 라인",
        "confidence": 92,
        "defect_summary": "표면 긁힘 발생",
        "recommendation": "정밀 재검사 필요",
        "model_version": "Exterior-CNN-v1",
        "image_url": "",
        "heatmap_url": "",
    }


def mock_ct_result():
    """
    API 연결 전 프론트 테스트용 CT 검사 결과
    """
    return {
        "battery_id": "CT-001",
        "inspection_type": "CT 내부검사",
        "result": "불량",
        "risk_score": 76,
        "operator": "1",
        "line": "전체 라인",
        "confidence": 94,
        "defect_summary": "전극 정렬 이상, 내부 공극 이상, 분리막 변형 의심",
        "recommendation": "정밀 재검사 후 격리 및 원인 분석 권장",
        "model_version": "CT-CNN-v1",
        "image_url": "",
        "heatmap_url": "",
    }
# battery


# CNN 기반 이차전지 CT 이미지 불량 검출 시스템

## 1. 프로젝트 개요
이차전지 CT 이미지를 활용해 정상/불량 여부를 자동 분류하는 AI 기반 품질 검사 시스템입니다.

## 2. 문제 정의
이차전지 내부 결함은 안전성과 성능 저하로 이어질 수 있으며, CT 이미지를 사람이 직접 검사하는 방식은 시간과 비용이 많이 듭니다.

## 3. 사용 데이터
- CT_Datasets
- 라벨 기준: image_info.is_normal
- 정상: true
- 불량: false
- 불량 유형: porosity

## 4. 주요 기능
- CT 이미지 업로드
- CNN 기반 정상/불량 예측
- 예측 신뢰도 표시
- 검사 결과 안내 문구 제공

## 5. 기술 스택
- Python
- TensorFlow/Keras 또는 PyTorch
- FastAPI
- React
- Azure
- GitHub

## 6. 시스템 흐름
이미지 입력 → 전처리 → CNN 모델 예측 → 정상/불량 결과 반환 → 웹 화면 표시

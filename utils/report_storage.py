import os
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

# Azure App Service에서는 /home 경로가 저장용으로 더 안전함
if os.path.exists("/home"):
    REPORT_DIR = "/home/data"
else:
    REPORT_DIR = "data"

REPORT_PATH = os.path.join(REPORT_DIR, "reports.csv")

REPORT_COLUMNS = [
    "battery_id",
    "inspection_type",
    "result",
    "risk_score",
    "completed_at",
    "operator",
    "line",
    "confidence",
    "defect_summary",
    "recommendation",
    "model_version",
    "image_path",
    "heatmap_path",
    "overlay_path",
]


def load_reports():
    """
    reports.csv 전체 보고서 목록 불러오기
    inspection_report.py에서 목록 보여줄 때 사용
    """
    if not os.path.exists(REPORT_PATH):
        return pd.DataFrame(columns=REPORT_COLUMNS)

    df = pd.read_csv(REPORT_PATH)

    # 혹시 csv에 누락된 컬럼이 있으면 빈 값으로 채워서 오류 방지
    for col in REPORT_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df = df[REPORT_COLUMNS]

    # inspection_report.py에서 날짜 필터와 차트에 사용하므로 datetime 변환 필수
    df["completed_at"] = pd.to_datetime(df["completed_at"], errors="coerce")

    # 숫자 컬럼 변환
    df["risk_score"] = pd.to_numeric(df["risk_score"], errors="coerce").fillna(0).astype(int)
    df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce").fillna(0).astype(int)

    return df


def get_report_by_battery_id(battery_id):
    """
    battery_id 기준으로 개별 보고서 하나 조회
    report.py에서 상세 보고서 보여줄 때 사용
    """
    df = load_reports()

    if df.empty:
        return None

    result = df[df["battery_id"].astype(str) == str(battery_id)]

    if result.empty:
        return None

    # 같은 battery_id가 여러 개 있으면 가장 최근 검사 결과를 가져옴
    return result.iloc[-1].to_dict()


def save_inspection_report(
    battery_id,
    inspection_type,
    result,
    risk_score,
    operator,
    line,
    confidence,
    defect_summary,
    recommendation,
    model_version,
    image_path="",
    heatmap_path="",
    overlay_path="",
):
    os.makedirs(REPORT_DIR, exist_ok=True)

    new_report = {
        "battery_id": battery_id,
        "inspection_type": inspection_type,
        "result": result,
        "risk_score": risk_score,
        "completed_at": datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M"),
        "operator": operator,
        "line": line,
        "confidence": round(float(confidence) * 100, 2) if float(confidence) <= 1 else round(float(confidence), 2),
        "image_path": image_path,
        "heatmap_path": heatmap_path,
        "overlay_path": overlay_path,
        "defect_summary": defect_summary,
        "recommendation": recommendation,
        "model_version": model_version,
    }

    df = load_reports()

    df = pd.concat([df, pd.DataFrame([new_report])], ignore_index=True)
    df = df[REPORT_COLUMNS]

    df.to_csv(REPORT_PATH, index=False, encoding="utf-8-sig")
    print(f"[REPORT SAVE] path={REPORT_PATH}, rows={len(df)}")


# 💡 불러오기 함수 새로 추가!
def load_inspection_reports():
    """저장된 CSV 파일을 읽어서 DataFrame으로 반환합니다."""
    if os.path.exists(REPORT_PATH):
        return pd.read_csv(REPORT_PATH)
    else:
        return pd.DataFrame(columns=REPORT_COLUMNS)  # 파일이 없으면 빈 컬럼 틀만 반환
    
def clear_reports():
    """전체 보고서 이력 초기화"""
    os.makedirs(REPORT_DIR, exist_ok=True)
    empty_df = pd.DataFrame(columns=REPORT_COLUMNS)
    empty_df.to_csv(REPORT_PATH, index=False, encoding="utf-8-sig")
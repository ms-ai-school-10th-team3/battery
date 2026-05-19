import os
from datetime import datetime

import pandas as pd


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

    return df[REPORT_COLUMNS]


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
):
    os.makedirs(REPORT_DIR, exist_ok=True)

    new_report = {
        "battery_id": battery_id,
        "inspection_type": inspection_type,
        "result": result,
        "risk_score": risk_score,
        "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "operator": operator,
        "line": line,
        "confidence": confidence,
        "defect_summary": defect_summary,
        "recommendation": recommendation,
        "model_version": model_version,
    }

    df = load_reports()

    df = pd.concat([df, pd.DataFrame([new_report])], ignore_index=True)
    df = df[REPORT_COLUMNS]

    df.to_csv(REPORT_PATH, index=False, encoding="utf-8-sig")
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
REPORT_IMAGE_DIR = os.path.join(REPORT_DIR, "report_images")

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


def get_now_kst() -> str:
    """한국 시간 기준 현재 시각 문자열"""
    return datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")


def ensure_report_dirs():
    """보고서 저장 폴더 생성"""
    os.makedirs(REPORT_DIR, exist_ok=True)
    os.makedirs(REPORT_IMAGE_DIR, exist_ok=True)


def _load_reports_raw() -> pd.DataFrame:
    """
    저장용 raw reports.csv 로드.
    completed_at을 datetime으로 바꾸지 않고 문자열 상태로 유지한다.
    """
    ensure_report_dirs()

    if not os.path.exists(REPORT_PATH):
        return pd.DataFrame(columns=REPORT_COLUMNS)

    df = pd.read_csv(REPORT_PATH)

    for col in REPORT_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df = df[REPORT_COLUMNS]
    return df


def load_reports():
    """
    reports.csv 전체 보고서 목록 불러오기.
    inspection_report.py에서 목록/필터/차트 보여줄 때 사용.
    """
    df = _load_reports_raw()

    if df.empty:
        return pd.DataFrame(columns=REPORT_COLUMNS)

    # 날짜 컬럼 변환
    df["completed_at"] = pd.to_datetime(df["completed_at"], errors="coerce")

    # 숫자 컬럼 변환
    df["risk_score"] = pd.to_numeric(df["risk_score"], errors="coerce").fillna(0).astype(int)
    df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce").fillna(0).astype(int)

    return df[REPORT_COLUMNS]


def get_report_by_battery_id(battery_id):
    """
    battery_id 기준으로 개별 보고서 하나 조회.
    report.py에서 상세 보고서 보여줄 때 사용.
    """
    df = load_reports()

    if df.empty:
        return None

    result = df[df["battery_id"].astype(str) == str(battery_id)]

    if result.empty:
        return None

    # 같은 battery_id가 여러 개 있으면 가장 최근 검사 결과를 가져옴
    result = result.sort_values("completed_at", ascending=True)
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
    """
    외관/CT 검사 결과를 reports.csv에 저장.
    """
    ensure_report_dirs()

    completed_at = get_now_kst()

    new_report = {
        "battery_id": battery_id,
        "inspection_type": inspection_type,
        "result": result,
        "risk_score": risk_score,
        "completed_at": completed_at,
        "operator": operator,
        "line": line,
        "confidence": round(float(confidence) * 100, 2)
        if float(confidence) <= 1
        else round(float(confidence), 2),
        "defect_summary": defect_summary,
        "recommendation": recommendation,
        "model_version": model_version,
        "image_path": image_path,
        "heatmap_path": heatmap_path,
        "overlay_path": overlay_path,
    }

    df = _load_reports_raw()
    df = pd.concat([df, pd.DataFrame([new_report])], ignore_index=True)
    df = df[REPORT_COLUMNS]

    # completed_at이 비어 있는 행 보정
    df["completed_at"] = df["completed_at"].fillna("")
    empty_time_mask = df["completed_at"].astype(str).str.strip().isin(
        ["", "None", "NaT", "nan"]
    )
    df.loc[empty_time_mask, "completed_at"] = completed_at

    df.to_csv(REPORT_PATH, index=False, encoding="utf-8-sig")

    print(
        f"[REPORT SAVE] path={REPORT_PATH}, rows={len(df)}, completed_at={completed_at}"
    )


def load_inspection_reports():
    """
    저장된 검사 보고서를 DataFrame으로 반환.
    기존 코드 호환용 함수.
    """
    return load_reports()


def clear_reports():
    """전체 보고서 이력 초기화"""
    ensure_report_dirs()
    empty_df = pd.DataFrame(columns=REPORT_COLUMNS)
    empty_df.to_csv(REPORT_PATH, index=False, encoding="utf-8-sig")
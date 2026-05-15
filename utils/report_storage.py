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

    if os.path.exists(REPORT_PATH):
        df = pd.read_csv(REPORT_PATH)
    else:
        df = pd.DataFrame(columns=REPORT_COLUMNS)

    df = pd.concat([df, pd.DataFrame([new_report])], ignore_index=True)
    df = df[REPORT_COLUMNS]

    df.to_csv(REPORT_PATH, index=False, encoding="utf-8-sig")
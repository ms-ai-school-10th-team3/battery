import json
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_TYPE = "Exterior"  # "Exterior" 또는 "CT"

if DATA_TYPE == "Exterior":
    JSON_PATH = BASE_DIR / "data" / "Exterior" / "out_data.json"
else:
    JSON_PATH = BASE_DIR / "data" / "CT" / "ct_data.json"


def extract_defect_name(item):
    is_normal = item.get("is_normal", False)
    swelling = item.get("swelling", False)
    defects = item.get("defects", None)

    if is_normal:
        return "normal"

    if swelling:
        return "swelling"

    if defects is None:
        return "defect_unknown"

    if isinstance(defects, dict):
        return defects.get("name", "defect_unknown")

    if isinstance(defects, list):
        names = []
        for defect in defects:
            if isinstance(defect, dict) and "name" in defect:
                names.append(defect["name"])

        if len(names) == 0:
            return "defect_unknown"

        return names[0]

    return "defect_unknown"


with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

counter = Counter()

for item in data:
    label = extract_defect_name(item)
    counter[label] += 1

print(f"\n[{DATA_TYPE}] 결함 클래스 개수 확인")
print("=" * 50)

for label, count in counter.most_common():
    print(f"{label}: {count}")

print("\n전체 클래스 목록:")
print(list(counter.keys()))
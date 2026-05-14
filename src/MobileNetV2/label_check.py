import json

with open("train/ct_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

normal_count = sum(1 for item in data if item["is_normal"] is True)
defect_count = sum(1 for item in data if item["is_normal"] is False)

print("정상:", normal_count)
print("불량:", defect_count)
print("전체:", len(data))
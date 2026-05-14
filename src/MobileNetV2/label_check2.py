import json
from pathlib import Path
from collections import Counter

# =========================
# 경로 설정
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent

CT_JSON_PATH = BASE_DIR / "data" / "CT" / "ct_data.json"
EXTERIOR_JSON_PATH = BASE_DIR / "data" / "Exterior" / "out_data.json"

CT_IMG_DIR = BASE_DIR / "data" / "CT" / "VS_CT_Datasets_images"
EXTERIOR_IMG_DIR = BASE_DIR / "data" / "Exterior" / "VS_Exterior_Img_Datasets_images"


def load_json(json_path):
    """JSON 파일 로드"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def print_json_summary(name, data):
    """JSON 전체 구조 요약"""
    print("\n" + "=" * 80)
    print(f"[{name}] JSON 구조 확인")
    print("=" * 80)

    print(f"데이터 타입: {type(data)}")

    if isinstance(data, list):
        print(f"총 데이터 개수: {len(data)}")

        if len(data) > 0:
            first = data[0]
            print(f"\n첫 번째 데이터 타입: {type(first)}")

            if isinstance(first, dict):
                print("\n첫 번째 데이터 key 목록:")
                for key in first.keys():
                    print(f" - {key}")

                print("\n첫 번째 데이터 전체 출력:")
                print(json.dumps(first, ensure_ascii=False, indent=2))

    elif isinstance(data, dict):
        print(f"최상위 key 목록:")
        for key in data.keys():
            print(f" - {key}")

        print("\n최상위 일부 출력:")
        print(json.dumps(data, ensure_ascii=False, indent=2)[:3000])

        # dict 안에 list가 들어있는 경우 찾기
        print("\nlist 형태로 들어있는 key 후보:")
        for key, value in data.items():
            if isinstance(value, list):
                print(f" - {key}: {len(value)}개")
                if len(value) > 0 and isinstance(value[0], dict):
                    print(f"   첫 번째 item keys: {list(value[0].keys())}")


def find_records(data):
    """
    JSON이 list면 그대로 반환,
    dict면 내부에 있는 list 중 가장 데이터가 많아 보이는 것을 반환
    """
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        list_candidates = []

        for key, value in data.items():
            if isinstance(value, list):
                list_candidates.append((key, value))

        if list_candidates:
            # 가장 긴 list를 실제 데이터 records로 추정
            key, records = max(list_candidates, key=lambda x: len(x[1]))
            print(f"\n실제 데이터 목록으로 추정되는 key: {key}")
            return records

    return []


def analyze_keys(name, records):
    """전체 데이터에서 key 빈도 확인"""
    print("\n" + "-" * 80)
    print(f"[{name}] 전체 key 빈도 확인")
    print("-" * 80)

    key_counter = Counter()

    for item in records:
        if isinstance(item, dict):
            key_counter.update(item.keys())

    for key, count in key_counter.most_common():
        print(f"{key}: {count}")


def find_possible_label_columns(name, records):
    """정상/불량 라벨로 보이는 컬럼 후보 찾기"""
    print("\n" + "-" * 80)
    print(f"[{name}] 라벨 후보 컬럼 확인")
    print("-" * 80)

    possible_keywords = [
        "label", "class", "category", "normal", "defect",
        "fault", "abnormal", "status", "result",
        "is_normal", "is_defect"
    ]

    if not records:
        print("records가 비어 있습니다.")
        return

    sample = records[:100]

    all_keys = set()
    for item in sample:
        if isinstance(item, dict):
            all_keys.update(item.keys())

    candidate_keys = [
        key for key in all_keys
        if any(keyword.lower() in key.lower() for keyword in possible_keywords)
    ]

    if not candidate_keys:
        print("라벨로 보이는 key를 자동으로 찾지 못했습니다.")
        print("위의 key 목록과 첫 번째 데이터 출력을 보고 직접 확인해야 합니다.")
        return

    for key in candidate_keys:
        values = []

        for item in records:
            if isinstance(item, dict) and key in item:
                value = item[key]

                # list/dict는 그대로 카운트하기 어려우니까 문자열화
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, ensure_ascii=False)

                values.append(value)

        counter = Counter(values)

        print(f"\n후보 key: {key}")
        print(f"값 종류 개수: {len(counter)}")
        print("상위 값:")
        for value, count in counter.most_common(20):
            print(f" - {value}: {count}")


def find_possible_filename_columns(name, records):
    """이미지 파일명으로 보이는 컬럼 후보 찾기"""
    print("\n" + "-" * 80)
    print(f"[{name}] 이미지 파일명 후보 컬럼 확인")
    print("-" * 80)

    possible_keywords = [
        "file", "filename", "image", "img", "path", "name"
    ]

    if not records:
        print("records가 비어 있습니다.")
        return

    sample = records[:100]

    all_keys = set()
    for item in sample:
        if isinstance(item, dict):
            all_keys.update(item.keys())

    candidate_keys = [
        key for key in all_keys
        if any(keyword.lower() in key.lower() for keyword in possible_keywords)
    ]

    if not candidate_keys:
        print("이미지 파일명으로 보이는 key를 자동으로 찾지 못했습니다.")
        return

    for key in candidate_keys:
        print(f"\n후보 key: {key}")
        printed = 0

        for item in records:
            if isinstance(item, dict) and key in item:
                value = item[key]
                print(f" - {value}")
                printed += 1

            if printed >= 10:
                break


def check_image_folder(name, img_dir):
    """이미지 폴더 내 파일 개수 확인"""
    print("\n" + "-" * 80)
    print(f"[{name}] 이미지 폴더 확인")
    print("-" * 80)

    if not img_dir.exists():
        print(f"이미지 폴더가 존재하지 않습니다: {img_dir}")
        return

    image_extensions = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp"]

    image_files = []
    for ext in image_extensions:
        image_files.extend(list(img_dir.glob(ext)))

    print(f"이미지 폴더 경로: {img_dir}")
    print(f"이미지 파일 개수: {len(image_files)}")

    print("\n이미지 파일 샘플:")
    for path in image_files[:10]:
        print(f" - {path.name}")


def run_check(name, json_path, img_dir):
    print("\n\n")
    print("#" * 100)
    print(f"{name} 데이터 확인 시작")
    print("#" * 100)

    if not json_path.exists():
        print(f"JSON 파일이 존재하지 않습니다: {json_path}")
        return

    data = load_json(json_path)

    print_json_summary(name, data)

    records = find_records(data)

    print(f"\nrecords 추정 개수: {len(records)}")

    analyze_keys(name, records)
    find_possible_filename_columns(name, records)
    find_possible_label_columns(name, records)
    check_image_folder(name, img_dir)


if __name__ == "__main__":
    run_check("CT", CT_JSON_PATH, CT_IMG_DIR)
    run_check("Exterior", EXTERIOR_JSON_PATH, EXTERIOR_IMG_DIR)
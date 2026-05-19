import time
import json
from pathlib import Path
from datetime import datetime

import torch
import numpy as np
from PIL import Image

from modeling.deeplab import DeepLab


BASE_DIR = Path(__file__).resolve().parent

WEIGHT_PATH = BASE_DIR / "weights" / "model_best.pth"
RESULT_DIR = BASE_DIR / "results"
UPLOAD_DIR = BASE_DIR / "uploads"
TEST_IMAGE_DIR = BASE_DIR / "test_images"

NUM_CLASSES = 4
BACKBONE = "mobilenet"
OUTPUT_STRIDE = 16
INPUT_SIZE = 512

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

CLASS_NAMES = {
    0: "background",
    1: "resin_overflow",
    2: "porosity",
    3: "battery_outline",
}

DEFECT_CLASSES = {
    1: "resin_overflow",
    2: "porosity",
}

OUTLINE_CLASS = 3

OVERLAY_COLORS = {
    1: np.array([255, 0, 0], dtype=np.uint8),
    2: np.array([0, 255, 0], dtype=np.uint8),
    3: np.array([0, 0, 255], dtype=np.uint8),
}

DEFECT_PIXEL_THRESHOLD = 50
OUTLINE_PIXEL_THRESHOLD = 1000
OVERLAY_ALPHA = 0.5


def load_model():
    if not WEIGHT_PATH.exists():
        raise FileNotFoundError(f"모델 파일 없음: {WEIGHT_PATH}")

    model = DeepLab(
        num_classes=NUM_CLASSES,
        backbone=BACKBONE,
        output_stride=OUTPUT_STRIDE,
        sync_bn=False,
        freeze_bn=False,
    )

    checkpoint = torch.load(str(WEIGHT_PATH), map_location=DEVICE, weights_only=False)

    if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
        state_dict = checkpoint["state_dict"]
    else:
        state_dict = checkpoint

    clean_state_dict = {}
    for k, v in state_dict.items():
        clean_state_dict[k.replace("module.", "", 1) if k.startswith("module.") else k] = v

    model.load_state_dict(clean_state_dict, strict=True)
    model.to(DEVICE)
    model.eval()

    return model


MODEL = load_model()


def preprocess_image(image_path):
    image_path = Path(image_path)

    image = Image.open(image_path).convert("RGB")
    original_size = image.size

    image = image.resize((INPUT_SIZE, INPUT_SIZE), Image.BILINEAR)
    image_np = np.array(image).astype(np.float32) / 255.0

    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    image_np = (image_np - mean) / std

    image_np = image_np.transpose(2, 0, 1)
    tensor = torch.from_numpy(image_np).unsqueeze(0).float().to(DEVICE)

    return tensor, original_size


def create_result_dir():
    today_str = datetime.now().strftime("%Y-%m-%d")

    date_dir = RESULT_DIR / today_str
    date_dir.mkdir(parents=True, exist_ok=True)

    existing_numbers = []

    for item in date_dir.iterdir():
        if item.is_dir() and item.name.isdigit():
            existing_numbers.append(int(item.name))

    next_number = max(existing_numbers, default=0) + 1

    sample_result_dir = date_dir / str(next_number)
    sample_result_dir.mkdir(parents=True, exist_ok=True)

    result_id = f"{today_str}/{next_number}"

    return sample_result_dir, result_id


def save_overlay(image_path, pred_mask, save_path):
    image = Image.open(image_path).convert("RGB")
    image = image.resize((INPUT_SIZE, INPUT_SIZE), Image.BILINEAR)

    overlay = np.array(image).copy()

    for cls, color in OVERLAY_COLORS.items():
        area = pred_mask == cls
        overlay[area] = (
            overlay[area] * (1 - OVERLAY_ALPHA) + color * OVERLAY_ALPHA
        ).astype(np.uint8)

    Image.fromarray(overlay).save(str(save_path))


def save_raw_mask(pred_mask, save_path):
    Image.fromarray(pred_mask.astype(np.uint8)).save(str(save_path))


def save_colored_mask(pred_mask, save_path):
    color_mask = np.zeros(
        (pred_mask.shape[0], pred_mask.shape[1], 3),
        dtype=np.uint8
    )

    for cls, color in OVERLAY_COLORS.items():
        color_mask[pred_mask == cls] = color

    Image.fromarray(color_mask).save(str(save_path))


def save_original_as_jpg(image_path, save_path):
    image = Image.open(image_path).convert("RGB")
    image.save(str(save_path), "JPEG", quality=95)


def judge_prediction(pred_mask):
    total_pixels = int(pred_mask.size)

    all_class_pixel_counts = {}
    all_class_ratios = {}

    for cls, name in CLASS_NAMES.items():
        pixels = int(np.sum(pred_mask == cls))
        all_class_pixel_counts[name] = pixels
        all_class_ratios[name] = round(pixels / total_pixels * 100, 4)

    outline_pixels = int(np.sum(pred_mask == OUTLINE_CLASS))
    battery_outline_detected = outline_pixels >= OUTLINE_PIXEL_THRESHOLD

    defect_types = []
    defect_pixel_counts = {}
    defect_ratios = {}

    for cls, name in DEFECT_CLASSES.items():
        pixels = int(np.sum(pred_mask == cls))
        ratio = pixels / total_pixels * 100

        defect_pixel_counts[name] = pixels
        defect_ratios[name] = round(ratio, 4)

        if pixels >= DEFECT_PIXEL_THRESHOLD:
            defect_types.append(name)

    defect_exists = len(defect_types) > 0
    abnormal = defect_exists

    return {
        "battery_outline_detected": bool(battery_outline_detected),
        "battery_outline_pixels": outline_pixels,
        "defect_exists": bool(defect_exists),
        "defect_types": defect_types,
        "defect_pixel_counts": defect_pixel_counts,
        "defect_ratios": defect_ratios,
        "swelling": None,
        "final_result": "abnormal" if abnormal else "normal",
        "abnormal": bool(abnormal),
        "all_class_pixel_counts": all_class_pixel_counts,
        "all_class_ratios": all_class_ratios,
    }


def predict_one_image(image_path):
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"이미지 파일 없음: {image_path}")

    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    started = time.time()

    tensor, original_size = preprocess_image(image_path)

    with torch.no_grad():
        output = MODEL(tensor)
        pred_mask = (
            torch.argmax(output, dim=1)
            .squeeze(0)
            .cpu()
            .numpy()
            .astype(np.uint8)
        )

    sample_result_dir, result_id = create_result_dir()

    original_copy_path = sample_result_dir / "original.jpg"
    raw_mask_path = sample_result_dir / "raw_mask.png"
    colored_mask_path = sample_result_dir / "colored_mask.png"
    overlay_path = sample_result_dir / "overlay.png"
    json_path = sample_result_dir / "result.json"

    save_original_as_jpg(image_path, original_copy_path)
    save_raw_mask(pred_mask, raw_mask_path)
    save_colored_mask(pred_mask, colored_mask_path)
    save_overlay(image_path, pred_mask, overlay_path)

    judgement = judge_prediction(pred_mask)
    elapsed = time.time() - started

    result = {
        "id": result_id,
        "filename": image_path.name,
        "original_size": {
            "width": original_size[0],
            "height": original_size[1],
        },
        "model_input_size": {
            "width": INPUT_SIZE,
            "height": INPUT_SIZE,
        },
        "elapsed_sec": round(elapsed, 4),
        "judgement": judgement,
        "files": {
            "original": str(original_copy_path.relative_to(BASE_DIR)).replace("\\", "/"),
            "raw_mask": str(raw_mask_path.relative_to(BASE_DIR)).replace("\\", "/"),
            "colored_mask": str(colored_mask_path.relative_to(BASE_DIR)).replace("\\", "/"),
            "overlay": str(overlay_path.relative_to(BASE_DIR)).replace("\\", "/"),
            "result_json": str(json_path.relative_to(BASE_DIR)).replace("\\", "/"),
        },
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result


if __name__ == "__main__":
    test_image_path = TEST_IMAGE_DIR / "CT_module_pouch_407_y_194.jpg"

    if not test_image_path.exists():
        raise FileNotFoundError(f"테스트 이미지 없음: {test_image_path}")

    result = predict_one_image(test_image_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
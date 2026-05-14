import json
import ast
import random
from pathlib import Path
from collections import Counter

import pandas as pd

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, Subset

from torchvision import models, transforms
from PIL import Image

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

import matplotlib.pyplot as plt


# =========================
# 1. 기본 설정
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent

# "Exterior" 또는 "CT"
# 외관 5K 돌릴 때: DATA_TYPE = "Exterior"
# CT 5K 돌릴 때: DATA_TYPE = "CT"
DATA_TYPE = "CT"

if DATA_TYPE == "Exterior":
    CSV_PATH = BASE_DIR / "data" / "Exterior" / "out_data5K.csv"
    IMG_DIR = BASE_DIR / "data" / "Exterior" / "VS_Exterior_Img_Datasets_images"

elif DATA_TYPE == "CT":
    CSV_PATH = BASE_DIR / "data" / "CT" / "ct_data5K.csv"
    IMG_DIR = BASE_DIR / "data" / "CT" / "VS_CT_Datasets_images"

else:
    raise ValueError("DATA_TYPE은 'Exterior' 또는 'CT'만 가능합니다.")

RESULT_DIR = BASE_DIR / "results" / f"{DATA_TYPE}_defect_type"
MODEL_DIR = BASE_DIR / "models"

RESULT_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

BATCH_SIZE = 16
EPOCHS = 5
LEARNING_RATE = 0.0001
IMG_SIZE = 224
SEED = 42

random.seed(SEED)
torch.manual_seed(SEED)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"사용 장치: {DEVICE}")
print(f"학습 데이터 종류: {DATA_TYPE}")
print(f"CSV 경로: {CSV_PATH}")
print(f"이미지 폴더 경로: {IMG_DIR}")


# =========================
# 2. CSV 문자열 파싱 함수
# =========================

def parse_csv_value(value):
    """
    CSV 안에 들어있는 문자열 형태의 list/dict/bool 값을
    실제 Python 객체로 바꿔주는 함수
    """

    if pd.isna(value):
        return None

    if isinstance(value, bool):
        return value

    if isinstance(value, (dict, list)):
        return value

    value = str(value).strip()

    if value == "":
        return None

    # bool 문자열 처리
    if value.lower() == "true":
        return True

    if value.lower() == "false":
        return False

    if value.lower() in ["none", "null", "nan"]:
        return None

    # JSON / Python dict-list 문자열 처리
    try:
        return ast.literal_eval(value)
    except Exception:
        return value


# =========================
# 3. defects에서 결함명 추출
# =========================

def extract_defect_name(item):
    """
    CSV 한 줄 item에서 대표 라벨 추출

    normal:
        is_normal == True

    defect:
        swelling == True이면 swelling
        defects 안에 name이 있으면 해당 결함명
        둘 다 없으면 defect_unknown
    """

    is_normal = parse_csv_value(item.get("is_normal", False))
    swelling = parse_csv_value(item.get("swelling", False))
    defects = parse_csv_value(item.get("defects", None))

    if is_normal is True:
        return "normal"

    if swelling is True:
        return "swelling"

    if defects is None:
        return "defect_unknown"

    # defects가 dict 형태인 경우
    # 예: {"name": "Pollution", "points": [...]}
    if isinstance(defects, dict):
        return defects.get("name", "defect_unknown")

    # defects가 list 형태인 경우
    # 예: [{"name": "Pollution", ...}, {"name": "Damaged", ...}]
    if isinstance(defects, list):
        names = []

        for defect in defects:
            if isinstance(defect, dict) and "name" in defect:
                names.append(defect["name"])

        if len(names) == 0:
            return "defect_unknown"

        # 여러 결함이 있으면 첫 번째 결함을 대표 라벨로 사용
        return names[0]

    return "defect_unknown"


# =========================
# 4. 데이터셋 클래스
# =========================

class BatteryDefectTypeDataset(Dataset):
    def __init__(self, csv_path, img_dir, transform=None):
        self.csv_path = Path(csv_path)
        self.img_dir = Path(img_dir)
        self.transform = transform

        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {self.csv_path}")

        if not self.img_dir.exists():
            raise FileNotFoundError(f"이미지 폴더를 찾을 수 없습니다: {self.img_dir}")

        df = pd.read_csv(self.csv_path)

        print("\nCSV 컬럼 목록:")
        print(df.columns.tolist())

        if "file_name" not in df.columns:
            raise ValueError("CSV에 'file_name' 컬럼이 없습니다. 컬럼명을 확인하세요.")

        records = []

        for _, row in df.iterrows():
            item = row.to_dict()

            file_name = str(item["file_name"]).strip()
            img_path = self.img_dir / file_name

            if not img_path.exists():
                print(f"이미지 없음: {img_path}")
                continue

            label_name = extract_defect_name(item)

            records.append({
                "img_path": img_path,
                "label_name": label_name,
                "file_name": file_name
            })

        if len(records) == 0:
            raise ValueError("사용 가능한 이미지가 없습니다. file_name과 이미지 폴더 경로를 확인하세요.")

        label_names = sorted(list(set(record["label_name"] for record in records)))

        self.label_to_idx = {label: idx for idx, label in enumerate(label_names)}
        self.idx_to_label = {idx: label for label, idx in self.label_to_idx.items()}

        self.samples = []

        for record in records:
            label_idx = self.label_to_idx[record["label_name"]]
            self.samples.append({
                "img_path": record["img_path"],
                "label": label_idx,
                "label_name": record["label_name"],
                "file_name": record["file_name"]
            })

        print(f"\n사용 가능한 이미지 개수: {len(self.samples)}")
        print(f"클래스 개수: {len(self.label_to_idx)}")

        print("\n클래스 목록:")
        for label, idx in self.label_to_idx.items():
            print(f"  {idx}: {label}")

        print("\n라벨 개수:")
        counter = Counter(sample["label_name"] for sample in self.samples)
        for label, count in counter.most_common():
            print(f"  {label}: {count}")

        # label mapping 저장
        mapping_path = RESULT_DIR / "label_mapping.json"
        with open(mapping_path, "w", encoding="utf-8") as f:
            json.dump(self.label_to_idx, f, ensure_ascii=False, indent=2)

        print(f"\n라벨 매핑 저장 완료: {mapping_path}")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]

        img_path = sample["img_path"]
        label = sample["label"]

        image = Image.open(img_path).convert("RGB")

        if self.transform:
            image = self.transform(image)

        return image, label


# =========================
# 5. 이미지 전처리
# =========================

train_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

val_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# =========================
# 6. 데이터 로드
# =========================

train_base_dataset = BatteryDefectTypeDataset(
    csv_path=CSV_PATH,
    img_dir=IMG_DIR,
    transform=train_transform
)

val_base_dataset = BatteryDefectTypeDataset(
    csv_path=CSV_PATH,
    img_dir=IMG_DIR,
    transform=val_transform
)

labels = [sample["label"] for sample in train_base_dataset.samples]
indices = list(range(len(train_base_dataset)))

# 클래스별 비율을 최대한 유지하면서 train/val 분리
try:
    train_indices, val_indices = train_test_split(
        indices,
        test_size=0.2,
        random_state=SEED,
        stratify=labels
    )
except ValueError:
    print("\n일부 클래스 개수가 너무 적어서 stratify 분할이 불가능합니다.")
    print("일반 랜덤 분할로 진행합니다.")
    train_indices, val_indices = train_test_split(
        indices,
        test_size=0.2,
        random_state=SEED
    )

train_dataset = Subset(train_base_dataset, train_indices)
val_dataset = Subset(val_base_dataset, val_indices)

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False
)

print(f"\ntrain 개수: {len(train_dataset)}")
print(f"val 개수: {len(val_dataset)}")


# =========================
# 7. 클래스 불균형 대응용 weight
# =========================

num_classes = len(train_base_dataset.label_to_idx)

train_labels = [train_base_dataset.samples[i]["label"] for i in train_indices]
label_counter = Counter(train_labels)

class_weights = []

for class_idx in range(num_classes):
    count = label_counter.get(class_idx, 1)
    weight = len(train_labels) / (num_classes * count)
    class_weights.append(weight)

class_weights = torch.tensor(class_weights, dtype=torch.float).to(DEVICE)

print("\n클래스 가중치:")
for idx, weight in enumerate(class_weights.cpu().numpy()):
    print(f"  {train_base_dataset.idx_to_label[idx]}: {weight:.4f}")


# =========================
# 8. MobileNetV2 모델 가져오기
# =========================

model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)

# 기존 ImageNet 1000개 분류층을 현재 클래스 개수에 맞게 변경
in_features = model.classifier[1].in_features
model.classifier[1] = nn.Linear(in_features, num_classes)

model = model.to(DEVICE)


# =========================
# 9. 손실 함수와 optimizer
# =========================

criterion = nn.CrossEntropyLoss(weight=class_weights)
optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)


# =========================
# 10. 학습 함수
# =========================

def train_one_epoch(model, loader):
    model.train()

    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in loader:
        images = images.to(DEVICE)
        labels = labels.to(DEVICE)

        optimizer.zero_grad()

        outputs = model(images)
        loss = criterion(outputs, labels)

        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)

        _, preds = torch.max(outputs, 1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)

    epoch_loss = running_loss / total
    epoch_acc = correct / total

    return epoch_loss, epoch_acc


# =========================
# 11. 평가 함수
# =========================

def evaluate(model, loader):
    model.eval()

    running_loss = 0.0
    correct = 0
    total = 0

    all_labels = []
    all_preds = []

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(DEVICE)
            labels = labels.to(DEVICE)

            outputs = model(images)
            loss = criterion(outputs, labels)

            running_loss += loss.item() * images.size(0)

            _, preds = torch.max(outputs, 1)

            correct += (preds == labels).sum().item()
            total += labels.size(0)

            all_labels.extend(labels.cpu().numpy())
            all_preds.extend(preds.cpu().numpy())

    epoch_loss = running_loss / total
    epoch_acc = correct / total

    return epoch_loss, epoch_acc, all_labels, all_preds


# =========================
# 12. 학습 실행
# =========================

train_losses = []
val_losses = []
train_accs = []
val_accs = []

y_true = []
y_pred = []

for epoch in range(EPOCHS):
    train_loss, train_acc = train_one_epoch(model, train_loader)
    val_loss, val_acc, y_true, y_pred = evaluate(model, val_loader)

    train_losses.append(train_loss)
    val_losses.append(val_loss)
    train_accs.append(train_acc)
    val_accs.append(val_acc)

    print(f"\nEpoch [{epoch + 1}/{EPOCHS}]")
    print(f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f}")
    print(f"Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.4f}")


# =========================
# 13. 최종 평가 결과 출력
# =========================

target_names = [
    train_base_dataset.idx_to_label[i]
    for i in range(num_classes)
]

print("\n분류 리포트")
print(classification_report(
    y_true,
    y_pred,
    labels=list(range(num_classes)),
    target_names=target_names,
    zero_division=0
))

print("\nConfusion Matrix")
cm = confusion_matrix(y_true, y_pred, labels=list(range(num_classes)))
print(cm)


# =========================
# 14. 그래프 저장
# =========================

plt.figure()
plt.plot(train_losses, label="train_loss")
plt.plot(val_losses, label="val_loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.legend()
plt.title(f"{DATA_TYPE} Defect Type Loss")
plt.savefig(RESULT_DIR / "loss_graph.png")
plt.close()

plt.figure()
plt.plot(train_accs, label="train_acc")
plt.plot(val_accs, label="val_acc")
plt.xlabel("Epoch")
plt.ylabel("Accuracy")
plt.legend()
plt.title(f"{DATA_TYPE} Defect Type Accuracy")
plt.savefig(RESULT_DIR / "accuracy_graph.png")
plt.close()


# =========================
# 15. 모델 저장
# =========================

model_save_path = MODEL_DIR / f"{DATA_TYPE}_defect_type_mobilenetv2.pth"

torch.save({
    "model_state_dict": model.state_dict(),
    "label_to_idx": train_base_dataset.label_to_idx,
    "idx_to_label": train_base_dataset.idx_to_label,
    "data_type": DATA_TYPE
}, model_save_path)

print(f"\n모델 저장 완료: {model_save_path}")
print(f"결과 그래프 저장 위치: {RESULT_DIR}")
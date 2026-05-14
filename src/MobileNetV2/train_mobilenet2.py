import json
import random
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split

from torchvision import models, transforms
from PIL import Image

from sklearn.metrics import classification_report, confusion_matrix

import matplotlib.pyplot as plt


# =========================
# 1. 기본 설정
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_TYPE = "Exterior"   # "Exterior" 또는 "CT"

if DATA_TYPE == "Exterior":
    JSON_PATH = BASE_DIR / "data" / "Exterior" / "out_data.json"
    IMG_DIR = BASE_DIR / "data" / "Exterior" / "VS_Exterior_Img_Datasets_images"
elif DATA_TYPE == "CT":
    JSON_PATH = BASE_DIR / "data" / "CT" / "ct_data.json"
    IMG_DIR = BASE_DIR / "data" / "CT" / "VS_CT_Datasets_images"
else:
    raise ValueError("DATA_TYPE은 'Exterior' 또는 'CT'만 가능합니다.")

RESULT_DIR = BASE_DIR / "results" / DATA_TYPE
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


# =========================
# 2. 데이터셋 클래스
# =========================

class BatteryDataset(Dataset):
    def __init__(self, json_path, img_dir, transform=None):
        self.json_path = Path(json_path)
        self.img_dir = Path(img_dir)
        self.transform = transform
        self.samples = []

        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in data:
            file_name = item["file_name"]
            is_normal = item["is_normal"]

            img_path = self.img_dir / file_name

            if not img_path.exists():
                print(f"이미지 없음: {img_path}")
                continue

            # normal = 0, defect = 1
            label = 0 if is_normal else 1

            self.samples.append((img_path, label))

        print(f"사용 가능한 이미지 개수: {len(self.samples)}")

        normal_count = sum(1 for _, label in self.samples if label == 0)
        defect_count = sum(1 for _, label in self.samples if label == 1)

        print(f"normal 개수: {normal_count}")
        print(f"defect 개수: {defect_count}")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]

        image = Image.open(img_path).convert("RGB")

        if self.transform:
            image = self.transform(image)

        return image, label


# =========================
# 3. 이미지 전처리
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
# 4. 데이터 로드 및 분리
# =========================

full_dataset = BatteryDataset(
    json_path=JSON_PATH,
    img_dir=IMG_DIR,
    transform=train_transform
)

total_size = len(full_dataset)

if total_size == 0:
    raise ValueError("사용 가능한 이미지가 없습니다. JSON의 file_name과 이미지 폴더를 확인하세요.")

train_size = int(total_size * 0.8)
val_size = total_size - train_size

train_dataset, val_dataset = random_split(
    full_dataset,
    [train_size, val_size],
    generator=torch.Generator().manual_seed(SEED)
)

# 검증 데이터에는 회전/뒤집기 같은 augmentation이 들어가면 안 되므로 transform 교체
val_dataset.dataset.transform = val_transform

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

print(f"train 개수: {train_size}")
print(f"val 개수: {val_size}")


# =========================
# 5. MobileNetV2 CNN 모델 가져오기
# =========================

model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)

# 기존 ImageNet 1000개 분류층을 normal/defect 2개 분류층으로 교체
in_features = model.classifier[1].in_features
model.classifier[1] = nn.Linear(in_features, 2)

model = model.to(DEVICE)


# =========================
# 6. 손실 함수와 optimizer
# =========================

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)


# =========================
# 7. 학습 함수
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
# 8. 평가 함수
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
# 9. 학습 실행
# =========================

train_losses = []
val_losses = []
train_accs = []
val_accs = []

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
# 10. 최종 평가 결과 출력
# =========================

print("\n분류 리포트")
print(classification_report(
    y_true,
    y_pred,
    target_names=["normal", "defect"]
))

print("\nConfusion Matrix")
cm = confusion_matrix(y_true, y_pred)
print(cm)


# =========================
# 11. 그래프 저장
# =========================

plt.figure()
plt.plot(train_losses, label="train_loss")
plt.plot(val_losses, label="val_loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.legend()
plt.title(f"{DATA_TYPE} Loss")
plt.savefig(RESULT_DIR / "loss_graph.png")
plt.close()

plt.figure()
plt.plot(train_accs, label="train_acc")
plt.plot(val_accs, label="val_acc")
plt.xlabel("Epoch")
plt.ylabel("Accuracy")
plt.legend()
plt.title(f"{DATA_TYPE} Accuracy")
plt.savefig(RESULT_DIR / "accuracy_graph.png")
plt.close()


# =========================
# 12. 모델 저장
# =========================

model_save_path = MODEL_DIR / f"{DATA_TYPE}_mobilenetv2.pth"
torch.save(model.state_dict(), model_save_path)

print(f"\n모델 저장 완료: {model_save_path}")
print(f"결과 그래프 저장 위치: {RESULT_DIR}")
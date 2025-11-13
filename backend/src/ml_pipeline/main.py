import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import json  # ⭐ 1. Thêm thư viện JSON
import os    # ⭐ 2. Thêm thư viện OS

# --- Sửa lại đường dẫn import để chạy từ gốc (theo lỗi ở lần trước) ---
from .model.model import model
from .train.train import run
from backend.src.ml_pipeline.dataset import Img_Segmentation_Dataset, train_transform, valid_transform

# ===================================================================
# CẤU HÌNH
# ===================================================================
NUM_EPOCHS = 20
NUM_CLASSES = 4
BATCH_SIZE = 8 # ⭐ 3. Định nghĩa BATCH_SIZE ở một nơi

# --- Sửa lại đường dẫn: DVC chạy từ thư mục gốc của dự án ---
# Vì vậy, không cần '../'
DATASET_ROOT = "backend/public/data/"
ANNOTATION_FILE = "backend/public/processed/annotations.json"

# ⭐ 4. Đường dẫn đến file ID (output của bước DVC trước)
TRAIN_IDS_PATH = "backend/public/processed/train_ids.json"
VALID_IDS_PATH = "backend/public/processed/valid_ids.json"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# --- Khởi tạo các thành phần ---
model = model.to(device) # ⭐ 5. Gửi model sang device
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size = 5, gamma = 0.5)

# ===================================================================
# ⭐ 6. ĐỌC FILE IDS TỪ BƯỚC DVC TRƯỚC
# ===================================================================
print(f"Đang tải train_ids từ: {TRAIN_IDS_PATH}")
with open(TRAIN_IDS_PATH, 'r') as f:
    train_ids = json.load(f)

print(f"Đang tải valid_ids từ: {VALID_IDS_PATH}")
with open(VALID_IDS_PATH, 'r') as f:
    valid_ids = json.load(f)

print(f"Đã tải {len(train_ids)} train IDs và {len(valid_ids)} valid IDs.")

# ===================================================================
# TẠO DATASET VÀ DATALOADER
# ===================================================================
train_dataset = Img_Segmentation_Dataset(DATASET_ROOT, ANNOTATION_FILE, transforms=train_transform(), image_ids=train_ids)
valid_dataset = Img_Segmentation_Dataset(DATASET_ROOT, ANNOTATION_FILE, transforms=valid_transform(), image_ids=valid_ids)

# DataLoader sử dụng BATCH_SIZE
train_data_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0,  pin_memory=False)
valid_data_loader = DataLoader(valid_dataset, batch_size=BATCH_SIZE, shuffle=False,  num_workers=0, pin_memory=False)

# ===================================================================
# CẤU HÌNH HPARAMS (Sửa lại batch_size cho nhất quán)
# ===================================================================
hparams = {
    "run_name": "DeepLab_ResNet50_lr_1e-4_weighted",
    "learning_rate": 1e-4,
    "batch_size": BATCH_SIZE, # ⭐ 7. Dùng biến BATCH_SIZE
    "num_epochs": NUM_EPOCHS,
    "model_arch": "DeepLabV3-ResNet50",
    "optimizer": "Adam",
    "loss_function": "CrossEntropyLoss_Weighted", # Tên này ngụ ý bạn nên dùng class weights
    "image_size": 256, 
    "lr_scheduler": "StepLR",
    "lr_step_size": 5,
    "lr_gamma": 0.5
}

# ===================================================================
# CHẠY TRAINING
# ===================================================================
if __name__ == "__main__":
    run(
        train_data_loader, 
        valid_data_loader, 
        model, 
        criterion, 
        optimizer, 
        lr_scheduler,
        device, 
        num_epochs=NUM_EPOCHS, 
        num_classes=NUM_CLASSES, 
        hparams=hparams
    )
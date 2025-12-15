from model import DualStreamTransformerFusion
from dataset import ShopliftDataset
from config import *
from data import download_roboflow_dataset

import torch, os
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import transforms
from torch.optim import AdamW
from tqdm import tqdm


class EMA:
    def __init__(self, model, decay=0.999):
        self.decay = decay
        # Only track float parameters (skip integer buffers like num_batches_tracked)
        self.shadow = {}
        for k, v in model.state_dict().items():
            if v.dtype in (torch.float32, torch.float16, torch.bfloat16):
                self.shadow[k] = v.clone().detach()
            else:
                # For non-float parameters, just store a reference
                self.shadow[k] = v

    @torch.no_grad()
    def update(self, model):
        for k, v in model.state_dict().items():
            if k in self.shadow:
                # Only update float parameters
                if self.shadow[k].dtype in (torch.float32, torch.float16, torch.bfloat16):
                    self.shadow[k].mul_(self.decay).add_(v, alpha=1 - self.decay)
                else:
                    # For non-float parameters, just copy the value
                    self.shadow[k] = v

    def apply_to(self, model):
        model.load_state_dict(self.shadow)


def train():
    # =====================================================
    # 1. DATASET
    # =====================================================
    # Check if local dataset exists first
    local_train_dir = "FYP-Shoplift-1/train/images"
    local_valid_dir = "FYP-Shoplift-1/valid/images"
    
    import os
    if os.path.exists(local_train_dir) and os.path.exists(local_valid_dir):
        print(f"Using local dataset: {local_train_dir}, {local_valid_dir}")
        train_dir, valid_dir = local_train_dir, local_valid_dir
    else:
        print("Local dataset not found, downloading from Roboflow...")
        train_dir, valid_dir = download_roboflow_dataset()

    transform = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(
            [0.485, 0.456, 0.406],
            [0.229, 0.224, 0.225],
        ),
    ])

    train_ds = ShopliftDataset(train_dir, transform)
    val_ds   = ShopliftDataset(valid_dir, transform)

    train_loader = DataLoader(
        train_ds,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=NUM_WORKERS,
        pin_memory=(DEVICE.type == "cuda"),
    )

    val_loader = DataLoader(
        val_ds,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS,
        pin_memory=(DEVICE.type == "cuda"),
    )

    # =====================================================
    # 2. MODEL / OPTIM / LOSS
    # =====================================================
    model = DualStreamTransformerFusion().to(DEVICE)

    optimizer = AdamW(model.parameters(), lr=LR, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=EPOCHS
    )

    criterion = nn.BCEWithLogitsLoss()

    scaler = torch.cuda.amp.GradScaler(enabled=(DEVICE.type == "cuda"))
    ema = EMA(model, decay=0.999)

    best_val_loss = float("inf")

    # =====================================================
    # 3. TRAINING LOOP
    # =====================================================
    for epoch in range(EPOCHS):
        print(f"\n===== Epoch {epoch+1}/{EPOCHS} =====")

        # -----------------------------
        # TRAIN
        # -----------------------------
        model.train()
        train_loss = 0.0

        for imgs, poses, labels in tqdm(train_loader, desc="Training"):
            imgs = imgs.to(DEVICE)
            poses = poses.to(DEVICE)
            labels = labels.to(DEVICE)

            optimizer.zero_grad()

            with torch.amp.autocast(device_type='cuda' if DEVICE.type == "cuda" else 'cpu', enabled=(DEVICE.type == "cuda")):
                logits = model(imgs, poses)
                loss = criterion(logits, labels)

            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            nn.utils.clip_grad_norm_(model.parameters(), 2.0)

            scaler.step(optimizer)
            scaler.update()

            ema.update(model)

            train_loss += loss.item()

        scheduler.step()
        avg_train_loss = train_loss / len(train_loader)

        # -----------------------------
        # VALIDATION
        # -----------------------------
        model.eval()
        val_loss = 0.0
        correct, total = 0, 0

        with torch.no_grad():
            for imgs, poses, labels in tqdm(val_loader, desc="Validation"):
                imgs = imgs.to(DEVICE)
                poses = poses.to(DEVICE)
                labels = labels.to(DEVICE)

                logits = model(imgs, poses)
                loss = criterion(logits, labels)
                val_loss += loss.item()

                preds = (torch.sigmoid(logits) > 0.5).float()
                correct += (preds == labels).sum().item()
                total += labels.size(0)

        avg_val_loss = val_loss / len(val_loader)
        val_acc = 100.0 * correct / total

        print(
            f"Train Loss: {avg_train_loss:.4f} | "
            f"Val Loss: {avg_val_loss:.4f} | "
            f"Val Acc: {val_acc:.2f}%"
        )

        # -----------------------------
        # CHECKPOINT
        # -----------------------------
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            os.makedirs("weights", exist_ok=True)
            torch.save(model.state_dict(), MODEL_WEIGHTS_PATH)
            print("✅ Saved new best model")

    # =====================================================
    # 4. APPLY EMA WEIGHTS (FINAL)
    # =====================================================
    ema.apply_to(model)
    torch.save(model.state_dict(), MODEL_WEIGHTS_PATH)
    print("✅ EMA weights applied and saved")


if __name__ == "__main__":
    train()

import os, glob, torch
from torch.utils.data import Dataset
from PIL import Image
from ultralytics import YOLO
from config import *

def list_images(folder):
    paths = []
    for ext in ("*.jpg", "*.png", "*.jpeg", "*.webp"):
        paths.extend(glob.glob(os.path.join(folder, ext)))
    return sorted(paths)

class ShopliftDataset(Dataset):
    def __init__(self, img_dir, transform):
        self.image_paths = list_images(img_dir)
        self.transform = transform
        # Force YOLO to use CPU to avoid torchvision NMS CUDA issues
        self.pose_model = YOLO(POSE_MODEL_WEIGHTS)
        self.SHOPLIFT_CLASS_ID = 1

    def __len__(self):
        return len(self.image_paths)

    def extract_pose(self, img_path):
        pose = torch.zeros(POSE_DIM, dtype=torch.float32)
        try:
            # Use CPU device for YOLO inference to avoid torchvision NMS CUDA issues
            r = self.pose_model(img_path, verbose=False, device='cpu')[0]
            if r.keypoints is not None and r.keypoints.data.shape[0] > 0:
                pose_data = r.keypoints.data[0].cpu().numpy().flatten()
                pose_len = min(len(pose_data), POSE_DIM)
                pose[:pose_len] = torch.tensor(pose_data[:pose_len], dtype=torch.float32)
        except:
            pass
        return pose

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        image = Image.open(img_path).convert("RGB")
        image = self.transform(image)

        pose = self.extract_pose(img_path)

        label = 0.0
        # Cross-platform path handling: replace images with labels directory
        img_dir = os.path.dirname(img_path)
        img_filename = os.path.basename(img_path)
        
        # Try to find labels directory
        labels_dir = None
        # Method 1: Same level as images directory
        if "images" in img_dir:
            labels_dir = img_dir.replace("images", "labels")
        # Method 2: Parent directory contains labels folder
        if labels_dir is None or not os.path.exists(labels_dir):
            parent_dir = os.path.dirname(img_dir)
            labels_dir = os.path.join(parent_dir, "labels")
        
        label_path = os.path.join(labels_dir, img_filename.rsplit(".", 1)[0] + ".txt")
        if os.path.exists(label_path):
            with open(label_path) as f:
                for line in f:
                    if int(line.split()[0]) == self.SHOPLIFT_CLASS_ID:
                        label = 1.0
                        break

        return image, pose, torch.tensor([label])

import torch
import os
import cv2
import numpy as np
from PIL import Image
from torchvision import transforms
from ultralytics import YOLO

from model import DualStreamTransformerFusion
from config import *

# Lazy-loaded models
_pose_model = None
_model = None
_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
])

def _load_models():
    """Lazy load models on first use"""
    global _pose_model, _model
    
    if _pose_model is None:
        if not os.path.exists(POSE_MODEL_WEIGHTS):
            raise FileNotFoundError(f"Pose model weights not found: {POSE_MODEL_WEIGHTS}")
        # Force YOLO to use CPU to avoid torchvision NMS CUDA issues
        _pose_model = YOLO(POSE_MODEL_WEIGHTS)
    
    if _model is None:
        if not os.path.exists(MODEL_WEIGHTS_PATH):
            raise FileNotFoundError(f"Model weights not found: {MODEL_WEIGHTS_PATH}. Please train the model first.")
        _model = DualStreamTransformerFusion().to(DEVICE)
        _model.load_state_dict(torch.load(MODEL_WEIGHTS_PATH, map_location=DEVICE))
        _model.eval()
    
    return _pose_model, _model

def predict_image(image: Image.Image) -> float:
    """Predict shoplifting probability for an image"""
    pose_model, model = _load_models()
    
    img_tensor = _transform(image).unsqueeze(0).to(DEVICE)

    pose = torch.zeros(POSE_DIM)
    # Use CPU device for YOLO inference to avoid torchvision NMS CUDA issues
    r = pose_model(image, verbose=False, device='cpu')[0]
    if r.keypoints is not None and r.keypoints.data.shape[0] > 0:
        pose_data = r.keypoints.data[0].cpu().numpy().flatten()
        pose_len = min(len(pose_data), POSE_DIM)
        pose[:pose_len] = torch.tensor(pose_data[:pose_len], dtype=torch.float32)

    pose = pose.unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        prob = torch.sigmoid(model(img_tensor, pose)).item()

    return prob

# Define skeleton connectivity for drawing
SKELETON = [
    (0,1), (1,3), (0,2), (2,4),
    (5,7), (7,9), (6,8), (8,10),
    (5,6), (5,11), (6,12),
    (11,13), (13,15),
    (12,14), (14,16)
]

def draw_pose(image, keypoints):
    """Draws keypoints and skeleton lines on the image."""
    for (x, y, conf) in keypoints:
        if conf > 0.2:
            cv2.circle(image, (int(x), int(y)), 3, (0,255,0), -1)

    for a, b in SKELETON:
        # Check boundary to avoid index errors
        if a < len(keypoints) and b < len(keypoints):
            x1, y1, c1 = keypoints[a]
            x2, y2, c2 = keypoints[b]
            if c1 > 0.2 and c2 > 0.2:
                cv2.line(image, (int(x1),int(y1)), (int(x2),int(y2)), (0,255,255), 2)
    return image

def visualize_image(image: Image.Image, threshold: float = 0.5) -> Image.Image:
    """
    Visualize image with pose keypoints, skeleton, bounding boxes, and prediction.
    Returns a PIL Image with the visualization overlay.
    """
    pose_model, model = _load_models()
    
    # Convert PIL to OpenCV format
    img_array = np.array(image.convert('RGB'))
    img_rgb = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    img_rgb_copy = img_rgb.copy()
    
    # Run pose detection
    r = pose_model(image, verbose=False, device='cpu')[0]
    
    # Draw bounding boxes and get box coordinates for text placement
    box_coords = None
    if r.boxes is not None and len(r.boxes) > 0:
        box = r.boxes.xyxy[0].cpu().numpy()
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(img_rgb_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)
        box_coords = (x1, y1, x2, y2)
    
    # Extract and draw keypoints
    pose = torch.zeros(POSE_DIM)
    if r.keypoints is not None and hasattr(r.keypoints, 'data'):
        if r.keypoints.data.shape[0] > 0:
            kp = r.keypoints.data[0].cpu().numpy()
            img_rgb_copy = draw_pose(img_rgb_copy, kp)
            pose_data = kp.flatten()
            pose_len = min(len(pose_data), POSE_DIM)
            pose[:pose_len] = torch.tensor(pose_data[:pose_len], dtype=torch.float32)
    
    # Make prediction
    img_tensor = _transform(image).unsqueeze(0).to(DEVICE)
    pose_tensor = pose.unsqueeze(0).to(DEVICE)
    
    with torch.no_grad():
        prob = torch.sigmoid(model(img_tensor, pose_tensor)).item()
    
    pred = 1 if prob > threshold else 0
    pred_text = "Shoplifting" if pred == 1 else "Normal"
    
    # Add prediction text overlay - position it above the bounding box
    text = f"{pred_text} ({prob:.3f})"
    text_color = (0, 0, 255) if pred == 1 else (0, 255, 0)  # Red for shoplifting, Green for normal
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    thickness = 2
    
    # Get text size
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    
    # Position text above bounding box, or at top-left if no box detected
    if box_coords:
        x1, y1, x2, y2 = box_coords
        # Position text above the bounding box
        text_x = x1
        text_y = max(y1 - 10, text_height + 10)  # Above box, but at least 10px from top
        
        # Draw background rectangle for text
        cv2.rectangle(img_rgb_copy, 
                     (text_x - 5, text_y - text_height - 5), 
                     (text_x + text_width + 5, text_y + baseline + 5), 
                     (0, 0, 0), -1)  # Black background
        
        # Draw text
        cv2.putText(img_rgb_copy, text, (text_x, text_y), font, font_scale, text_color, thickness, cv2.LINE_AA)
    else:
        # Fallback: place at top-left if no bounding box
        cv2.putText(img_rgb_copy, text, (10, 30), font, font_scale, text_color, thickness, cv2.LINE_AA)
    
    # Convert back to RGB and PIL Image
    img_rgb_result = cv2.cvtColor(img_rgb_copy, cv2.COLOR_BGR2RGB)
    return Image.fromarray(img_rgb_result)

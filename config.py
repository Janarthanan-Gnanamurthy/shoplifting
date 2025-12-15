import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

IMG_SIZE = 224
POSE_DIM = 51
D_MODEL = 512

TRANSFORMER_LAYERS = 2
TRANSFORMER_HEADS = 8
TRANSFORMER_FF_DIM = 1024
DROPOUT = 0.3

BATCH_SIZE = 8
LR = 1e-4
EPOCHS = 20
NUM_WORKERS = 0

POSE_MODEL_WEIGHTS = "yolov8n-pose.pt"
MODEL_WEIGHTS_PATH = "weights/dual_stream_transformer_fusion.pth"

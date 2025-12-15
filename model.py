import torch
import torch.nn as nn
from torchvision import models
from config import *

class DualStreamTransformerFusion(nn.Module):
    def __init__(self):
        super().__init__()

        resnet = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        self.image_backbone = nn.Sequential(*list(resnet.children())[:-1])
        self.image_feat_dim = resnet.fc.in_features

        self.image_proj = nn.Sequential(
            nn.Linear(self.image_feat_dim, D_MODEL),
            nn.LayerNorm(D_MODEL),
            nn.ReLU(),
            nn.Dropout(DROPOUT),
        )

        self.pose_mlp = nn.Sequential(
            nn.Linear(POSE_DIM, D_MODEL),
            nn.LayerNorm(D_MODEL),
            nn.ReLU(),
            nn.Dropout(DROPOUT),
        )

        self.token_pos_embed = nn.Embedding(2, D_MODEL)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=D_MODEL,
            nhead=TRANSFORMER_HEADS,
            dim_feedforward=TRANSFORMER_FF_DIM,
            dropout=DROPOUT,
            batch_first=True,
            activation="gelu",
        )
        self.transformer = nn.TransformerEncoder(
            encoder_layer, num_layers=TRANSFORMER_LAYERS
        )

        self.gate = nn.Sequential(
            nn.Linear(D_MODEL * 2, D_MODEL),
            nn.LayerNorm(D_MODEL),
            nn.Sigmoid(),
        )

        self.cls_head = nn.Sequential(
            nn.LayerNorm(D_MODEL),
            nn.Dropout(DROPOUT),
            nn.Linear(D_MODEL, D_MODEL // 2),
            nn.GELU(),
            nn.Dropout(DROPOUT),
            nn.utils.weight_norm(nn.Linear(D_MODEL // 2, 1)),
        )

        nn.init.normal_(self.cls_head[-1].weight_g, std=0.05)

    def forward(self, images, poses):
        B = images.size(0)

        img_feat = self.image_backbone(images).view(B, -1)
        img_tok = self.image_proj(img_feat)

        pose_tok = self.pose_mlp(poses)

        seq = torch.stack([img_tok, pose_tok], dim=1)
        pos = torch.arange(0, 2, device=seq.device).unsqueeze(0)
        seq = seq + self.token_pos_embed(pos)

        fused = self.transformer(seq)

        t_img, t_pose = fused[:, 0], fused[:, 1]
        g = self.gate(torch.cat([t_img, t_pose], dim=-1))
        pooled = g * t_img + (1 - g) * t_pose

        return self.cls_head(pooled)

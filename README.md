## Shoplifting Detector

This project is a **shoplifting detection system** built around a dual‑stream transformer model and YOLOv8 pose estimation. It exposes a **FastAPI** backend that accepts images, predicts the probability of shoplifting behaviour, and can return a visualized image with pose keypoints and prediction overlays.

### Features
- **REST API** using `FastAPI` (`app.py`)
- **Prediction endpoint** `/predict` returning:
  - `shoplifting_probability` (0–1)
  - `prediction` (`"Shoplifting"` or `"Normal"`)
- **Visualization endpoint** `/visualize` returning:
  - JPEG image with keypoints, skeleton, bounding boxes and prediction overlay
- **Training utilities** (`train.py`, `dataset.py`, `data.py`, `config.py`) for the custom model
- Pretrained weights:
  - `weights/dual_stream_transformer_fusion.pth`
  - `yolov8n-pose.pt`

---

### 1. Environment setup

1. **Clone / copy** this repository to your machine.
2. Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

3. Install dependencies (example – adjust to your actual `requirements.txt` if present):

```bash
pip install fastapi uvicorn pillow torch torchvision ultralytics
```

You may also need extra packages depending on your local setup (e.g. `opencv-python`, `numpy`, etc.) that are imported in `inference.py`, `train.py`, or `model.py`.

---

### 2. Project structure

```text
app.py                     # FastAPI application (API endpoints)
inference.py               # Model loading and image inference utilities
model.py                   # Dual-stream transformer / fusion model definition
train.py                   # Training script
dataset.py, data.py        # Dataset and data loading utilities
config.py                  # Configuration (paths, hyperparameters, etc.)
weights/
  dual_stream_transformer_fusion.pth  # Trained model weights
yolov8n-pose.pt            # YOLOv8 pose model weights
FYP-Shoplift-1/            # Dataset (train/valid/test) and data.yaml
```

---

### 3. Running the API

From the project root:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Then open your browser at:
- **Root**: `http://localhost:8000/`
- **Docs (Swagger UI)**: `http://localhost:8000/docs`

You should see basic info about the API and be able to test endpoints from the docs.

---

### 4. Endpoints

- **GET `/`**
  - Health/info: returns a simple JSON with API name and status.

- **GET `/health`**
  - Tries to load the models (via `_load_models` in `inference.py`) and returns:
    - `status`: `"healthy" | "unhealthy" | "error"`
    - `models_loaded`: `true | false`
    - `error` (optional): description if something went wrong (e.g. missing weights).

- **POST `/predict`**
  - **Body**: form‑data with a single field:
    - `file`: image file (any common image type).
  - **Response JSON**:
    - `shoplifting_probability`: float in \[0, 1\]
    - `prediction`: `"Shoplifting"` if probability > 0.5 else `"Normal"`.

- **POST `/visualize`**
  - **Query / form parameters**:
    - `file`: image file
    - `threshold` (optional, float, default `0.5`): decision boundary for label.
  - **Response**:
    - JPEG image with visualization (pose keypoints / bounding boxes / overlayed prediction).

---

### 5. Model weights

- Place the trained fusion weights at:
  - `weights/dual_stream_transformer_fusion.pth`
- Ensure the YOLOv8 pose weights are present:
  - `yolov8n-pose.pt` in the project root
- If paths differ in your local environment, update them in `config.py` and/or `inference.py`.

---

### 6. Training (optional)

If you want to retrain or fine‑tune the model:

1. Ensure the dataset under `FYP-Shoplift-1/` matches the paths expected by `data.yaml` and your training script.
2. Review and adjust training hyperparameters in `config.py` or `train.py`.
3. Run (example):

```bash
python train.py
```

After training, replace `weights/dual_stream_transformer_fusion.pth` with the new checkpoint or adjust the path in `inference.py`.

---

### 7. Notes & troubleshooting

- If `/health` or prediction endpoints complain about missing weights, confirm:
  - The files exist at the paths mentioned above.
  - File names and extensions are correct.
- If you encounter CUDA or GPU issues, either:
  - Install the correct CUDA‑enabled PyTorch build, **or**
  - Force CPU inference in `inference.py` (e.g. set `device="cpu"`).
- Check `http://localhost:8000/docs` to quickly debug request/response formats.



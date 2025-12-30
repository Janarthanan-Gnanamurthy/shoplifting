from fastapi import FastAPI, UploadFile, File, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import tempfile
import shutil
import os
import cv2

from inference import predict_image, visualize_image

app = FastAPI(title="Shoplifting Detection API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Shoplifting Detection API", "status": "running"}

@app.get("/health")
async def health():
    """Health check endpoint to verify models are available"""
    try:
        from inference import _load_models
        _load_models()
        return {"status": "healthy", "models_loaded": True}
    except FileNotFoundError as e:
        return {"status": "unhealthy", "models_loaded": False, "error": str(e)}
    except Exception as e:
        return {"status": "error", "models_loaded": False, "error": str(e)}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and process image
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # Make prediction
        prob = predict_image(image)

        return {
            "shoplifting_probability": round(prob, 4),
            "prediction": "Shoplifting" if prob > 0.5 else "Normal"
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Model not available: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/visualize")
async def visualize(file: UploadFile = File(...), threshold: float = 0.5):
    """
    Visualize image with pose keypoints, skeleton, bounding boxes, and prediction overlay.
    Returns the visualized image as JPEG.
    
    Parameters:
    - file: Image file to visualize
    - threshold: Prediction threshold (default: 0.5)
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and process image
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # Generate visualization
        visualized_image = visualize_image(image, threshold=threshold)
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        visualized_image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        return Response(content=img_byte_arr.read(), media_type="image/jpeg")
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Model not available: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@app.post("/analyze_video")
async def analyze_video(
    file: UploadFile = File(...), 
    frame_skip: int = 5,
    confidence_threshold: float = 0.7
):
    """
    Analyzes a video file and returns timestamps of suspicious activity.
    
    Parameters:
    - frame_skip: Process every Nth frame to speed up inference (default: 5)
    - confidence_threshold: Probability required to flag a frame (default: 0.7)
    """
    
    # 1. Validate File
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")

    # 2. Save Uploaded File to Temp (OpenCV requires a file path)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_video:
        shutil.copyfileobj(file.file, tmp_video)
        temp_video_path = tmp_video.name

    try:
        cap = cv2.VideoCapture(temp_video_path)
        if not cap.isOpened():
            raise HTTPException(status_code=500, detail="Could not open video file")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        detections = []
        is_shoplifting_detected = False
        max_prob = 0.0

        current_frame = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Optimization: Skip frames to speed up processing
            if current_frame % frame_skip != 0:
                current_frame += 1
                continue

            # Convert BGR (OpenCV) to RGB (PIL)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)

            # Run Inference
            try:
                prob = predict_image(pil_image)
            except Exception:
                prob = 0.0 # Handle inference errors gracefully

            # Update Max Probability found in video
            if prob > max_prob:
                max_prob = prob

            # Flag Detection
            if prob > confidence_threshold:
                is_shoplifting_detected = True
                timestamp = round(current_frame / fps, 2)
                
                detections.append({
                    "timestamp": timestamp,
                    "frame_index": current_frame,
                    "probability": round(prob, 4)
                })

            current_frame += 1

        cap.release()

        # 3. Post-processing: Group timestamps into "events"
        # If we have timestamps [1.0, 1.2, 1.4, 5.0, 5.2], group them into events.
        events = []
        if detections:
            start_time = detections[0]['timestamp']
            last_time = detections[0]['timestamp']
            
            for i in range(1, len(detections)):
                curr_time = detections[i]['timestamp']
                # If current detection is more than 1 second away from last, consider it a new event
                if curr_time - last_time > 1.5:
                    events.append({"start": start_time, "end": last_time})
                    start_time = curr_time
                last_time = curr_time
            
            # Append the final event
            events.append({"start": start_time, "end": last_time})

        return {
            "filename": file.filename,
            "duration_seconds": round(total_frames / fps, 2),
            "fps": fps,
            "overall_prediction": "Shoplifting Detected" if is_shoplifting_detected else "Normal",
            "max_confidence": round(max_prob, 4),
            "timeline_events": events, # Simplified start/end times
            "raw_detections_count": len(detections) # How many frames were flagged
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video processing failed: {str(e)}")
    finally:
        # Cleanup temp file
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
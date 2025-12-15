from fastapi import FastAPI, UploadFile, File, HTTPException, Response
from PIL import Image
import io

from inference import predict_image, visualize_image

app = FastAPI(title="Shoplifting Detection API")

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

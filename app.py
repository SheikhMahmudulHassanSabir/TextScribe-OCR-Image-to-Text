from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import time
import shutil
import base64
from typing import List
import cv2
import numpy as np

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "pipeline"))
from pipeline import OCRPipeline, detect_text_type

app = FastAPI(title="TextScribe OCR API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize Pipeline
ocr_pipeline = OCRPipeline()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

html_dir = os.path.join(os.path.dirname(__file__), "html")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    with open(os.path.join(html_dir, "index.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/{filename}.html")
def read_html(filename: str):
    file_path = os.path.join(html_dir, f"{filename}.html")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="Not Found", status_code=404)


# --- API v1 ---

start_time_global = time.time()

@app.get("/api/v1/health")
def check_health():
    return JSONResponse({
        "status": "healthy",
        "model_loaded": True,
        "gpu_available": False, 
        "uptime_seconds": time.time() - start_time_global
    })

@app.get("/api/v1/ocr/config")
def get_config():
    return JSONResponse({
        "max_size_mb": 10,
        "allowed_formats": ["image/jpeg", "image/png", "image/bmp", "image/tiff"]
    })

def process_file_logic(file_path: str, lang="en", use_angle_cls=True):
    start_time = time.time()
    try:
        # Load image for type detection
        img = cv2.imread(file_path)
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
            
        # Detect text type
        text_type = detect_text_type(img)
        print(f"[INFO] Processing {file_path} as {text_type}")
        
        # Run pipeline
        results = ocr_pipeline(img, text_type)
        
        formatted_results = []
        texts = []
        for i, item in enumerate(results):
            text = item.get('text', '')
            confidence = item.get('confidence', 0.0)
            texts.append(text)
            
            formatted_results.append({
                "line_number": i + 1,
                "text": text,
                "confidence": round(float(confidence), 4),
                "bounding_box": item.get('box', [0,0,0,0])
            })
            
        full_text = "\n".join(texts) if texts else ""
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            "success": True,
            "full_text": full_text,
            "processing_time_ms": processing_time,
            "total_detections": len(results),
            "results": formatted_results,
            "diagnostics": {
                "classification": text_type,
                "image_shape": list(img.shape),
                "lines_detected": len(results)
            }
        }
    except Exception as e:
        print(f"[ERROR] process_file_logic failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ocr/recognize")
async def recognize_text(
    file: UploadFile = File(...),
):
    if not file.filename:
        return JSONResponse({"success": False, "message": "No file uploaded"}, status_code=400)
    
    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:
        return JSONResponse({"success": False, "message": "File exceeds 10MB limit. Please use a smaller image."}, status_code=413)
        
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file_bytes)
            
        data = process_file_logic(file_path)
        return JSONResponse(data)
    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

class Base64Request(BaseModel):
    image_base64: str
    lang: str = "en"
    use_angle_cls: bool = True
    morph_op: str = "dilate"
    decoder: str = "greedy"

@app.post("/api/v1/ocr/recognize-base64")
async def recognize_base64(req: Base64Request):
    file_path = os.path.join(UPLOAD_DIR, f"temp_{int(time.time())}.jpg")
    try:
        img_data = base64.b64decode(req.image_base64.split(",")[-1])
        with open(file_path, "wb") as f:
            f.write(img_data)
            
        data = process_file_logic(file_path, req.lang, req.use_angle_cls)
        return JSONResponse(data)
    except Exception as e:
        return JSONResponse({"success": False, "message": "Invalid base64 string or processing error", "error": str(e)}, status_code=400)
    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

@app.post("/api/v1/ocr/batch")
async def recognize_batch(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        if not file.filename:
            continue
            
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        try:
            file_bytes = await file.read()
            with open(file_path, "wb") as buffer:
                buffer.write(file_bytes)
                
            data = process_file_logic(file_path)
            data["filename"] = file.filename
            results.append(data)
        finally:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
    return JSONResponse({"success": True, "batch_results": results})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)

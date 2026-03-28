"""
Main OCR Pipeline Orchestrator.
Supports dual-routing between custom CRNN for handwriting and PaddleOCR for digital text.
"""

import os
# PaddleOCR Environment Setup (Performance & Stability optimizations for Python 3.11 Windows)
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["DISABLE_MODEL_SOURCE_CHECK"] = "True"
os.environ["ENABLE_ONEDNN"] = "0" 
os.environ["FLAGS_enable_pir_api"] = "0" # Disable PIR to avoid unimplemented PirAttribute error

import cv2  # type: ignore
import numpy as np  # type: ignore
import logging
from typing import Union, List, Any
from PIL import Image  # type: ignore

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Import configuration
try:
    from .config import config  # type: ignore
except ImportError:
    config = {}

from .preprocessing import (  # type: ignore
    resize_image, to_grayscale, denoise_image, apply_clahe, 
    adaptive_threshold, deskew_image
)

from paddleocr import PaddleOCR  # type: ignore
import paddle  # type: ignore

# Custom CRNN Imports (Local handwriting model)
try:
    from .model.crnn import CRNN  # type: ignore
    from .ctc.ctc_decoder import CTCDecoder  # type: ignore
    from .utils.charset import get_default_charset  # type: ignore
    CUSTOM_MODEL_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Custom handwriting model components missing or misconfigured: {e}")
    CUSTOM_MODEL_AVAILABLE = False


def detect_text_type(img: np.ndarray) -> str:
    """
    Detects whether the text in an image is handwritten or digital (printed).
    Analyzes stroke variation, edge uniformity, and texture patterns.
    """
    try:
        if img is None:
            return "Unknown"
        
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        # Resize for consistent analysis if image is too large
        max_size = 800
        h, w = gray.shape
        if max(h, w) > max_size:
            scale = max_size / max(h, w)
            gray = cv2.resize(gray, (int(w * scale), int(h * scale)))
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply Otsu's thresholding for cleaner binary image
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # 1. Stroke width variation analysis using erosion
        kernel = np.ones((2, 2), np.uint8)
        eroded = cv2.erode(binary, kernel, iterations=1)
        stroke_diff = cv2.subtract(binary, eroded)
        
        stroke_pixels = stroke_diff[stroke_diff > 0]
        if len(stroke_pixels) > 10:
            stroke_mean = np.mean(stroke_pixels)
            stroke_std = np.std(stroke_pixels)
            stroke_cv = stroke_std / (stroke_mean + 1e-6)
        else:
            stroke_cv = 0
        
        # 2. Edge analysis using Sobel operators
        sobelx = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
        sobel_mag = np.sqrt(sobelx**2 + sobely**2)
        edge_std = np.std(sobel_mag)
        
        # 3. Connected component analysis
        score = 0
        try:
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, connectivity=8)
            if num_labels > 5:
                areas = stats[1:, cv2.CC_STAT_AREA]
                widths = stats[1:, cv2.CC_STAT_WIDTH]
                heights = stats[1:, cv2.CC_STAT_HEIGHT]
                
                area_std = np.std(areas)
                aspect_ratios = heights / (widths + 1e-6)
                aspect_std = np.std(aspect_ratios)
                
                # Digital text characteristics: uniform stroke, consistent aspect ratios
                if aspect_std < 0.4: score -= 1
                elif aspect_std > 0.8: score += 1
                
                if area_std < 100: score -= 1
                elif area_std > 500: score += 1
            else:
                score += 0 # Too few components to be sure
        except:
            pass
        
        # Decision logic enhancement
        if stroke_cv < 0.35: score -= 2
        elif stroke_cv > 0.55: score += 2
        
        if edge_std < 40: score -= 1
        elif edge_std > 90: score += 1
        
        if score <= -2:
            return "Digital"
        elif score >= 2:
            return "Handwritten"
        else:
            return "Mixed"
            
    except Exception as e:
        logger.warning(f"Text type detection failed: {e}")
        return "Unknown"


class HandwritingPipeline:
    """
    Custom CRNN pipeline for handwritten text.
    Handles legacy model preserving constraints.
    """
    def __init__(self, cfg: dict):
        self.cfg = cfg
        if not CUSTOM_MODEL_AVAILABLE:
            raise RuntimeError("CRNN model files not found in pipeline directory.")
            
        self.charset = get_default_charset()
        self.num_classes = len(self.charset) + 1  # +1 for CTC blank index
        
        try:
            self.model = CRNN(num_classes=self.num_classes, hidden_size=256)
            self.decoder = CTCDecoder(charset=self.charset, blank_index=0)
            
            # Safely attempt to load weights
            weights_path = os.path.join(os.path.dirname(__file__), "weights", "best_model.pdparams")
            if os.path.exists(weights_path):
                state_dict = paddle.load(weights_path)
                self.model.set_state_dict(state_dict)
                logger.info(f"Loaded custom CRNN weights from {weights_path}")
            else:
                logger.warning(f"No weights found at {weights_path}. Model will run uninitialized.")
                self.weights_missing = True
                
            self.model.eval()
        except Exception as e:
            logger.error(f"Failed to initialize HandwritingPipeline: {e}")
            raise RuntimeError(f"Handwriting init error: {str(e)}")
            
    def preprocess(self, img: np.ndarray) -> paddle.Tensor:
        """
        Deep preprocessing focused on handwriting contrast and noise reduction.
        """
        if len(img.shape) == 3:
            img = to_grayscale(img)
            
        # Deskew image if configured
        if self.cfg.get("deskew", {}).get("enabled", True):
            img = deskew_image(img, min_angle=self.cfg.get("deskew", {}).get("min_angle", -5))
            
        # Denoising and Contrast
        img = denoise_image(img, h=self.cfg.get("denoise", {}).get("h", 10))
        img = apply_clahe(img, clip_limit=2.5)
        img = adaptive_threshold(img, block_size=11, C=2)
        
        # Resize constraint (CRNN requires height=32 inference)
        h, w = img.shape[:2]
        target_h = 32
        scale = target_h / max(h, 1)
        new_w = int(w * scale)
        img = cv2.resize(img, (max(new_w, 32), target_h))

        # Format explicitly for [Batch, Channel, Height, Width] Paddle tensor
        img_norm = img.astype(np.float32) / 255.0
        img_norm = np.expand_dims(img_norm, axis=(0, 1))
        return paddle.to_tensor(img_norm)

    def __call__(self, img: np.ndarray) -> dict:
        """Process a single line image."""
        try:
            tensor = self.preprocess(img)
            with paddle.no_grad():
                preds = self.model(tensor)
            
            # Sequence CTC Decoding
            pred_np = preds.numpy()
            decoded_texts = self.decoder.greedy_decode(pred_np)
            
            text = decoded_texts[0] if decoded_texts else ""
            
            if getattr(self, "weights_missing", False) and not text:
                text = "[Handwriting model weights missing]"
                
            return {"text": text, "confidence": 0.85 if text else 0.0}
            
        except Exception as e:
            logger.error(f"Handwriting inference sequence failed: {e}")
            return {"text": "", "confidence": 0.0}


class PaddleOCRPipeline:
    """
    PaddleOCR instance delegated strictly for digital/printed text.
    """
    def __init__(self):
        try:
            # lang='en' is enough for most cases
            self.ocr = PaddleOCR(lang='en')
            logger.info("PaddleOCR Engine initialized.")
        except Exception as e:
            logger.error(f"PaddleOCR Engine failed to initialize: {e}")
            raise
        
    def preprocess(self, img: np.ndarray) -> np.ndarray:
        # Add padding to improve detection near edges
        padded = cv2.copyMakeBorder(img, 30, 30, 30, 30, cv2.BORDER_CONSTANT, value=[255, 255, 255])
        
        # Downscale if extremely large for faster/stable detection
        h, w = padded.shape[:2]
        if max(h, w) > 2000:
            scale = 2000 / max(h, w)
            padded = cv2.resize(padded, (int(w * scale), int(h * scale)))
            
        return padded
        
    def __call__(self, img: np.ndarray, rec: bool = True) -> List[dict]:
        """
        If rec=True, returns full OCR results.
        If rec=False, returns detection boxes only.
        """
        try:
            img_processed = self.preprocess(img)
            # In some PaddleOCR versions (like PaddleX 3.0), ocr() takes different arguments.
            # We try standard first, then fallback to no kwargs if it fails.
            try:
                result = self.ocr.ocr(img_processed, rec=rec, cls=True)
            except TypeError:
                logger.info("Standard PaddleOCR args failed, trying without kwargs.")
                result = self.ocr.ocr(img_processed)
            
            formatted_results = []
            if not result or result[0] is None:
                return []

            for item in result[0]:
                line: Any = item
                if rec:
                    # line format: [ [box], (text, score) ]
                    if len(line) >= 2 and len(line[1]) >= 2:
                        formatted_results.append({
                            "text": line[1][0],
                            "confidence": float(line[1][1]),
                            "box": line[0]
                        })
                else:
                    # line format: [box]
                    formatted_results.append({
                        "box": line
                    })
            
            return formatted_results
        except Exception as e:
            logger.error(f"PaddleOCR Error: {e}")
            return []


class OCRPipeline:
    """
    Primary Orchestrator.
    Routes to PaddleOCR for digital text.
    Routes to PaddleOCR (detection) + CRNN (recognition) for handwriting.
    """
    def __init__(self, cfg: dict = config):
        self.cfg = cfg
        logger.info("Initializing OCR Pipeline...")
        
        self.digital_pipeline = PaddleOCRPipeline()
        
        try:
            self.handwriting_pipeline = HandwritingPipeline(cfg)
        except Exception as e:
            logger.warning(f"Handwriting model failed to initialize: {e}. Falling back to PaddleOCR.")
            self.handwriting_pipeline = None  # type: ignore
            
    def _load_image(self, image_input: Union[str, np.ndarray, Image.Image]) -> np.ndarray:
        if isinstance(image_input, str):
            img = cv2.imread(image_input)
            if img is None:
                raise ValueError(f"Could not read image: {image_input}")
            return img
        elif isinstance(image_input, np.ndarray):
            return image_input
        elif isinstance(image_input, Image.Image):
            return cv2.cvtColor(np.array(image_input), cv2.COLOR_RGB2BGR)
        raise TypeError("Unsupported image input type.")
        
    def __call__(self, image_input: Union[str, np.ndarray, Image.Image], text_type: str = "Unknown") -> List[dict]:
        try:
            img = self._load_image(image_input)
            
            # If type is unknown, detect it
            if text_type == "Unknown":
                text_type = detect_text_type(img)
                logger.info(f"Auto-detected text type: {text_type}")

            if text_type == "Handwritten" and self.handwriting_pipeline:
                logger.info("Routing to Handwriting Pipeline (Hybrid Mode)")
                # 1. Detect text lines using PaddleOCR (robust detector)
                detections = self.digital_pipeline(img, rec=False)
                
                if not detections:
                    # Fallback: if no lines detected, try processing the whole image as one line
                    logger.warning("No lines detected by PaddleOCR. Attempting whole-image inference.")
                    res = self.handwriting_pipeline(img)
                    return [res] if res['text'] else []

                # 2. Sort detections top-to-bottom
                detections.sort(key=lambda x: np.mean(np.array(x['box'])[:, 1]))
                
                results = []
                for det in detections:
                    box = np.array(det['box']).astype(np.int32)
                    # Crop image (add small margin)
                    x_min, y_min = np.min(box, axis=0)
                    x_max, y_max = np.max(box, axis=0)
                    
                    # Expand box slightly for better recognition
                    h, w = img.shape[:2]
                    y_min = max(0, y_min - 2)
                    y_max = min(h, y_max + 2)
                    x_min = max(0, x_min - 2)
                    x_max = min(w, x_max + 2)
                    
                    crop = img[y_min:y_max, x_min:x_max]
                    if crop.size == 0: continue
                    
                    res = self.handwriting_pipeline(crop)
                    if res['text']:
                        results.append(res)
                
                return results
            else:
                # Digital or mixed, or handwriting model missing
                logger.info("Routing to Digital Pipeline (PaddleOCR)")
                return self.digital_pipeline(img)
                
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            import traceback
            traceback.print_exc()
            return [{"text": f"Error: {str(e)}", "confidence": 0.0}]


"""
CLAHE (Contrast Limited Adaptive Histogram Equalization) module.
"""

import cv2
import numpy as np
from typing import Tuple

def apply_clahe(img: np.ndarray, clip_limit: float = 2.0, tile_grid: Tuple[int, int] = (8, 8)) -> np.ndarray:
    """
    Applies CLAHE (Contrast Limited Adaptive Histogram Equalization) 
    to improve local contrast of the image.
    
    Args:
        img: Input image as numpy array (grayscale).
        clip_limit: Threshold for contrast limiting.
        tile_grid: Size of grid for histogram equalization (rows, cols).
        
    Returns:
        np.ndarray: Image after CLAHE application.
    """
    try:
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid)
        enhanced = clahe.apply(img)
        return enhanced
    except Exception as e:
        raise RuntimeError(f"Failed to apply CLAHE: {str(e)}")

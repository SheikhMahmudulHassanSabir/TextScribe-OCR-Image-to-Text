"""
Grayscale conversion module.
"""

import cv2
import numpy as np

def to_grayscale(img: np.ndarray) -> np.ndarray:
    """
    Converts an image to grayscale if it is not already.
    
    Args:
        img: Input image as numpy array.
        
    Returns:
        np.ndarray: Grayscale representation of the image.
    """
    try:
        if len(img.shape) == 3 and img.shape[2] == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        elif len(img.shape) == 3 and img.shape[2] == 4:
            return cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        return img
    except Exception as e:
        raise RuntimeError(f"Failed to convert image to grayscale: {str(e)}")

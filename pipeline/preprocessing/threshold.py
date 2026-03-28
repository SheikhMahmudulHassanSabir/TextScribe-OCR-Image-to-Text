"""
Adaptive thresholding module.
"""

import cv2
import numpy as np

def adaptive_threshold(img: np.ndarray, block_size: int = 11, C: int = 2) -> np.ndarray:
    """
    Applies Gaussian adaptive thresholding.
    
    Args:
        img: Input grayscale image as numpy array.
        block_size: Size of a pixel neighborhood that is used to calculate a threshold value 
                    for the pixel (must be odd).
        C: Constant subtracted from the mean or weighted mean.
        
    Returns:
        np.ndarray: Binarized image.
    """
    try:
        binary = cv2.adaptiveThreshold(
            img, 
            255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            block_size, 
            C
        )
        return binary
    except Exception as e:
        raise RuntimeError(f"Failed to apply adaptive thresholding: {str(e)}")

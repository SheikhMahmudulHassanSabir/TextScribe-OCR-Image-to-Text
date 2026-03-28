"""
Image resizing functionality maintaining aspect ratio.
"""

import cv2
import numpy as np

def resize_image(img: np.ndarray, target_height: int = 32, max_width: int = 1280) -> np.ndarray:
    """
    Resizes an image maintaining its aspect ratio to a specific height.
    Limits the maximum width if specified.
    
    Args:
        img: Input image as numpy array.
        target_height: Target height for the image. Default is 32.
        max_width: Maximum allowed width. Default is 1280.
        
    Returns:
        np.ndarray: Resized image.
    """
    try:
        h, w = img.shape[:2]
        
        # Calculate new width maintaining aspect ratio
        ratio = w / float(h)
        new_width = int(target_height * ratio)
        
        # Limit the width to max_width
        if new_width > max_width:
            new_width = max_width
            
        # Determine the interpolation method
        if new_width < w:
            interpolation = cv2.INTER_AREA
        else:
            interpolation = cv2.INTER_LINEAR
            
        resized = cv2.resize(img, (new_width, target_height), interpolation=interpolation)
        return resized
    except Exception as e:
        raise RuntimeError(f"Failed to resize image: {str(e)}")

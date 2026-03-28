"""
Noise reduction module using Non-Local Means Denoising.
"""

import cv2
import numpy as np

def denoise_image(img: np.ndarray, h: int = 10, template_window: int = 7, search_window: int = 21) -> np.ndarray:
    """
    Applies Fast Non-Local Means Denoising on grayscale variations.
    
    Args:
        img: Input grayscale image as numpy array.
        h: Parameter regulating filter strength. Big h value perfectly removes noise but also 
           removes image details, smaller h value preserves details but also preserves some noise.
        template_window: Size in pixels of the template patch that is used to compute weights. 
                         Should be odd.
        search_window: Size in pixels of the window that is used to compute weighted average for 
                       given pixel. Should be odd.
                       
    Returns:
        np.ndarray: Denoised image.
    """
    try:
        # Assuming the image is already grayscale as per pipeline order
        denoised = cv2.fastNlMeansDenoising(
            img, 
            None, 
            h=h, 
            templateWindowSize=template_window, 
            searchWindowSize=search_window
        )
        return denoised
    except Exception as e:
        raise RuntimeError(f"Failed to apply noise reduction: {str(e)}")

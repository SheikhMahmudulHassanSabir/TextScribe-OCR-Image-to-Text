"""
Morphological operations module.
"""

import cv2
import numpy as np
from typing import Tuple

def apply_morphology(img: np.ndarray, op: str = "dilate", kernel_size: Tuple[int, int] = (2, 2), iterations: int = 1) -> np.ndarray:
    """
    Applies selected morphological operation to process character strokes.
    
    Rule:
    - Use DILATION when characters are thin or broken.
    - Use EROSION when characters are thick or merging together.
    
    Args:
        img: Input binary image as numpy array.
        op: Operation type, either 'dilate' or 'erode'.
        kernel_size: Size of the structuring element.
        iterations: Number of times the operation is applied.
        
    Returns:
        np.ndarray: Transformed image.
    """
    try:
        kernel = np.ones(kernel_size, np.uint8)
        
        if op.lower() == "dilate":
            transformed = cv2.dilate(img, kernel, iterations=iterations)
        elif op.lower() == "erode":
            transformed = cv2.erode(img, kernel, iterations=iterations)
        else:
            raise ValueError(f"Unknown operation: {op}. Expected 'dilate' or 'erode'.")
            
        return transformed
    except Exception as e:
        raise RuntimeError(f"Failed to apply morphological operation: {str(e)}")

"""
Image deskewing module.
"""

import cv2
import numpy as np

def deskew_image(img: np.ndarray, min_angle: float = 0.5) -> np.ndarray:
    """
    Corrects image rotation if angle > ±0.5° (max ±45°).

    Args:
        img: Input image (binary or grayscale).
        min_angle: Minimum angle to trigger deskewing correction.

    Returns:
        np.ndarray: Deskewed image.
    """
    try:
        # Determine background behavior depending on image shape
        # Generally deskew is performed after some preprocessing, usually on grayscale
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()

        # Invert colors so text is white
        gray = cv2.bitwise_not(gray)

        # Thresholding
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # Use minAreaRect to find the angle
        coords = np.column_stack(np.where(thresh > 0))
        angle = cv2.minAreaRect(coords)[-1]
        
        # Adjust angle to be between -45 and 45
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        # check if it exceeds threshold
        if abs(angle) < min_angle:
            return img

        # check if max +- 45 is respected
        if abs(angle) > 45:
            return img

        # rotate the image to deskew it
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # check background color based on input (default to black if binary, white if doc)
        # Assuming typical white document background for OCR images
        bg_color = (255, 255, 255) if len(img.shape) == 3 else 255
            
        rotated = cv2.warpAffine(
            img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )
        return rotated

    except Exception as e:
        raise RuntimeError(f"Failed to deskew image: {str(e)}")

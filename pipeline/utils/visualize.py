"""
Visualization utilities for the pipeline.
"""

import cv2
import numpy as np

def show_image(title: str, img: np.ndarray):
    """
    Displays an image using OpenCV and waits for key press.
    """
    try:
        cv2.imshow(title, img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"Warning: Could not display image {title}: {str(e)}")

def save_image(filepath: str, img: np.ndarray):
    """
    Saves an image to the specified filepath.
    """
    try:
        cv2.imwrite(filepath, img)
    except Exception as e:
        print(f"Warning: Could not save image to {filepath}: {str(e)}")

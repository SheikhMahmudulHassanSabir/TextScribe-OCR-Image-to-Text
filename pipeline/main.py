"""
Main entry point for running the PaddleOCR pipeline.
"""

import sys
import os
import cv2
import numpy as np

# Add the parent directory to the path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pipeline import OCRPipeline

def create_sample_image(output_path: str = "sample_test.jpg"):
    """
    Creates a sample image with text for testing.
    """
    try:
        # Create a white blank image
        img = np.ones((100, 400, 3), dtype=np.uint8) * 255
        
        # Add some text
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, 'PaddleOCR', (50, 60), font, 1.5, (0, 0, 0), 2, cv2.LINE_AA)
        
        # Save image
        cv2.imwrite(output_path, img)
        print(f"Created sample image: {output_path}")
        return output_path
    except Exception as e:
        print(f"Failed to create sample image: {str(e)}")
        return None

def main():
    try:
        print("Initializing PaddleOCR Pipeline...")
        pipeline = OCRPipeline()
        
        # Test with a sample image
        sample_path = "sample_test.jpg"
        if not os.path.exists(sample_path):
            create_sample_image(sample_path)
            
        print(f"Running pipeline on {sample_path}...")
        results = pipeline(sample_path)
        
        print("\n--- OCR Results ---")
        for i, item in enumerate(results):
            text = item['text']
            confidence = item['confidence']
            print(f"Result {i+1}: {text} (confidence: {confidence:.4f})")
        print("-------------------")
            
    except Exception as e:
        print(f"Error during execution: {str(e)}")

if __name__ == "__main__":
    main()

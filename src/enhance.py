import cv2
import numpy as np

def enhance_scan(image):
    """
    Converts image to a clean black and white scan look.
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Adaptive thresholding to handle lighting variations
    # block_size: Size of a pixel neighborhood (must be odd). 
    # C: Constant subtracted from the mean.
    thresh = cv2.adaptiveThreshold(
        gray, 255, 
        cv2.THRESH_BINARY, 11, 2
    )

    return thresh

def enhance_magic_color(image):
    """
    Increases contrast and saturation for a 'Magic Color' look.
    """
    # Simple contrast enhancement (CLAHE)
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    
    limg = cv2.merge((cl, a, b))
    final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    
    return final

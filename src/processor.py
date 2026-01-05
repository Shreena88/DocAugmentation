import cv2
import numpy as np
import pytesseract
import os
from .utils import get_device_info

class DocumentProcessor:
    def __init__(self, mode='auto'):
        self.mode = mode
        self.device_info = get_device_info()
        print(f"Initialized DocumentProcessor on {self.device_info}")
        
        # Robust Tesseract Path Check
        # 1. Check common Windows install location
        # 2. Check User local install
        # 3. Fallback to PATH (default behavior of pytesseract if not set)
        
        paths_to_check = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe")
        ]
        
        found_tess = False
        for path in paths_to_check:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                print(f"DEBUG: Found Tesseract at {path}")
                found_tess = True
                break
        
        if not found_tess:
            print("DEBUG: Tesseract not found in common paths. Relying on System PATH.")

    def correct_orientation(self, image):
        """
        Detects text orientation using Tesseract OSD and rotates the image.
        Returns: Rotated Image, Boolean (True if rotated)
        """
        try:
            # Get OSD (Orientation Script Detection)
            # Output dict: {'PageNum': 0, 'Orientation': 0, 'Rotate': 0, ...}
            # Rotate: Amount of rotation needed (0, 90, 180, 270)
            results = pytesseract.image_to_osd(image, output_type=pytesseract.Output.DICT)
            print(f"DEBUG: Tesseract OSD Result: {results}")
            rotation = results["rotate"]
            
            if rotation == 0:
                print("DEBUG: Orientation is correct (0 deg).")
                return image, False
            
            print(f"DEBUG: Detected rotation needed: {rotation}")
            
            # Rotation mapping
            if rotation == 90:
                return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE), True
            elif rotation == 180:
                return cv2.rotate(image, cv2.ROTATE_180), True
            elif rotation == 270:
                return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE), True
                
            return image, False
            
        except Exception as e:
            print(f"ERROR: Auto-Orientation failed: {e}")
            # Raise it so GUI knows IT FAILED, not just "False" which means "Correct"
            raise e

    def load_image(self, path):
        return cv2.imread(path)

    def process(self, image_path, output_path):
        img = self.load_image(image_path)
        if img is None:
            raise FileNotFoundError(f"Image not found at {image_path}")
        
        # 1. Detect
        contours = self.detect_document(img)
        
        # 2. Rectify
        warped = self.rectify(img, contours)
        
        # 3. Enhance
        final = self.enhance(warped)
        
        cv2.imwrite(output_path, final)
        print(f"Saved to {output_path}")

    def detect_document(self, img):
        """
        Robust Detection Strategy (Merged):
        Uses Center-Seeded Watershed to handle complex backgrounds (grates, crumpled paper) 
        while maintaining precise edge detection.
        1. Resize & Blur.
        2. Gradient Calculation (Sobel).
        3. Markers: Center = Paper, Corners = Background.
        4. Watershed Segmentation.
        5. Contour Approximation (Iterative).
        """
        # Resize for speed and noise reduction
        target_height = 500
        ratio = img.shape[0] / float(target_height)
        image = cv2.resize(img, (int(img.shape[1] / ratio), target_height))
        h, w = image.shape[:2]
        
        # 1. Blur & Grayscale
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        
        # 2. Gradient (Sobel) to find edges/elevation
        grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        gradient = cv2.magnitude(grad_x, grad_y)
        gradient = cv2.normalize(gradient, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        
        # 3. Markers
        markers = np.zeros((h, w), dtype=np.int32)
        
        # Background Marker: Corners (assumed background)
        cv2.circle(markers, (5, 5), 10, 1, -1)
        cv2.circle(markers, (w-5, 5), 10, 1, -1)
        cv2.circle(markers, (w-5, h-5), 10, 1, -1)
        cv2.circle(markers, (5, h-5), 10, 1, -1)
        
        # Foreground Marker: Center (assumed paper)
        cx, cy = w // 2, h // 2
        cv2.circle(markers, (cx, cy), 40, 2, -1)
        
        # 4. Watershed
        watershed_mask = cv2.watershed(blurred, markers)
        
        # Extract Foreground (Label 2)
        mask = np.zeros((h, w), dtype=np.uint8)
        mask[watershed_mask == 2] = 255
        
        # TIGHTEN: Reduced erosion to 1 to avoid cutting text, but keep edges clean
        mask = cv2.erode(mask, None, iterations=1)
        
        # 5. Find Contour of the "Center Blob"
        cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        
        if not cnts:
            # Fallback for completely failed detection
            print("Detection failed, returning full frame.")
            return np.array([[[0, 0]], [[img.shape[1], 0]], [[img.shape[1], img.shape[0]]], [[0, img.shape[0]]]]).reshape(4, 2)
            
        c = max(cnts, key=cv2.contourArea)
        
        # Approximate loop to find 4 points
        peri = cv2.arcLength(c, True)
        screenCnt = None
        
        # Iterative Approximation
        for epsilon_factor in np.linspace(0.02, 0.10, 10):
            approx = cv2.approxPolyDP(c, epsilon_factor * peri, True)
            if len(approx) == 4:
                screenCnt = approx
                break
        
        if screenCnt is None:
            # Convex Hull Fallback
            hull = cv2.convexHull(c)
            peri_hull = cv2.arcLength(hull, True)
            approx = cv2.approxPolyDP(hull, 0.04 * peri_hull, True)
            if len(approx) == 4:
                screenCnt = approx
            else:
                # Bounding Rect Fallback
                rect = cv2.minAreaRect(c)
                box = cv2.boxPoints(rect)
                screenCnt = np.int64(box)
                screenCnt = screenCnt.reshape(4, 1, 2)
            
        return screenCnt.reshape(4, 2) * ratio


    def rectify(self, img, contours):
        from .rectify import four_point_transform
        return four_point_transform(img, contours)

    def enhance(self, img, mode='scan'):
        from .enhance import enhance_scan, enhance_magic_color
        if mode == 'scan':
            return enhance_scan(img)
        elif mode == 'color':
            return enhance_magic_color(img)
        elif mode == 'original':
            return img # Return rectified but not enhanced
        return img

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
from src.processor import DocumentProcessor
import threading

class DocAugApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DocAUG - Document Rectification")
        self.root.geometry("1000x800")
        self.root.configure(bg="#2E2E2E")

        self.processor = DocumentProcessor(mode='auto')
        
        self.current_image = None
        self.current_image_path = None # Track path for logging
        self.processed_image = None

        self.setup_ui()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#1E1E1E", height=60)
        header.pack(fill=tk.X)
        lbl_title = tk.Label(header, text="DocAUG", font=("Segoe UI", 24, "bold"), fg="#FFFFFF", bg="#1E1E1E")
        lbl_title.pack(side=tk.LEFT, padx=20, pady=10)

        # Toolbar
        toolbar = tk.Frame(self.root, bg="#3E3E3E", height=50)
        toolbar.pack(fill=tk.X)

        btn_style = {"bg": "#007ACC", "fg": "white", "font": ("Segoe UI", 10), "bd": 0, "padx": 15, "pady": 5}
        
        tk.Button(toolbar, text="Load Image", command=self.load_image, **btn_style).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(toolbar, text="Save Result", command=self.save_image, **btn_style).pack(side=tk.LEFT, padx=10, pady=10)
        
        # Rotation Controls
        tk.Label(toolbar, text="|", fg="#555", bg="#3E3E3E", font=("Segoe UI", 14)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="↻ Auto-Orient", command=self.auto_orient, **btn_style).pack(side=tk.LEFT, padx=5, pady=10)
        tk.Button(toolbar, text="↶ Left", command=lambda: self.manual_rotate('left'), **btn_style).pack(side=tk.LEFT, padx=5, pady=10)
        tk.Button(toolbar, text="↷ Right", command=lambda: self.manual_rotate('right'), **btn_style).pack(side=tk.LEFT, padx=5, pady=10)
        
        # Options Panel (Placed at TOP for visibility)
        options_frame = tk.Frame(self.root, bg="#2E2E2E")
        options_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(options_frame, text="Output Style:", fg="white", bg="#2E2E2E", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)
        
        self.enhancement_mode = tk.StringVar(value="color") # Default to Magic Color
        
        modes = [("Magic Color", "color"), ("Original", "original")]
        
        for text, val in modes:
            tk.Radiobutton(options_frame, text=text, variable=self.enhancement_mode, 
                           value=val, command=self.run_process,
                           bg="#2E2E2E", fg="white", selectcolor="#444", activebackground="#2E2E2E", activeforeground="white",
                           font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)



        # Main Content area
        self.content = tk.Frame(self.root, bg="#2E2E2E")
        self.content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Panels (Left: Original, Right: Result)
        self.panel_left = tk.Label(self.content, bg="#1E1E1E", text="Original Image", fg="#888")
        self.panel_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.panel_right = tk.Label(self.content, bg="#1E1E1E", text="Processed Document", fg="#888")
        self.panel_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if not path:
            return
        
        try:
            self.current_image = cv2.imread(path)
            self.current_image_path = path
            self.display_image(self.current_image, self.panel_left)
            self.run_process()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run_process(self):
        if self.current_image is None:
            print("DEBUG: No image loaded.")
            return
        # Auto process
        self.status_loading(True)
        
        # Run in thread
        enhance_mode = self.enhancement_mode.get()
        threading.Thread(target=self.process_flow, args=(enhance_mode,)).start()

    def process_flow(self, enhance_mode):
        try:
            print(f"DEBUG: process_flow running with enhance: {enhance_mode}")
            
            # Detect (Using new 'Smart Merged' logic)
            pts = self.processor.detect_document(self.current_image)
            
            # Visualize detection on the original image (Left Panel)
            debug_img = self.current_image.copy()
            if pts is not None:
                pts_int = pts.astype(int).reshape((-1, 1, 2))
                # Use Green for the unified robust mode
                cv2.polylines(debug_img, [pts_int], True, (0, 255, 0), 5) 
            
            # Update Left Panel with the debug image
            self.root.after(0, lambda: self.display_image(debug_img, self.panel_left))

            # Rectify
            warped = self.processor.rectify(self.current_image, pts)
            
            # Enhance
            self.processed_image = self.processor.enhance(warped, mode=enhance_mode)
            print(f"DEBUG: Enhanced image shape: {self.processed_image.shape}")
            
            # Display
            self.root.after(0, lambda: self.display_image(self.processed_image, self.panel_right))
            self.root.after(0, lambda: self.status_loading(False))
            
            print("DEBUG: Processing complete.")
            
        except Exception as e:
            print(f"ERROR: {e}")
            self.root.after(0, lambda: messagebox.showerror("Processing Error", str(e)))
            self.root.after(0, lambda: self.status_loading(False))

    def display_image(self, cv_img, label_widget):
        # Resize to fit widget roughly
        h, w = cv_img.shape[:2]
        
        # Max dimensions
        max_h = 600
        max_w = 450
        
        ratio = min(max_w/w, max_h/h)
        new_w = int(w * ratio)
        new_h = int(h * ratio)
        
        resized = cv2.resize(cv_img, (new_w, new_h))
        
        # Convert to RGB for PIL
        if len(resized.shape) == 2:
            rgb = cv2.cvtColor(resized, cv2.COLOR_GRAY2RGB)
        else:
            rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            
        img_pil = Image.fromarray(rgb)
        img_tk = ImageTk.PhotoImage(img_pil)
        
        label_widget.config(image=img_tk, text="")
        label_widget.image = img_tk  # Keep reference

    def save_image(self):
        if self.processed_image is None:
            messagebox.showwarning("Warning", "No processed image to save.")
            return
            
        path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
        if path:
            cv2.imwrite(path, self.processed_image)
            messagebox.showinfo("Success", f"Saved to {path}")

    def status_loading(self, is_loading):
        if is_loading:
            self.panel_right.config(text="Processing...")
        
    def auto_orient(self):
        if self.current_image is None and self.processed_image is None:
            messagebox.showwarning("Warning", "Load an image or process one first.")
            return

        # Prefer rotating the Processed image if available, otherwise Original
        target_img = self.processed_image if self.processed_image is not None else self.current_image
        
        self.status_loading(True)
        # Run in thread
        threading.Thread(target=self._run_auto_orient, args=(target_img,)).start()

    def _run_auto_orient(self, img):
        print("DEBUG: Running Auto-Orient...")
        try:
            rotated, was_rotated = self.processor.correct_orientation(img)
            
            if was_rotated:
                print("DEBUG: Rotated.")
                self.processed_image = rotated
                self.root.after(0, lambda: self.display_image(self.processed_image, self.panel_right))
                self.root.after(0, lambda: messagebox.showinfo("Orientation", "Image auto-rotated."))
            else:
                print("DEBUG: No rotation needed.")
                self.root.after(0, lambda: messagebox.showinfo("Orientation", "Orientation deemed correct (0° detected)."))
                
        except Exception as e:
            print(f"DEBUG: Auto-Orient Error: {e}")
            self.root.after(0, lambda: messagebox.showerror("Orientation Error", f"Failed to detect orientation.\nError: {e}"))
            
        self.root.after(0, lambda: self.status_loading(False))

    def manual_rotate(self, direction):
        if self.processed_image is None:
             if self.current_image is None:
                return
             # If no processed image, rotate original? No, let's process first usually. 
             # But user might want to rotate original. Let's rotate 'current_image' AND 'processed_image' if exists.
             # Actually, best workflow: Rotate 'processed' result.
             pass
        
        target = self.processed_image if self.processed_image is not None else self.current_image
        
        if direction == 'left':
            rotated = cv2.rotate(target, cv2.ROTATE_90_COUNTERCLOCKWISE)
        else:
            rotated = cv2.rotate(target, cv2.ROTATE_90_CLOCKWISE)
            
        self.processed_image = rotated
        self.display_image(self.processed_image, self.panel_right)
        
    def status_loading(self, is_loading):
        if is_loading:
            self.panel_right.config(text="Processing...")

if __name__ == "__main__":
    root = tk.Tk()
    app = DocAugApp(root)
    root.mainloop()

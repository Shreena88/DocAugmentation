# DocAUG - Document Rectification Tool

DocAUG is an intelligent document image rectification tool that automatically detects, straightens, and enhances scanned documents. It uses advanced computer vision techniques to transform skewed or perspective-distorted document images into clean, readable scans.

## Screenshots

### Application Interface
![DocAUG GUI Interface](images/gui-interface.png)

### Document Processing Example
![Document Processing](images/document-processing.png)
*Left: Original skewed document with detection outline | Right: Processed and rectified document*

## Download

### 📥 Ready-to-Use Application
**[Download DocAUG.exe](https://github.com/your-username/DocAUG/releases/latest/download/DocAUG.exe)** - Click to download the latest version

*No Python installation required! Just download and run.*

### System Requirements
- Windows 10/11 (64-bit)
- Tesseract OCR (for auto-orientation feature)
- 4GB RAM minimum, 8GB recommended

## Quick Start

### For End Users (No Programming Required)
1. **[Download DocAUG.exe](https://github.com/your-username/DocAUG/releases/latest/download/DocAUG.exe)** ⬇️
2. Install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki
3. Double-click `DocAUG.exe` to start
4. Click "Load Image" to select your document
5. The app will automatically detect and straighten your document
6. Click "Save Result" to export the processed image

### For Developers
```bash
git clone <repository-url>
cd DocAUG
pip install -r requirements.txt
python gui.py
```

## Features

### Core Functionality
- **Automatic Document Detection**: Uses center-seeded watershed algorithm to detect document boundaries even in complex backgrounds
- **Perspective Correction**: Four-point perspective transformation to create top-down document views
- **Smart Enhancement**: Multiple enhancement modes including scan optimization and magic color enhancement
- **Auto-Orientation**: Automatic text orientation detection and correction using OCR

### User Interfaces
- **Command Line Interface**: Batch processing and automation support
- **Graphical User Interface**: User-friendly desktop application with real-time preview
- **Processing Modes**: Auto, CPU, and GPU acceleration support

### Enhancement Options
- **Magic Color**: Enhanced contrast and saturation for vibrant document colors
- **Scan Mode**: Clean black and white output optimized for text readability
- **Original**: Rectified document without additional enhancement

## Installation

### Option 1: Executable File (Recommended for End Users)
**[📥 Download DocAUG.exe](https://github.com/your-username/DocAUG/releases/latest/download/DocAUG.exe)**

For easy use without Python installation:

1. Click the download link above to get the latest `DocAUG.exe`
2. Install Tesseract OCR (required for auto-orientation):
   - Download from: https://gto launch the application

### Option 2: Python Installation (For Developers)

#### Prerequisites
- Python 3.7 or higher
- OpenCV
- NumPy
- Tesseract OCR (for auto-orientation feature)

#### Install Dependencies
```bash
pip install -r requirements.txt
```

### Tesseract OCR Setup
For auto-orientation functionality, install Tesseract OCR:

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install to default location (C:\Program Files\Tesseract-OCR\)

**Linux/macOS:**
```bash
# Ubuntu/Debian
sudo apt install tesseract-ocr

# macOS
brew install tesseract
```

## Usage

### Executable Version (No Python Required)
Simply double-click `DocAUG.exe` to launch the graphical interface.

### Command Line Interface (Python)
```bash
# Basic usage
python main.py --input document.jpg --output result.jpg

# Specify processing mode
python main.py -i input.jpg -o output.jpg --mode gpu

# Available modes: auto, cpu, gpu
```

### Graphical User Interface (Python)
```bash
python gui.py
```

#### GUI Features:
- **Load Image**: Import document images (JPG, JPEG, PNG)
- **Real-time Processing**: Automatic detection and rectification preview
- **Enhancement Controls**: Switch between Magic Color and Original modes
- **Orientation Tools**: Auto-orient, manual left/right rotation
- **Save Results**: Export processed documents

## Building Executable

### For Developers: Creating DocAUG.exe

To create a standalone executable file that users can run without Python:

1. **Install PyInstaller**:
```bash
pip install pyinstaller
```

2. **Create the executable**:
```bash
# For GUI version (recommended)
pyinstaller --onefile --windowed --icon=icon.ico gui.py --name DocAUG

# For CLI version
pyinstaller --onefile main.py --name DocAUG-CLI
```

3. **Advanced build with version info**:
```bash
pyinstaller --onefile --windowed --version-file=version_info.txt --icon=icon.ico gui.py --name DocAUG
```

The executable will be created in the `dist/` folder and can be distributed to users who don't have Python installed.

### Build Options Explained:
- `--onefile`: Creates a single executable file
- `--windowed`: Hides the console window (for GUI apps)
- `--icon=icon.ico`: Adds a custom icon (optional)
- `--version-file`: Includes version information
- `--name`: Sets the output filename

## Project Structure

```
DocAUG/
├── main.py              # Command line interface
├── gui.py               # Graphical user interface
├── requirements.txt     # Python dependencies
├── version_info.txt     # Version information
├── src/
│   ├── processor.py     # Main document processing logic
│   ├── enhance.py       # Image enhancement algorithms
│   ├── rectify.py       # Perspective correction functions
│   ├── utils.py         # Hardware detection utilities
│   └── logger.py        # Activity logging system
└── logs/                # Generated log files
```

## Technical Details

### Detection Algorithm
DocAUG uses a robust center-seeded watershed approach:
1. **Preprocessing**: Image resizing and Gaussian blur for noise reduction
2. **Gradient Calculation**: Sobel operators to detect edges
3. **Marker-based Segmentation**: Center seed for document, corner seeds for background
4. **Watershed Segmentation**: Separates document from background
5. **Contour Approximation**: Iterative polygon approximation to find document corners

### Enhancement Modes
- **Scan Enhancement**: Adaptive thresholding for clean black/white output
- **Magic Color**: CLAHE (Contrast Limited Adaptive Histogram Equalization) for improved contrast and color

### Hardware Acceleration
- Automatic detection of CUDA-enabled GPUs
- OpenVINO support for Intel hardware
- Fallback to CPU processing when hardware acceleration unavailable

## Logging

DocAUG automatically logs processing activities to `logs/activity_log.md` with:
- Timestamp
- Input file information
- Detection and enhancement modes used
- Processing status

## Requirements

- opencv-python
- numpy
- pytesseract (for orientation detection)
- tkinter (for GUI - usually included with Python)
- PIL/Pillow (for GUI image handling)

## License

Open Source - See version_info.txt for details

## Contributing

This is an open-source project. Contributions are welcome for:
- Algorithm improvements
- New enhancement modes
- Performance optimizations
- Bug fixes and stability improvements

## Troubleshooting

### Common Issues
1. **Tesseract not found**: Ensure Tesseract OCR is installed and in system PATH
2. **GPU acceleration not working**: Verify CUDA installation and OpenCV GPU support
3. **Detection failures**: Try different lighting conditions or image preprocessing

### Performance Tips
- Use GPU mode for faster processing on supported hardware
- Resize large images before processing for better performance
- Ensure good lighting and contrast in source images for optimal detection

## Version

Current Version: 1.0.0
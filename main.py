import argparse
import logging
import sys
import os
from src.processor import DocumentProcessor

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/latest_run.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Automatic Document Image Rectification Tool")
    parser.add_argument("--input", "-i", type=str, required=True, help="Path to input image")
    parser.add_argument("--output", "-o", type=str, required=True, help="Path to output image")
    parser.add_argument("--mode", "-m", type=str, default="auto", choices=["auto", "cpu", "gpu"], help="Processing mode")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        logging.error(f"Input file not found: {args.input}")
        return

    logging.info(f"Starting processing for {args.input}")
    
    try:
        processor = DocumentProcessor(mode=args.mode)
        processor.process(args.input, args.output)
        logging.info(f"Successfully saved to {args.output}")
    except Exception as e:
        logging.error(f"Processing failed: {e}", exc_info=True)

if __name__ == "__main__":
    main()

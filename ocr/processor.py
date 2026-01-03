# ocr/processor.py
from PIL import Image
import pytesseract

import os

# Set Tesseract Path (Environment Variable > System PATH > Windows Default)
pytesseract.pytesseract.tesseract_cmd = os.environ.get('TESSERACT_CMD', 'tesseract')

def extract_text(image_path):
    try:
        img = Image.open(image_path).convert('L')
        config = '--oem 3 --psm 6 -l eng+hin'
        return pytesseract.image_to_string(img, config=config).strip()
    except:
        return ""
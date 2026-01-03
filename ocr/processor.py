# ocr/processor.py
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text(image_path):
    try:
        img = Image.open(image_path).convert('L')
        config = '--oem 3 --psm 6 -l eng+hin'
        return pytesseract.image_to_string(img, config=config).strip()
    except:
        return ""
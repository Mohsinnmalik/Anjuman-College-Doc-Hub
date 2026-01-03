# utils/pdf.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
from PIL import Image
import textwrap
import os

def create_official_pdf(letter_text, username, proof_path):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # --- PROFESSIONAL HEADER START ---
    
    # 1. Logos
    # Use absolute paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOGO_L = os.path.join(BASE_DIR, "static", "assets", "logo_left.jpg")
    LOGO_R = os.path.join(BASE_DIR, "static", "assets", "logo_right.jpg")
    
    # Logo Configuration
    logo_y = height - 130
    logo_w = 90
    logo_h = 90
    
    if os.path.exists(LOGO_L):
        c.drawImage(ImageReader(LOGO_L), 30, logo_y, width=logo_w, height=logo_h, mask='auto', preserveAspectRatio=True)
    
    if os.path.exists(LOGO_R):
        c.drawImage(ImageReader(LOGO_R), width - 30 - logo_w, logo_y, width=logo_w, height=logo_h, mask='auto', preserveAspectRatio=True)

    # 2. College Text (Centered)
    # "ANJUMAN COLLEGE OF"
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height - 60, "ANJUMAN COLLEGE OF")
    
    # "ENGINEERING & TECHNOLOGY"
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, height - 85, "ENGINEERING & TECHNOLOGY")
    
    # Address
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width/2, height - 105, "Mangalwari Bazaar Road, Sadar, Nagpur")
    
    # Managed By
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width/2, height - 120, "Managed By: Anjuman Hami-E-Islam")
    
    # Separator Line
    c.setLineWidth(2)
    c.line(30, height - 135, width - 30, height - 135)
    
    # Document Title
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height - 170, "Sick Leave Application")
    
    # --- HEADER END ---

    # Body
    c.setFont("Helvetica", 11)
    y = height - 210 # Started lower to clear the header
    lines = letter_text.split('\n')
    for line in lines:
        if line.startswith('**'):
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, line.replace('**', ''))
            y -= 20
        else:
            c.setFont("Helvetica", 11)
            wrapped = textwrap.wrap(line, width=90)
            for w in wrapped:
                if y < 100:
                    c.showPage()
                    y = height - 50
                c.drawString(70, y, w)
                y -= 15
            y -= 5
    
    # Page 2: Proof
    c.showPage()
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height - 50, "MEDICAL CERTIFICATE")
    
    try:
        img = Image.open(proof_path)
        img.thumbnail((width - 100, height - 200))
        x = (width - img.width) / 2
        c.drawImage(ImageReader(img), x, height - 100 - img.height, width=img.width, height=img.height)
    except:
        c.drawString(70, height - 200, "[Proof image failed to load]")
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
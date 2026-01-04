# utils/certificate.py
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps
import os

LOGO_PATH = "static/assets/college_logo.png"
SIGNATURE_PATH = "static/assets/signature.png"
# This is our GOLD BORDER FRAME (Landscape, Transparent center or White center handled in code)
FRAME_PATH = "static/assets/landscape_gold_border.png" 

COLLEGE_NAME = "XYZ COLLEGE OF ENGINEERING"

def get_font(name, size):
    try:
        # Linux/Docker Paths
        font_map = {
            'header': ['LiberationSerif-Bold.ttf', 'georgiab.ttf', 'timesbd.ttf', 'arialbd.ttf'],
            'body': ['LiberationSerif-Regular.ttf', 'georgia.ttf', 'times.ttf', 'arial.ttf'],
            'fancy': ['LiberationSans-Italic.ttf', 'calibri.ttf', 'corsiva.ttf'],
            'sans': ['LiberationSans-Regular.ttf', 'arial.ttf']
        }
        
        # Standard Linux Font Dir
        linux_font_dir = "/usr/share/fonts/truetype/liberation/"
        
        candidates = font_map.get(name, ['LiberationSans-Regular.ttf', 'arial.ttf'])
        for f in candidates:
            # Check absolute Linux path first
            linux_path = os.path.join(linux_font_dir, f)
            if os.path.exists(linux_path):
                return ImageFont.truetype(linux_path, size)
            
            # Check local directory/Windows system
            try: return ImageFont.truetype(f, size)
            except: continue
            
        return ImageFont.load_default()
    except: return ImageFont.load_default()

def draw_fit_text(draw, width, text, font_name, max_size, y_pos, color, margin_x=150):
    """Draws text centered and scaled to fit within margins"""
    max_w = width - (2 * margin_x)
    size = max_size
    
    # Font Mapping for Linux Fallback
    font_map = {
        'timesbd.ttf': 'LiberationSerif-Bold.ttf',
        'times.ttf': 'LiberationSerif-Regular.ttf',
        'arialbd.ttf': 'LiberationSans-Bold.ttf',
        'arial.ttf': 'LiberationSans-Regular.ttf'
    }
    
    linux_font_dir = "/usr/share/fonts/truetype/liberation/"
    
    def load_dynamic_font(fname, fsize):
        # Try 1: Direct load (Windows/Local)
        try: return ImageFont.truetype(fname, fsize)
        except: pass
        
        # Try 2: Linux Path
        linux_path = os.path.join(linux_font_dir, font_map.get(fname, fname))
        if os.path.exists(linux_path):
             return ImageFont.truetype(linux_path, fsize)
             
        # Try 3: Linux Mapped Name (if in path)
        try: return ImageFont.truetype(font_map.get(fname, fname), fsize)
        except: pass
        
        return ImageFont.load_default()

    font = ImageFont.load_default()
    while size > 15:
        font = load_dynamic_font(font_name, size)
        
        try:
            if draw.textlength(text, font=font) <= max_w:
                break
        except: break # Handle default font which might fail textlength in older PILLOW
        size -= 2
        
    try: w = draw.textlength(text, font=font)
    except: w = draw.textsize(text, font=font)[0] # Fallback for older Pillow
    
    draw.text(((width - w)/2, y_pos), text, fill=color, font=font)

def make_white_transparent(img):
    """Simple heuristic to make white pixels transparent"""
    img = img.convert("RGBA")
    datas = img.getdata()
    newData = []
    for item in datas:
        # If pixel is very light (near white), make it transparent
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
             newData.append((255, 255, 255, 0))
        else:
             newData.append(item)
    img.putdata(newData)
    return img

def generate_certificate(bg_path, output_path, recipient, event, date, principal_path=None, hod_path=None):
    # 1. Setup Canvas (Letter Landscape 3300x2550 @ 300 DPI)
    CANVAS_W, CANVAS_H = 3300, 2550
    base = Image.new('RGB', (CANVAS_W, CANVAS_H), (255, 255, 255))
    
    # 2. Process User Image (Watermark)
    if bg_path and os.path.exists(bg_path):
        try:
            user_img = Image.open(bg_path).convert("RGBA")
            user_img = ImageOps.fit(user_img, (CANVAS_W, CANVAS_H))
            white_layer = Image.new('RGBA', (CANVAS_W, CANVAS_H), (255,255,255,200)) # Faded
            watermarked = Image.alpha_composite(user_img, white_layer)
            base.paste(watermarked.convert("RGB"), (0,0))
        except: pass

    # 3. Add Gold Border Frame
    # We resize the frame to the new resolution
    if os.path.exists(FRAME_PATH):
        frame = Image.open(FRAME_PATH).resize((CANVAS_W, CANVAS_H))
        if frame.mode != 'RGBA': frame = make_white_transparent(frame)
        base.paste(frame, (0,0), frame)
    
    draw = ImageDraw.Draw(base)
    
    # Colors
    GOLD = (181, 148, 16, 255)
    NAVY = (20, 40, 90, 255)
    BLACK = (40, 40, 40, 255)
    
    center_x = CANVAS_W // 2
    
    # Logos (Top Corners)
    LOGO_SIZE = 350 
    LOGO_MARGIN_X = 300 # Aggressive shift to ensure visibility
    LOGO_MARGIN_Y = 200
    
    LOGO_L_PATH = "static/assets/logo_left.jpg"
    LOGO_R_PATH = "static/assets/logo_right.jpg"
    
    if os.path.exists(LOGO_L_PATH):
        l_logo = Image.open(LOGO_L_PATH).resize((LOGO_SIZE, LOGO_SIZE))
        if l_logo.mode != 'RGBA': l_logo = make_white_transparent(l_logo)
        base.paste(l_logo, (LOGO_MARGIN_X, LOGO_MARGIN_Y), l_logo)

    if os.path.exists(LOGO_R_PATH):
        r_logo = Image.open(LOGO_R_PATH).resize((LOGO_SIZE, LOGO_SIZE))
        if r_logo.mode != 'RGBA': r_logo = make_white_transparent(r_logo)
        base.paste(r_logo, (CANVAS_W - LOGO_MARGIN_X - LOGO_SIZE, LOGO_MARGIN_Y), r_logo)

    # Main Header "CERTIFICATE OF ACHIEVEMENT"
    # Adjusted Y positions for 2550 height
    draw_fit_text(draw, CANVAS_W, "CERTIFICATE", "timesbd.ttf", 200, 600, GOLD)
    draw_fit_text(draw, CANVAS_W, "OF ACHIEVEMENT", "timesbd.ttf", 100, 800, GOLD)
    
    # "is presented to"
    draw_fit_text(draw, CANVAS_W, "This certificate is proudly presented to", "times.ttf", 60, 1000, BLACK)
    
    # Recipient Name (BIG)
    draw_fit_text(draw, CANVAS_W, recipient.upper(), "timesbd.ttf", 250, 1200, NAVY)
    
    # Line under name
    draw.line((600, 1500, CANVAS_W-600, 1500), fill=GOLD, width=5)
    
    # "For outstanding..."
    draw_fit_text(draw, CANVAS_W, "For outstanding performance in", "times.ttf", 60, 1600, BLACK)
    
    # Event
    draw_fit_text(draw, CANVAS_W, event, "arialbd.ttf", 120, 1750, BLACK)
    
    # Date & Signatures (Bottom)
    
    # Date (Center Bottom)
    draw_fit_text(draw, CANVAS_W, f"Awarded on {date}", "times.ttf", 50, 2200, BLACK)
    
    # Signatures
    # HOD (Bottom Left)
    # Always draw line and label
    draw.line((400, 2200, 800, 2200), fill=BLACK, width=3)
    draw.text((480, 2220), "H.O.D Signature", fill=BLACK, font=get_font('body', 40))
    
    if hod_path and os.path.exists(hod_path):
        try:
            hod_img = Image.open(hod_path).resize((400, 150))
            if hod_img.mode != 'RGBA': hod_img = make_white_transparent(hod_img)
            # Position: Above line
            base.paste(hod_img, (400, 2050), hod_img)
        except: pass

    # Principal (Bottom Right)
    # Always draw line and label
    draw.line((CANVAS_W - 800, 2200, CANVAS_W - 400, 2200), fill=BLACK, width=3)
    draw.text((CANVAS_W - 750, 2220), "Principal Signature", fill=BLACK, font=get_font('body', 40))

    if principal_path and os.path.exists(principal_path):
        try:
            p_img = Image.open(principal_path).resize((400, 150))
            if p_img.mode != 'RGBA': p_img = make_white_transparent(p_img)
            # Position: Above line
            base.paste(p_img, (CANVAS_W - 800, 2050), p_img)
        except: pass
    
    # If no Principal signature uploaded, do we show blank line? 
    # User said: "otherwise keep it empty/blank". 
    # So if no file, we draw nothing. 
        
    base.save(output_path)
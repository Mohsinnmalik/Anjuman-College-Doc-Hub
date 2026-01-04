from PIL import Image, ImageDraw, ImageFont, ImageOps
import os

# --- HELPERS (Copied for stability) ---
# --- HELPERS (Copied for stability) ---
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
    img = img.convert("RGBA")
    datas = img.getdata()
    newData = []
    for item in datas:
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
             newData.append((255, 255, 255, 0))
        else:
             newData.append(item)
    img.putdata(newData)
    return img

# --- MAIN GENERATOR ---
def generate_poster(bg_path, output_path, title, subtitle, date, venue):
    # 1. Setup Canvas: A4 Portrait (2480 x 3508 px)
    CANVAS_W, CANVAS_H = 2480, 3508
    base = Image.new('RGB', (CANVAS_W, CANVAS_H), (255, 255, 255))
    
    # 2. Process Background (Watermark)
    if bg_path and os.path.exists(bg_path):
        try:
            user_img = Image.open(bg_path).convert("RGBA")
            user_img = ImageOps.fit(user_img, (CANVAS_W, CANVAS_H))
            # White fade layer
            white_layer = Image.new('RGBA', (CANVAS_W, CANVAS_H), (255,255,255,210)) # Heavy fade for text readability
            watermarked = Image.alpha_composite(user_img, white_layer)
            base.paste(watermarked.convert("RGB"), (0,0))
        except: pass

    draw = ImageDraw.Draw(base)
    
    # Colors
    MAROON = (100, 20, 20, 255) # Anjuman Theme
    BLACK = (0, 0, 0, 255)
    NAVY = (20, 40, 90, 255)
    GOLD = (181, 148, 16, 255)
    
    # --- HEADER SECTION (Top 600px) ---
    # Logos
    LOGO_SIZE = 300
    LOGO_MARGIN = 120
    LOGO_L_PATH = "static/assets/logo_left.jpg"
    LOGO_R_PATH = "static/assets/logo_right.jpg"
    
    # Left Logo
    if os.path.exists(LOGO_L_PATH):
        l_logo = Image.open(LOGO_L_PATH).resize((LOGO_SIZE, LOGO_SIZE))
        if l_logo.mode != 'RGBA': l_logo = make_white_transparent(l_logo)
        base.paste(l_logo, (LOGO_MARGIN, LOGO_MARGIN), l_logo)
        
    # Right Logo
    if os.path.exists(LOGO_R_PATH):
        r_logo = Image.open(LOGO_R_PATH).resize((LOGO_SIZE, LOGO_SIZE))
        if r_logo.mode != 'RGBA': r_logo = make_white_transparent(r_logo)
        base.paste(r_logo, (CANVAS_W - LOGO_MARGIN - LOGO_SIZE, LOGO_MARGIN), r_logo)

    # Header Text
    center_x = CANVAS_W // 2
    # "ANJUMAN COLLEGE OF"
    draw_fit_text(draw, CANVAS_W, "ANJUMAN COLLEGE OF", "arialbd.ttf", 90, 150, MAROON, margin_x=450)
    # "ENGINEERING & TECHNOLOGY"
    draw_fit_text(draw, CANVAS_W, "ENGINEERING & TECHNOLOGY", "arialbd.ttf", 110, 260, MAROON, margin_x=450)
    # Address
    draw_fit_text(draw, CANVAS_W, "Mangalwari Bazaar Road, Sadar, Nagpur", "arial.ttf", 55, 400, BLACK)
    # Managed By
    draw_fit_text(draw, CANVAS_W, "Managed By: Anjuman Hami-E-Islam", "arialbd.ttf", 50, 480, BLACK)
    
    # Separator Line
    draw.line((100, 600, CANVAS_W - 100, 600), fill=GOLD, width=5)
    
    # --- CONTENT SECTION ---
    
    # "PRESENTS" or "ANNOUNCES"
    draw_fit_text(draw, CANVAS_W, "PRESENTS", "times.ttf", 60, 800, BLACK)
    
    # Main Title (The Event)
    draw_fit_text(draw, CANVAS_W, title.upper(), "arialbd.ttf", 250, 1000, NAVY, margin_x=100)
    
    # Subtitle
    if subtitle:
        draw_fit_text(draw, CANVAS_W, subtitle, "times.ttf", 100, 1350, BLACK)
        
    # --- DETAILS BOX (Bottom) ---
    box_top = CANVAS_H - 1000
    
    # Details Formatting
    details_y = 1800
    
    # DATE Icon/Text
    draw_fit_text(draw, CANVAS_W, "DATE", "arialbd.ttf", 60, details_y, GOLD)
    draw_fit_text(draw, CANVAS_W, date, "arialbd.ttf", 120, details_y + 80, BLACK)
    
    # VENUE Icon/Text
    venue_y = details_y + 300
    draw_fit_text(draw, CANVAS_W, "VENUE", "arialbd.ttf", 60, venue_y, GOLD)
    draw_fit_text(draw, CANVAS_W, venue, "arialbd.ttf", 100, venue_y + 80, BLACK)
    
    # Footer
    draw.line((100, CANVAS_H - 200, CANVAS_W - 100, CANVAS_H - 200), fill=GOLD, width=5)
    draw_fit_text(draw, CANVAS_W, "Join us for this spectacular event!", "times.ttf", 60, CANVAS_H - 150, BLACK)

    base.save(output_path)
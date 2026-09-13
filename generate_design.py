"""
Generates print-ready PNG designs (transparent background) for the
PawsAndScrubs niche: breed-specific pet ownership x nursing/healthcare.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

CANVAS_W, CANVAS_H = 3591, 4364  # matches Printify front placeholder for blueprint 12

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_BLACK = os.path.join(SCRIPT_DIR, "ArchivoBlack-Regular.ttf")  # OFL licensed, single weight
FONT_CONDENSED = os.path.join(SCRIPT_DIR, "Oswald-Variable.ttf")   # OFL licensed, variable weight
FONT_CONDENSED_WEIGHT = 700  # bold instance of the variable font

PALETTES = {
    "black_shirt": {"ink": (255, 255, 255, 255), "accent": (255, 200, 87, 255)},
    "white_shirt": {"ink": (30, 30, 30, 255), "accent": (216, 90, 80, 255)},
}


def load_font(font_path, size):
    font = ImageFont.truetype(font_path, size)
    if font_path == FONT_CONDENSED:
        font.set_variation_by_axes([FONT_CONDENSED_WEIGHT])
    return font


def fit_text_width(draw, text, font_path, max_width, start_size, min_size=40):
    size = start_size
    while size > min_size:
        font = load_font(font_path, size)
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            return font, w, bbox
        size -= 4
    return load_font(font_path, min_size), 0, (0, 0, 0, 0)


def draw_paw_print(draw, cx, cy, scale, color):
    pad_w, pad_h = 130 * scale, 100 * scale
    draw.ellipse([cx - pad_w / 2, cy - pad_h / 2, cx + pad_w / 2, cy + pad_h / 2], fill=color)
    toe_r = 42 * scale
    offsets = [(-105 * scale, -95 * scale), (-38 * scale, -130 * scale),
               (38 * scale, -130 * scale), (105 * scale, -95 * scale)]
    for ox, oy in offsets:
        draw.ellipse([cx + ox - toe_r, cy + oy - toe_r, cx + ox + toe_r, cy + oy + toe_r], fill=color)


def draw_medical_cross(draw, cx, cy, size, color):
    arm = size * 0.32
    draw.rectangle([cx - arm / 2, cy - size / 2, cx + arm / 2, cy + size / 2], fill=color)
    draw.rectangle([cx - size / 2, cy - arm / 2, cx + size / 2, cy + arm / 2], fill=color)


def generate(breed_line, role_line, shirt_tone, out_path):
    palette = PALETTES[shirt_tone]
    ink = palette["ink"]
    accent = palette["accent"]

    img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = 260
    max_w = CANVAS_W - margin * 2

    # Top line: breed callout, condensed bold, all caps
    breed_text = breed_line.upper()
    font1, w1, bbox1 = fit_text_width(draw, breed_text, FONT_CONDENSED, max_w, 340)
    h1 = bbox1[3] - bbox1[1]

    # Divider word
    and_font = load_font(FONT_CONDENSED, 100)
    and_text = "&"

    # Bottom line: role, big and bold
    role_text = role_line.upper()
    font2, w2, bbox2 = fit_text_width(draw, role_text, FONT_BLACK, max_w, 420)
    h2 = bbox2[3] - bbox2[1]

    icon_scale = 2.1
    icon_block_h = 260 * icon_scale

    total_h = h1 + 60 + 120 + 60 + icon_block_h + 60 + h2
    y = (CANVAS_H - total_h) / 2

    # Breed line
    x1 = (CANVAS_W - w1) / 2
    draw.text((x1, y - bbox1[1]), breed_text, font=font1, fill=ink)
    y += h1 + 60

    # Ampersand
    abbox = draw.textbbox((0, 0), and_text, font=and_font)
    aw = abbox[2] - abbox[0]
    draw.text(((CANVAS_W - aw) / 2, y - abbox[1]), and_text, font=and_font, fill=accent)
    y += 120 + 60

    # Icon row: paw print + medical cross
    icon_y = y + icon_block_h / 2
    draw_paw_print(draw, CANVAS_W / 2 - 260, icon_y, icon_scale, ink)
    draw_medical_cross(draw, CANVAS_W / 2 + 260, icon_y, 220, accent)
    y += icon_block_h + 60

    # Role line
    x2 = (CANVAS_W - w2) / 2
    draw.text((x2, y - bbox2[1]), role_text, font=font2, fill=ink)

    img.save(out_path, "PNG")
    print(f"Saved {out_path} ({CANVAS_W}x{CANVAS_H})")


if __name__ == "__main__":
    designs = [
        ("Golden Retriever Mom", "Nurse Life", "black_shirt", "design_01_golden_retriever_nurse.png"),
        ("German Shepherd Dad", "ICU Nurse", "black_shirt", "design_02_german_shepherd_icu.png"),
        ("French Bulldog Mom", "ER Nurse", "white_shirt", "design_03_frenchie_er_nurse.png"),
        ("Labrador Mom", "School Nurse", "white_shirt", "design_04_labrador_school_nurse.png"),
        ("Corgi Mom", "Nurse Life", "black_shirt", "design_05_corgi_nurse.png"),
    ]
    for breed, role, tone, fname in designs:
        generate(breed, role, tone, f"./printify_automation/designs/{fname}")

import io
import numpy as np
from PIL import Image
from collections import Counter


def rgb_to_hsv(rgb):
    """Convert RGB [0-255] to HSV (H:0-360, S:0-100, V:0-100)"""
    r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    delta = max_val - min_val
    
    v = max_val * 100
    
    if max_val == 0:
        s = 0
    else:
        s = (delta / max_val) * 100
    
    if delta == 0:
        h = 0
    elif max_val == r:
        h = ((g - b) / delta) % 6
    elif max_val == g:
        h = (b - r) / delta + 2
    else:
        h = (r - g) / delta + 4
    
    h = h * 60
    if h < 0:
        h += 360
    
    return (h, s, v)


def extract_dominant_colors(image_bytes, num_colors=3, resize_width=150):
    """
    Extract dominant colors from an image using k-means-like approach.
    
    Args:
        image_bytes: bytes of image
        num_colors: number of dominant colors to extract
        resize_width: resize width for faster processing
    
    Returns:
        list of dicts with 'rgb', 'hsv', 'percentage'
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    w, h = img.size
    ratio = resize_width / w
    new_h = int(h * ratio)
    img = img.resize((resize_width, new_h), Image.LANCZOS)
    
    pixels = np.array(img).reshape(-1, 3)
    
    quantized = (pixels // 16) * 16
    quantized = quantized.astype(np.int32)
    
    color_counts = Counter()
    for pixel in quantized:
        color_counts[tuple(pixel)] += 1
    
    total_pixels = len(quantized)
    
    top_colors = color_counts.most_common(num_colors * 10)
    
    selected = []
    for color, count in top_colors:
        if len(selected) >= num_colors:
            break
        
        too_similar = False
        for sel_color, _ in selected:
            dist = np.sqrt(np.sum((np.array(color) - np.array(sel_color)) ** 2))
            if dist < 40:
                too_similar = True
                break
        
        if not too_similar:
            selected.append((color, count))
    
    selected_count = sum(c for _, c in selected)
    
    result = []
    for color, count in selected:
        rgb = tuple(int(v + 8) for v in color)
        hsv = rgb_to_hsv(rgb)
        percentage = (count / total_pixels) * 100
        result.append({
            "rgb": rgb,
            "hsv": hsv,
            "percentage": round(percentage, 2)
        })
    
    result.sort(key=lambda x: x["percentage"], reverse=True)
    
    return result


def compute_color_signature(image_bytes):
    """
    Compute a color signature of the image for matching.
    
    Returns:
        dict with color statistics
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((100, 100), Image.LANCZOS)
    pixels = np.array(img).reshape(-1, 3).astype(np.float32)
    
    avg_rgb = np.mean(pixels, axis=0)
    
    hsv_pixels = np.array([rgb_to_hsv(p) for p in pixels])
    avg_hsv = np.mean(hsv_pixels, axis=0)
    
    saturation_avg = avg_hsv[1]
    brightness_avg = avg_hsv[2]
    
    std_rgb = np.std(pixels, axis=0)
    color_variance = np.mean(std_rgb)
    
    r_channel = pixels[:, 0]
    g_channel = pixels[:, 1]
    b_channel = pixels[:, 2]
    
    rg_ratio = np.mean(r_channel / (g_channel + 1))
    rb_ratio = np.mean(r_channel / (b_channel + 1))
    gb_ratio = np.mean(g_channel / (b_channel + 1))
    
    warmness = (np.mean(r_channel) - np.mean(b_channel)) / 255.0 * 100
    
    dominant_colors = extract_dominant_colors(image_bytes, num_colors=3)
    
    return {
        "avg_rgb": avg_rgb.tolist(),
        "avg_hsv": avg_hsv.tolist(),
        "saturation_avg": saturation_avg,
        "brightness_avg": brightness_avg,
        "color_variance": color_variance,
        "rg_ratio": rg_ratio,
        "rb_ratio": rb_ratio,
        "gb_ratio": gb_ratio,
        "warmness": warmness,
        "dominant_colors": dominant_colors
    }

import numpy as np


FILM_SIGNATURES = {
    "Kodak Portra 400": {
        "warmness": 8,
        "saturation_avg": 35,
        "contrast": 0.95,
        "color_shift": "warm",
        "tone": "soft",
        "red_boost": 1.05,
        "green_boost": 0.98,
        "blue_boost": 0.92,
        "fade": 5,
        "description": "柔和平滑的肤色表现，自然的色彩还原"
    },
    "Fuji Velvia 50": {
        "warmness": -3,
        "saturation_avg": 55,
        "contrast": 1.2,
        "color_shift": "cool",
        "tone": "vibrant",
        "red_boost": 1.1,
        "green_boost": 1.15,
        "blue_boost": 1.2,
        "fade": 0,
        "description": "高饱和度，鲜艳色彩，风景摄影经典"
    },
    "Kodak Gold 200": {
        "warmness": 15,
        "saturation_avg": 42,
        "contrast": 1.0,
        "color_shift": "warm",
        "tone": "classic",
        "red_boost": 1.15,
        "green_boost": 1.0,
        "blue_boost": 0.85,
        "fade": 3,
        "description": "温暖色调，经典家庭胶片感"
    },
    "Ilford HP5": {
        "warmness": 0,
        "saturation_avg": 0,
        "contrast": 1.15,
        "color_shift": "neutral",
        "tone": "monochrome",
        "red_boost": 1.0,
        "green_boost": 1.0,
        "blue_boost": 1.0,
        "fade": 2,
        "description": "经典黑白胶片，丰富的灰度层次"
    },
    "Vintage 80s": {
        "warmness": 12,
        "saturation_avg": 32,
        "contrast": 0.9,
        "color_shift": "warm",
        "tone": "faded",
        "red_boost": 1.2,
        "green_boost": 0.9,
        "blue_boost": 0.75,
        "fade": 15,
        "description": "80年代复古感，褪色青橙色调"
    },
    "CineStill 800T": {
        "warmness": -10,
        "saturation_avg": 40,
        "contrast": 1.1,
        "color_shift": "cool",
        "tone": "cinematic",
        "red_boost": 0.95,
        "green_boost": 0.9,
        "blue_boost": 1.15,
        "fade": 8,
        "description": "电影胶片风格，独特的夜景色调"
    },
    "Ektachrome E100": {
        "warmness": -2,
        "saturation_avg": 50,
        "contrast": 1.15,
        "color_shift": "cool",
        "tone": "bright",
        "red_boost": 1.05,
        "green_boost": 1.1,
        "blue_boost": 1.12,
        "fade": 0,
        "description": "反转片，清透明亮的色彩"
    },
    "Lomo LC-A": {
        "warmness": 10,
        "saturation_avg": 52,
        "contrast": 1.25,
        "color_shift": "warm",
        "tone": "toy",
        "red_boost": 1.25,
        "green_boost": 1.1,
        "blue_boost": 0.9,
        "fade": 5,
        "description": "暗角浓重，色彩饱和的玩具相机感"
    },
    "Fuji Superia 200": {
        "warmness": 5,
        "saturation_avg": 45,
        "contrast": 1.05,
        "color_shift": "neutral",
        "tone": "natural",
        "red_boost": 1.05,
        "green_boost": 1.08,
        "blue_boost": 0.95,
        "fade": 2,
        "description": "富士日常胶片，绿色表现出色"
    },
    "Kodak UltraMax 400": {
        "warmness": 12,
        "saturation_avg": 48,
        "contrast": 1.05,
        "color_shift": "warm",
        "tone": "vivid",
        "red_boost": 1.18,
        "green_boost": 1.02,
        "blue_boost": 0.88,
        "fade": 4,
        "description": "高饱和度全能胶卷，色彩鲜艳"
    },
    "Agfa Vista 200": {
        "warmness": 3,
        "saturation_avg": 40,
        "contrast": 0.95,
        "color_shift": "cool",
        "tone": "muted",
        "red_boost": 0.95,
        "green_boost": 1.05,
        "blue_boost": 1.05,
        "fade": 6,
        "description": "淡雅色彩，青色色调，已停产经典"
    },
    "Fuji Pro 400H": {
        "warmness": 2,
        "saturation_avg": 38,
        "contrast": 1.0,
        "color_shift": "neutral",
        "tone": "professional",
        "red_boost": 1.0,
        "green_boost": 1.08,
        "blue_boost": 1.02,
        "fade": 1,
        "description": "专业人像胶片，柔和自然的肤色"
    }
}


def normalize_value(value, min_val, max_val):
    """Normalize value to 0-1 range"""
    return (value - min_val) / (max_val - min_val)


def compute_similarity(signature, film_sig):
    """
    Compute similarity between image signature and film signature.
    Higher score = more similar (0-100)
    """
    scores = []
    
    warmness_img = signature.get("warmness", 0)
    warmness_film = film_sig.get("warmness", 0)
    warmness_diff = abs(warmness_img - warmness_film)
    warmness_score = max(0, 100 - warmness_diff * 3)
    scores.append(("warmness", warmness_score, 0.3))
    
    sat_img = signature.get("saturation_avg", 40)
    sat_film = film_sig.get("saturation_avg", 40)
    sat_diff = abs(sat_img - sat_film)
    sat_score = max(0, 100 - sat_diff * 2)
    scores.append(("saturation", sat_score, 0.25))
    
    var_img = signature.get("color_variance", 30)
    contrast_film = film_sig.get("contrast", 1.0)
    contrast_score = 100 - abs(var_img / 30 - contrast_film) * 50
    contrast_score = max(0, min(100, contrast_score))
    scores.append(("contrast", contrast_score, 0.15))
    
    avg_rgb = signature.get("avg_rgb", [128, 128, 128])
    r_ratio = avg_rgb[0] / (avg_rgb[2] + 1)
    film_r_ratio = film_sig.get("red_boost", 1.0) / film_sig.get("blue_boost", 1.0)
    ratio_diff = abs(r_ratio - film_r_ratio)
    ratio_score = max(0, 100 - ratio_diff * 80)
    scores.append(("color_balance", ratio_score, 0.15))
    
    fade_film = film_sig.get("fade", 0)
    bright_img = signature.get("brightness_avg", 50)
    fade_score = 100 - abs(bright_img / 50 - (1 - fade_film / 200)) * 50
    fade_score = max(0, min(100, fade_score))
    scores.append(("fade", fade_score, 0.05))
    
    dominant_colors = signature.get("dominant_colors", [])
    dominant_score = 0
    if len(dominant_colors) >= 1:
        main_color = dominant_colors[0]
        main_hue = main_color["hsv"][0]
        main_sat = main_color["hsv"][1]
        
        color_shift = film_sig.get("color_shift", "neutral")
        if color_shift == "warm" and (main_hue < 60 or main_hue > 300):
            dominant_score = 70
        elif color_shift == "cool" and 180 < main_hue < 300:
            dominant_score = 70
        elif color_shift == "neutral":
            dominant_score = 50
        else:
            dominant_score = 30
    
    scores.append(("dominant_hue", dominant_score, 0.1))
    
    total_score = 0
    total_weight = 0
    for name, score, weight in scores:
        total_score += score * weight
        total_weight += weight
    
    final_score = total_score / total_weight if total_weight > 0 else 0
    
    return round(final_score, 1)


def match_films(image_signature, top_n=5):
    """
    Match image signature to film recipes.
    
    Args:
        image_signature: dict from compute_color_signature
        top_n: number of top matches to return
    
    Returns:
        list of dicts with 'name', 'similarity_score', 'description'
    """
    results = []
    
    for film_name, film_sig in FILM_SIGNATURES.items():
        score = compute_similarity(image_signature, film_sig)
        results.append({
            "name": film_name,
            "similarity_score": score,
            "description": film_sig.get("description", ""),
            "film_sig": film_sig
        })
    
    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    
    return results[:top_n]


def get_all_film_signatures():
    return FILM_SIGNATURES

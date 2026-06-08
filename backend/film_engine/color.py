import numpy as np
from PIL import Image


def apply_tone_curve(image_array, r_curve=None, g_curve=None, b_curve=None):
    """
    Apply tone curves to each channel.
    Curve format: list of (x, y) control points, x and y in [0, 255]
    """
    result = image_array.copy()
    
    def build_lut(curve_points):
        if curve_points is None or len(curve_points) < 2:
            return np.arange(256, dtype=np.uint8)
        curve_points = sorted(curve_points, key=lambda p: p[0])
        xs = [p[0] for p in curve_points]
        ys = [p[1] for p in curve_points]
        lut = np.interp(np.arange(256), xs, ys)
        return np.clip(lut, 0, 255).astype(np.uint8)
    
    r_lut = build_lut(r_curve)
    g_lut = build_lut(g_curve)
    b_lut = build_lut(b_curve)
    
    result[..., 0] = r_lut[result[..., 0]]
    result[..., 1] = g_lut[result[..., 1]]
    result[..., 2] = b_lut[result[..., 2]]
    
    return result


def apply_saturation(image_array, saturation):
    """
    Adjust saturation. saturation: 0.0 ~ 2.0+ (1.0 = original)
    """
    gray = np.dot(image_array[..., :3], [0.299, 0.587, 0.114])
    gray = gray[..., np.newaxis]
    result = gray + saturation * (image_array[..., :3] - gray)
    return np.clip(result, 0, 255).astype(np.uint8)


def apply_contrast(image_array, contrast):
    """
    Adjust contrast. contrast: 0.0 ~ 2.0+ (1.0 = original)
    """
    mean = 128.0
    result = mean + contrast * (image_array.astype(np.float32) - mean)
    return np.clip(result, 0, 255).astype(np.uint8)


def apply_brightness(image_array, brightness):
    """
    Adjust brightness. brightness: -100 ~ 100 (0 = original)
    """
    result = image_array.astype(np.float32) + brightness
    return np.clip(result, 0, 255).astype(np.uint8)


def apply_color_temperature(image_array, temperature):
    """
    Adjust color temperature. temperature: -100 ~ 100 (0 = original)
    Positive = warmer (more red/yellow), Negative = cooler (more blue)
    """
    result = image_array.astype(np.float32)
    temp_factor = temperature / 100.0
    
    if temp_factor > 0:
        result[..., 0] = result[..., 0] + temp_factor * 30
        result[..., 1] = result[..., 1] + temp_factor * 15
        result[..., 2] = result[..., 2] - temp_factor * 10
    else:
        result[..., 0] = result[..., 0] + temp_factor * 20
        result[..., 1] = result[..., 1] + temp_factor * 10
        result[..., 2] = result[..., 2] - temp_factor * 25
    
    return np.clip(result, 0, 255).astype(np.uint8)


def apply_vignette(image_array, strength):
    """
    Apply vignette effect. strength: 0 ~ 100
    """
    if strength <= 0:
        return image_array
    
    h, w = image_array.shape[:2]
    y_idx, x_idx = np.ogrid[:h, :w]
    center_y, center_x = h / 2.0, w / 2.0
    
    distance = np.sqrt((x_idx - center_x) ** 2 + (y_idx - center_y) ** 2)
    max_dist = np.sqrt(center_x ** 2 + center_y ** 2)
    normalized_dist = distance / max_dist
    
    vignette = 1.0 - (strength / 100.0) * (normalized_dist ** 2)
    vignette = np.clip(vignette, 0, 1)
    vignette = vignette[..., np.newaxis]
    
    result = image_array.astype(np.float32) * vignette
    return np.clip(result, 0, 255).astype(np.uint8)

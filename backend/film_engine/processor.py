from PIL import Image
import numpy as np
import io

from .color import (
    apply_saturation,
    apply_contrast,
    apply_brightness,
    apply_color_temperature,
    apply_vignette,
    apply_tone_curve
)
from .grain import apply_film_grain, apply_film_scratch


DEFAULT_RECIPE = {
    "name": "Original",
    "saturation": 1.0,
    "contrast": 1.0,
    "brightness": 0,
    "temperature": 0,
    "grain_amount": 0,
    "grain_size": 1.0,
    "vignette": 0,
    "scratch_amount": 0,
    "r_curve": None,
    "g_curve": None,
    "b_curve": None,
    "fade": 0
}


def apply_fade(image_array, fade_amount):
    """
    Apply fade effect (reduce contrast and lift blacks)
    fade_amount: 0 ~ 100
    """
    if fade_amount <= 0:
        return image_array
    
    fade_factor = fade_amount / 100.0
    lift = fade_factor * 30
    result = image_array.astype(np.float32)
    result = lift + (255 - lift) * (result / 255.0)
    return np.clip(result, 0, 255).astype(np.uint8)


def process_image(image_bytes, params):
    """
    Process image with film simulation parameters.
    
    Args:
        image_bytes: bytes of image file
        params: dict of film parameters
    
    Returns:
        bytes of processed JPEG image
    """
    p = {**DEFAULT_RECIPE, **params}
    
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_array = np.array(img)
    
    img_array = apply_brightness(img_array, p["brightness"])
    img_array = apply_contrast(img_array, p["contrast"])
    img_array = apply_saturation(img_array, p["saturation"])
    img_array = apply_color_temperature(img_array, p["temperature"])
    img_array = apply_tone_curve(img_array, p["r_curve"], p["g_curve"], p["b_curve"])
    img_array = apply_fade(img_array, p["fade"])
    img_array = apply_vignette(img_array, p["vignette"])
    img_array = apply_film_grain(img_array, p["grain_amount"], p["grain_size"])
    img_array = apply_film_scratch(img_array, p["scratch_amount"])
    
    result_img = Image.fromarray(img_array)
    output = io.BytesIO()
    result_img.save(output, format="JPEG", quality=92)
    return output.getvalue()


def get_default_params():
    return DEFAULT_RECIPE.copy()

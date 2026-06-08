import numpy as np


def apply_film_grain(image_array, grain_amount, grain_size=1.0):
    """
    Apply film grain effect.
    grain_amount: 0 ~ 100 (intensity)
    grain_size: 0.5 ~ 3.0 (size of grain particles)
    """
    if grain_amount <= 0:
        return image_array
    
    h, w = image_array.shape[:2]
    
    grain_h = int(h / grain_size)
    grain_w = int(w / grain_size)
    
    grain = np.random.normal(0, grain_amount / 100.0 * 30, (grain_h, grain_w, 3))
    
    if grain_size != 1.0:
        from PIL import Image
        grain_img = Image.fromarray(np.clip(grain + 128, 0, 255).astype(np.uint8))
        grain_img = grain_img.resize((w, h), Image.NEAREST)
        grain = (np.array(grain_img).astype(np.float32) - 128)
    else:
        grain = np.clip(grain, -128, 127)
    
    result = image_array.astype(np.float32) + grain
    return np.clip(result, 0, 255).astype(np.uint8)


def apply_film_scratch(image_array, amount=0):
    """
    Apply film scratch/dust effect for vintage feel.
    amount: 0 ~ 100
    """
    if amount <= 0:
        return image_array
    
    h, w = image_array.shape[:2]
    result = image_array.copy()
    
    num_dust = int(amount * 5)
    for _ in range(num_dust):
        x = np.random.randint(0, w)
        y = np.random.randint(0, h)
        size = np.random.randint(1, 3)
        brightness = np.random.randint(200, 255)
        result[y:y+size, x:x+size] = brightness
    
    num_scratches = int(amount / 10)
    for _ in range(num_scratches):
        x1 = np.random.randint(0, w)
        y1 = np.random.randint(0, h)
        length = np.random.randint(20, 100)
        angle = np.random.uniform(-0.3, 0.3)
        x2 = int(x1 + length * np.cos(angle))
        y2 = int(y1 + length * np.sin(angle))
        
        steps = max(abs(x2 - x1), abs(y2 - y1))
        if steps == 0:
            continue
        for i in range(steps):
            t = i / steps
            x = int(x1 + t * (x2 - x1))
            y = int(y1 + t * (y2 - y1))
            if 0 <= x < w and 0 <= y < h:
                result[y, x] = np.clip(result[y, x].astype(np.int32) + 30, 0, 255)
    
    return result

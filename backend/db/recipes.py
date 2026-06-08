import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "film_recipes.db")

PARAM_KEYS = [
    "saturation", "contrast", "brightness", "temperature",
    "grain_amount", "grain_size", "vignette", "scratch_amount",
    "fade", "r_curve", "g_curve", "b_curve"
]


def get_db_path():
    return os.path.abspath(DB_PATH)


def init_db():
    """Initialize database and create tables"""
    db_dir = os.path.dirname(get_db_path())
    os.makedirs(db_dir, exist_ok=True)
    
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT DEFAULT '',
            category TEXT DEFAULT 'custom',
            saturation REAL DEFAULT 1.0,
            contrast REAL DEFAULT 1.0,
            brightness REAL DEFAULT 0,
            temperature REAL DEFAULT 0,
            grain_amount REAL DEFAULT 0,
            grain_size REAL DEFAULT 1.0,
            vignette REAL DEFAULT 0,
            scratch_amount REAL DEFAULT 0,
            fade REAL DEFAULT 0,
            r_curve TEXT DEFAULT NULL,
            g_curve TEXT DEFAULT NULL,
            b_curve TEXT DEFAULT NULL,
            is_builtin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    
    _seed_builtin_recipes()


def _seed_builtin_recipes():
    """Seed built-in film recipes"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM recipes WHERE is_builtin = 1")
    count = cursor.fetchone()[0]
    if count > 0:
        conn.close()
        return
    
    builtin_recipes = [
        {
            "name": "Kodak Portra 400",
            "description": "柔和平滑的肤色表现，自然的色彩还原",
            "category": "portrait",
            "saturation": 0.9,
            "contrast": 0.95,
            "brightness": 5,
            "temperature": 10,
            "grain_amount": 15,
            "grain_size": 1.0,
            "vignette": 10,
            "scratch_amount": 0,
            "fade": 5,
            "r_curve": json.dumps([[0, 10], [128, 130], [255, 250]]),
            "g_curve": json.dumps([[0, 5], [128, 125], [255, 245]]),
            "b_curve": json.dumps([[0, 0], [128, 120], [255, 240]]),
            "is_builtin": 1
        },
        {
            "name": "Fuji Velvia 50",
            "description": "高饱和度，鲜艳色彩，风景摄影经典",
            "category": "landscape",
            "saturation": 1.4,
            "contrast": 1.2,
            "brightness": 0,
            "temperature": -5,
            "grain_amount": 10,
            "grain_size": 0.8,
            "vignette": 15,
            "scratch_amount": 0,
            "fade": 0,
            "r_curve": json.dumps([[0, 0], [64, 70], [192, 195], [255, 255]]),
            "g_curve": json.dumps([[0, 5], [128, 130], [255, 250]]),
            "b_curve": json.dumps([[0, 10], [128, 135], [255, 255]]),
            "is_builtin": 1
        },
        {
            "name": "Kodak Gold 200",
            "description": "温暖色调，经典家庭胶片感",
            "category": "classic",
            "saturation": 1.1,
            "contrast": 1.0,
            "brightness": 8,
            "temperature": 20,
            "grain_amount": 20,
            "grain_size": 1.2,
            "vignette": 8,
            "scratch_amount": 0,
            "fade": 3,
            "r_curve": json.dumps([[0, 15], [128, 135], [255, 250]]),
            "g_curve": json.dumps([[0, 10], [128, 128], [255, 240]]),
            "b_curve": json.dumps([[0, 5], [128, 115], [255, 230]]),
            "is_builtin": 1
        },
        {
            "name": "Ilford HP5",
            "description": "经典黑白胶片，丰富的灰度层次",
            "category": "bw",
            "saturation": 0.0,
            "contrast": 1.15,
            "brightness": 0,
            "temperature": 0,
            "grain_amount": 30,
            "grain_size": 1.5,
            "vignette": 12,
            "scratch_amount": 5,
            "fade": 2,
            "r_curve": None,
            "g_curve": None,
            "b_curve": None,
            "is_builtin": 1
        },
        {
            "name": "Vintage 80s",
            "description": "80年代复古感，褪色青橙色调",
            "category": "vintage",
            "saturation": 0.85,
            "contrast": 0.9,
            "brightness": 3,
            "temperature": 15,
            "grain_amount": 25,
            "grain_size": 1.3,
            "vignette": 20,
            "scratch_amount": 10,
            "fade": 15,
            "r_curve": json.dumps([[0, 20], [64, 75], [128, 140], [192, 200], [255, 240]]),
            "g_curve": json.dumps([[0, 15], [128, 120], [255, 225]]),
            "b_curve": json.dumps([[0, 30], [128, 110], [255, 200]]),
            "is_builtin": 1
        },
        {
            "name": "CineStill 800T",
            "description": "电影胶片风格，独特的夜景色调",
            "category": "cinematic",
            "saturation": 1.05,
            "contrast": 1.1,
            "brightness": -5,
            "temperature": -15,
            "grain_amount": 35,
            "grain_size": 1.4,
            "vignette": 25,
            "scratch_amount": 2,
            "fade": 8,
            "r_curve": json.dumps([[0, 5], [128, 120], [255, 245]]),
            "g_curve": json.dumps([[0, 0], [128, 115], [255, 235]]),
            "b_curve": json.dumps([[0, 15], [128, 140], [255, 255]]),
            "is_builtin": 1
        },
        {
            "name": "Ektachrome E100",
            "description": "反转片，清透明亮的色彩",
            "category": "slide",
            "saturation": 1.25,
            "contrast": 1.15,
            "brightness": 2,
            "temperature": -3,
            "grain_amount": 8,
            "grain_size": 0.7,
            "vignette": 5,
            "scratch_amount": 0,
            "fade": 0,
            "r_curve": json.dumps([[0, 0], [64, 60], [128, 128], [192, 200], [255, 255]]),
            "g_curve": json.dumps([[0, 0], [128, 130], [255, 255]]),
            "b_curve": json.dumps([[0, 5], [128, 132], [255, 252]]),
            "is_builtin": 1
        },
        {
            "name": "Lomo LC-A",
            "description": "暗角浓重，色彩饱和的玩具相机感",
            "category": "toy",
            "saturation": 1.35,
            "contrast": 1.25,
            "brightness": -2,
            "temperature": 12,
            "grain_amount": 40,
            "grain_size": 1.6,
            "vignette": 45,
            "scratch_amount": 8,
            "fade": 5,
            "r_curve": json.dumps([[0, 0], [128, 140], [255, 250]]),
            "g_curve": json.dumps([[0, 5], [128, 135], [255, 245]]),
            "b_curve": json.dumps([[0, 0], [128, 120], [255, 230]]),
            "is_builtin": 1
        }
    ]
    
    for recipe in builtin_recipes:
        try:
            placeholders = ", ".join(["?"] * len(recipe))
            columns = ", ".join(recipe.keys())
            cursor.execute(
                f"INSERT OR IGNORE INTO recipes ({columns}) VALUES ({placeholders})",
                tuple(recipe.values())
            )
        except Exception:
            pass
    
    conn.commit()
    conn.close()


def _row_to_recipe(row):
    """Convert database row to recipe dict"""
    if row is None:
        return None
    
    columns = [
        "id", "name", "description", "category",
        "saturation", "contrast", "brightness", "temperature",
        "grain_amount", "grain_size", "vignette", "scratch_amount",
        "fade", "r_curve", "g_curve", "b_curve",
        "is_builtin", "created_at", "updated_at"
    ]
    
    recipe = dict(zip(columns, row))
    
    for key in ["r_curve", "g_curve", "b_curve"]:
        if recipe[key]:
            recipe[key] = json.loads(recipe[key])
    
    return recipe


def list_recipes(category=None):
    """List all recipes, optionally filtered by category"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    if category:
        cursor.execute("SELECT * FROM recipes WHERE category = ? ORDER BY is_builtin DESC, name", (category,))
    else:
        cursor.execute("SELECT * FROM recipes ORDER BY is_builtin DESC, name")
    
    rows = cursor.fetchall()
    conn.close()
    
    return [_row_to_recipe(row) for row in rows]


def get_recipe(recipe_id):
    """Get a single recipe by ID"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
    row = cursor.fetchone()
    conn.close()
    
    return _row_to_recipe(row)


def get_recipe_by_name(name):
    """Get a single recipe by name"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM recipes WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    
    return _row_to_recipe(row)


def create_recipe(name, params, description="", category="custom"):
    """Create a new custom recipe"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    recipe_data = {
        "name": name,
        "description": description,
        "category": category,
        "is_builtin": 0
    }
    
    for key in PARAM_KEYS:
        if key in params:
            val = params[key]
            if key in ["r_curve", "g_curve", "b_curve"] and val is not None:
                recipe_data[key] = json.dumps(val)
            else:
                recipe_data[key] = val
    
    columns = ", ".join(recipe_data.keys())
    placeholders = ", ".join(["?"] * len(recipe_data))
    
    cursor.execute(
        f"INSERT INTO recipes ({columns}) VALUES ({placeholders})",
        tuple(recipe_data.values())
    )
    
    recipe_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return get_recipe(recipe_id)


def update_recipe(recipe_id, params, name=None, description=None, category=None):
    """Update an existing recipe"""
    recipe = get_recipe(recipe_id)
    if not recipe:
        return None
    
    if recipe["is_builtin"]:
        raise ValueError("Cannot modify built-in recipes")
    
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    updates = []
    values = []
    
    if name is not None:
        updates.append("name = ?")
        values.append(name)
    if description is not None:
        updates.append("description = ?")
        values.append(description)
    if category is not None:
        updates.append("category = ?")
        values.append(category)
    
    for key in PARAM_KEYS:
        if key in params:
            val = params[key]
            updates.append(f"{key} = ?")
            if key in ["r_curve", "g_curve", "b_curve"] and val is not None:
                values.append(json.dumps(val))
            else:
                values.append(val)
    
    updates.append("updated_at = CURRENT_TIMESTAMP")
    values.append(recipe_id)
    
    cursor.execute(
        f"UPDATE recipes SET {', '.join(updates)} WHERE id = ?",
        tuple(values)
    )
    
    conn.commit()
    conn.close()
    
    return get_recipe(recipe_id)


def delete_recipe(recipe_id):
    """Delete a recipe"""
    recipe = get_recipe(recipe_id)
    if not recipe:
        return False
    
    if recipe["is_builtin"]:
        raise ValueError("Cannot delete built-in recipes")
    
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    conn.commit()
    conn.close()
    
    return True


def recipe_to_params(recipe):
    """Extract processing parameters from recipe dict"""
    params = {}
    for key in PARAM_KEYS:
        if key in recipe:
            params[key] = recipe[key]
    return params


def list_categories():
    """List all categories"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT category FROM recipes ORDER BY category")
    rows = cursor.fetchall()
    conn.close()
    
    return [row[0] for row in rows]

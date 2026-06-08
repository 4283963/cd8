from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io
import base64
import traceback
import threading
import time
from functools import wraps

from film_engine import (
    process_image,
    get_default_params,
    extract_dominant_colors,
    compute_color_signature,
    match_films
)
from db import (
    init_db,
    list_recipes,
    get_recipe,
    get_recipe_by_name,
    create_recipe,
    update_recipe,
    delete_recipe,
    recipe_to_params,
    list_categories
)

app = Flask(__name__)
CORS(app, max_age=3600)

init_db()

MAX_CONCURRENT_PROCESS = 2
process_semaphore = threading.Semaphore(MAX_CONCURRENT_PROCESS)
pending_requests = 0
pending_lock = threading.Lock()

PROCESS_TIMEOUT = 30


def limit_concurrency(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        global pending_requests

        with pending_lock:
            if pending_requests >= MAX_CONCURRENT_PROCESS * 3:
                return jsonify({
                    "error": "Server is busy. Please try again later.",
                    "code": "TOO_MANY_REQUESTS"
                }), 429
            pending_requests += 1

        try:
            acquired = process_semaphore.acquire(timeout=PROCESS_TIMEOUT)
            if not acquired:
                return jsonify({
                    "error": "Processing timeout. Server is too busy.",
                    "code": "TIMEOUT"
                }), 503

            try:
                return f(*args, **kwargs)
            finally:
                process_semaphore.release()
        finally:
            with pending_lock:
                pending_requests -= 1

    return decorated


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Film simulation API is running"})


@app.route("/api/recipes", methods=["GET"])
def get_recipes():
    category = request.args.get("category")
    recipes = list_recipes(category)
    return jsonify({"recipes": recipes})


@app.route("/api/recipes/<int:recipe_id>", methods=["GET"])
def get_recipe_detail(recipe_id):
    recipe = get_recipe(recipe_id)
    if not recipe:
        return jsonify({"error": "Recipe not found"}), 404
    return jsonify({"recipe": recipe})


@app.route("/api/recipes", methods=["POST"])
def create_new_recipe():
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "Recipe name is required"}), 400
    
    name = data["name"]
    params = data.get("params", {})
    description = data.get("description", "")
    category = data.get("category", "custom")
    
    try:
        existing = get_recipe_by_name(name)
        if existing:
            return jsonify({"error": "Recipe with this name already exists"}), 400
        
        recipe = create_recipe(name, params, description, category)
        return jsonify({"recipe": recipe}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/recipes/<int:recipe_id>", methods=["PUT"])
def update_existing_recipe(recipe_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    
    try:
        recipe = update_recipe(
            recipe_id,
            params=data.get("params", {}),
            name=data.get("name"),
            description=data.get("description"),
            category=data.get("category")
        )
        if not recipe:
            return jsonify({"error": "Recipe not found"}), 404
        return jsonify({"recipe": recipe})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/recipes/<int:recipe_id>", methods=["DELETE"])
def delete_existing_recipe(recipe_id):
    try:
        result = delete_recipe(recipe_id)
        if not result:
            return jsonify({"error": "Recipe not found"}), 404
        return jsonify({"message": "Recipe deleted successfully"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/categories", methods=["GET"])
def get_categories():
    categories = list_categories()
    return jsonify({"categories": categories})


@app.route("/api/params/default", methods=["GET"])
def get_default():
    return jsonify({"params": get_default_params()})


@app.route("/api/process", methods=["POST"])
@limit_concurrency
def process():
    """
    Process image with film simulation parameters.
    Accepts: multipart form with 'image' file and 'params' (JSON string)
    Returns: processed image as JPEG
    """
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        image_file = request.files["image"]
        if image_file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        
        image_bytes = image_file.read()
        
        import json
        params_str = request.form.get("params", "{}")
        try:
            params = json.loads(params_str) if params_str else {}
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid params JSON"}), 400
        
        recipe_id = request.form.get("recipe_id")
        if recipe_id:
            recipe = get_recipe(int(recipe_id))
            if recipe:
                recipe_params = recipe_to_params(recipe)
                recipe_params.update(params)
                params = recipe_params
        
        result_bytes = process_image(image_bytes, params)
        
        return send_file(
            io.BytesIO(result_bytes),
            mimetype="image/jpeg"
        )
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/process/base64", methods=["POST"])
@limit_concurrency
def process_base64():
    """
    Process image with base64 input/output.
    Accepts: JSON with 'image' (base64 string) and 'params' (dict)
    Returns: JSON with 'image' (base64 processed image)
    """
    try:
        data = request.get_json()
        if not data or "image" not in data:
            return jsonify({"error": "No image data provided"}), 400
        
        image_b64 = data["image"]
        if "," in image_b64:
            image_b64 = image_b64.split(",", 1)[1]
        
        image_bytes = base64.b64decode(image_b64)
        params = data.get("params", {})
        
        recipe_id = data.get("recipe_id")
        if recipe_id:
            recipe = get_recipe(int(recipe_id))
            if recipe:
                recipe_params = recipe_to_params(recipe)
                recipe_params.update(params)
                params = recipe_params
        
        result_bytes = process_image(image_bytes, params)
        result_b64 = base64.b64encode(result_bytes).decode("utf-8")
        
        return jsonify({
            "image": f"data:image/jpeg;base64,{result_b64}"
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/analyze-colors", methods=["POST"])
def analyze_colors():
    """
    Analyze image colors and extract dominant colors.
    Accepts: multipart form with 'image' file
    Returns: color analysis result with dominant colors and signature
    """
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        image_file = request.files["image"]
        if image_file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        
        image_bytes = image_file.read()
        
        dominant_colors = extract_dominant_colors(image_bytes, num_colors=3)
        signature = compute_color_signature(image_bytes)
        
        return jsonify({
            "dominant_colors": dominant_colors,
            "signature": signature
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/analyze-colors/base64", methods=["POST"])
def analyze_colors_base64():
    """
    Analyze image colors with base64 input.
    Accepts: JSON with 'image' (base64 string)
    Returns: color analysis result
    """
    try:
        data = request.get_json()
        if not data or "image" not in data:
            return jsonify({"error": "No image data provided"}), 400
        
        image_b64 = data["image"]
        if "," in image_b64:
            image_b64 = image_b64.split(",", 1)[1]
        
        image_bytes = base64.b64decode(image_b64)
        
        dominant_colors = extract_dominant_colors(image_bytes, num_colors=3)
        signature = compute_color_signature(image_bytes)
        
        return jsonify({
            "dominant_colors": dominant_colors,
            "signature": signature
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/match-film", methods=["POST"])
def match_film():
    """
    Analyze image and match to similar film stock.
    Accepts: multipart form with 'image' file
    Returns: matched films with similarity scores
    """
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        image_file = request.files["image"]
        if image_file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        
        image_bytes = image_file.read()
        
        signature = compute_color_signature(image_bytes)
        dominant_colors = extract_dominant_colors(image_bytes, num_colors=3)
        matches = match_films(signature, top_n=5)
        
        clean_matches = []
        for m in matches:
            clean_matches.append({
                "name": m["name"],
                "similarity_score": m["similarity_score"],
                "description": m["description"]
            })
        
        return jsonify({
            "dominant_colors": dominant_colors,
            "signature": {
                "warmness": round(signature.get("warmness", 0), 2),
                "saturation_avg": round(signature.get("saturation_avg", 0), 2),
                "brightness_avg": round(signature.get("brightness_avg", 0), 2),
                "color_variance": round(signature.get("color_variance", 0), 2)
            },
            "matches": clean_matches
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/match-film/base64", methods=["POST"])
def match_film_base64():
    """
    Analyze image and match film with base64 input.
    Accepts: JSON with 'image' (base64 string)
    Returns: matched films
    """
    try:
        data = request.get_json()
        if not data or "image" not in data:
            return jsonify({"error": "No image data provided"}), 400
        
        image_b64 = data["image"]
        if "," in image_b64:
            image_b64 = image_b64.split(",", 1)[1]
        
        image_bytes = base64.b64decode(image_b64)
        
        signature = compute_color_signature(image_bytes)
        dominant_colors = extract_dominant_colors(image_bytes, num_colors=3)
        matches = match_films(signature, top_n=5)
        
        clean_matches = []
        for m in matches:
            clean_matches.append({
                "name": m["name"],
                "similarity_score": m["similarity_score"],
                "description": m["description"]
            })
        
        return jsonify({
            "dominant_colors": dominant_colors,
            "signature": {
                "warmness": round(signature.get("warmness", 0), 2),
                "saturation_avg": round(signature.get("saturation_avg", 0), 2),
                "brightness_avg": round(signature.get("brightness_avg", 0), 2),
                "color_variance": round(signature.get("color_variance", 0), 2)
            },
            "matches": clean_matches
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

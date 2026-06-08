from .processor import process_image, get_default_params, DEFAULT_RECIPE
from .color_analyzer import extract_dominant_colors, compute_color_signature
from .film_matcher import match_films, get_all_film_signatures

__all__ = [
    "process_image",
    "get_default_params",
    "DEFAULT_RECIPE",
    "extract_dominant_colors",
    "compute_color_signature",
    "match_films",
    "get_all_film_signatures"
]

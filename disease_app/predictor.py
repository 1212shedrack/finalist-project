"""
predictor.py — TFLite model loader and inference engine.

VERIFIED WORKING PREPROCESSING (from existing disease_app/views.py):
    img = tf.keras.utils.load_img(image_path, target_size=(224, 224))
    img = tf.keras.utils.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = img.astype(np.float32)
    # NO division by 255 — the model handles normalization internally

CLASS ORDER (alphabetical folder names from training):
    0 → health
    1 → non_amaranthus
    2 → spot_leaf
    3 → white_rust
"""

import os
import json
import logging
import numpy as np
from ai_edge_litert.interpreter import Interpreter
from django.conf import settings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
logger = logging.getLogger(__name__)

# ── Class configuration ───────────────────────────────────────────────────────
CLASS_NAMES = ['health', 'non_amaranthus', 'spot_leaf', 'white_rust']

DISPLAY_NAMES = {
    'health':          'Healthy',
    'non_amaranthus':  'Non-Amaranthus',
    'spot_leaf':       'Leaf Spot',
    'white_rust':      'White Rust',
}

RISK_CONFIG = {
    'health':         {'level': 'Low',     'color': 'success'},
    'non_amaranthus': {'level': 'Unknown', 'color': 'secondary'},
    'spot_leaf':      {'level': 'Medium',  'color': 'warning'},
    'white_rust':     {'level': 'High',    'color': 'danger'},
}

IMAGE_SIZE = (224, 224)

# ── Global interpreter ────────────────────────────────────────────────────────
_interpreter = None
_model_loaded = False
_model_error = None


def _load_model():
    global _interpreter, _model_loaded, _model_error
    model_path = str(settings.TFLITE_MODEL_PATH)

    if not os.path.exists(model_path):
        _model_error = f'Model file not found: {model_path}'
        logger.error(_model_error)
        return

    try:
        _interpreter = Interpreter(model_path=model_path, num_threads=4)
        _interpreter.allocate_tensors()
        _model_loaded = True
        out_shape = _interpreter.get_output_details()[0]['shape']
        logger.info('TFLite model loaded. Output shape: %s', out_shape)
    except Exception as exc:
        _model_error = str(exc)
        logger.error('Failed to load model: %s', exc)


# Load once at startup
_load_model()


def predict_image(image_path: str) -> dict:
    """
    Run inference on an image file.

    Args:
        image_path: Absolute path to the saved image file.

    Returns:
        dict with keys: predicted_class, display_name, confidence,
                        probabilities, risk_level, risk_color
    """
    if not _model_loaded:
        raise RuntimeError(f'Model not available: {_model_error}')

    # ── Preprocess — matches the original working code exactly ────────────────
    img       = tf.keras.utils.load_img(image_path, target_size=IMAGE_SIZE)
    img_array = tf.keras.utils.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0).astype(np.float32)
    # NOTE: NO /255 normalization — the model applies preprocessing internally

    # ── Inference ─────────────────────────────────────────────────────────────
    inp_details = _interpreter.get_input_details()[0]
    out_details = _interpreter.get_output_details()[0]

    _interpreter.set_tensor(inp_details['index'], img_array)
    _interpreter.invoke()

    scores = _interpreter.get_tensor(out_details['index']).flatten().tolist()

    # ── Build result ──────────────────────────────────────────────────────────
    predicted_idx   = int(np.argmax(scores))
    predicted_class = CLASS_NAMES[predicted_idx]
    confidence      = round(float(scores[predicted_idx]) * 100, 2)

    prob_dict = {
        CLASS_NAMES[i]: round(float(scores[i]) * 100, 2)
        for i in range(len(CLASS_NAMES))
    }

    risk    = RISK_CONFIG.get(predicted_class, {'level': 'Unknown', 'color': 'secondary'})
    display = DISPLAY_NAMES.get(predicted_class, predicted_class)

    logger.info('Prediction: %s (%.1f%%)', display, confidence)

    return {
        'predicted_class': predicted_class,
        'display_name':    display,
        'confidence':      confidence,
        'probabilities':   prob_dict,
        'risk_level':      risk['level'],
        'risk_color':      risk['color'],
    }


# ── Language-specific recommendations map ────────────────────────────────────
# Maps language code → recommendations JSON filename
# Falls back to English (recommendations.json) for any unrecognised language.
RECOMMENDATIONS_FILES = {
    'en': 'recommendations.json',
    'sw': 'recommendations_sw.json',
    'fr': 'recommendations_fr.json',
}


def load_recommendation(predicted_class: str, lang: str = 'en') -> dict:
    """
    Load recommendation dict from the correct language JSON file.

    Args:
        predicted_class: One of health | spot_leaf | white_rust | non_amaranthus
        lang:            Language code — 'en', 'sw', or 'fr' (default 'en')

    Returns:
        dict with title, summary, risk_level, treatment, prevention …
        Falls back to English if the language file is missing.
    """
    base_dir = settings.RECOMMENDATIONS_PATH.parent   # same folder as recommendations.json

    # Resolve filename; fall back to English if language not in map
    filename = RECOMMENDATIONS_FILES.get(lang, RECOMMENDATIONS_FILES['en'])
    file_path = base_dir / filename

    # If language file doesn't exist yet, fall back to English
    if not file_path.exists():
        logger.warning('Recommendations file not found for lang=%s, falling back to English', lang)
        file_path = base_dir / RECOMMENDATIONS_FILES['en']

    try:
        with open(str(file_path), 'r', encoding='utf-8') as f:
            recs = json.load(f)
        rec = recs.get(predicted_class, {})
        if not rec:
            logger.warning('No recommendation for class: %s in lang: %s', predicted_class, lang)
        return rec
    except FileNotFoundError:
        logger.error('Recommendations file not found: %s', file_path)
        return {}
    except json.JSONDecodeError as exc:
        logger.error('Invalid JSON in %s: %s', filename, exc)
        return {}


def get_model_status() -> dict:
    """Return model load status for about/debug pages."""
    return {
        'loaded':     _model_loaded,
        'error':      _model_error,
        'model_path': str(settings.TFLITE_MODEL_PATH),
        'classes':    CLASS_NAMES,
    }

import os
import json
import numpy as np
import tensorflow as tf

from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage


# =========================
# BASE DIR
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# =========================
# LOAD MODEL
# =========================
MODEL_PATH = os.path.join(
    BASE_DIR,
    'model',
    'amaranthus_efficientnet(5).tflite'
)

interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

CLASS_NAMES = ['health', 'non_amaranthus', 'spot_leaf', 'white_rust']


# =========================
# LOAD RECOMMENDATIONS
# =========================
RECOMMENDATION_PATH = os.path.join(
    BASE_DIR,
    'recommendations.json'
)

with open(RECOMMENDATION_PATH, 'r') as file:
    RECOMMENDATIONS = json.load(file)


# =========================
# PREPROCESS IMAGE (SAFE)
# =========================
def preprocess_image(image_path):

    try:
        img = tf.keras.utils.load_img(
            image_path,
            target_size=(224, 224)
        )
    except Exception:
        raise ValueError("Invalid image file uploaded")

    img = tf.keras.utils.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = img.astype(np.float32)

    return img


# =========================
# PREDICT FUNCTION
# =========================
def predict(image_path):

    img = preprocess_image(image_path)

    interpreter.set_tensor(
        input_details[0]['index'],
        img
    )

    interpreter.invoke()

    output = interpreter.get_tensor(
        output_details[0]['index']
    )

    predictions = np.squeeze(output)

    predicted_index = int(np.argmax(predictions))
    predicted_class = CLASS_NAMES[predicted_index]
    confidence = float(predictions[predicted_index]) * 100

    return predicted_class, confidence


# =========================
# MAIN VIEW (FIXED PRG PATTERN)
# =========================
def index(request):

    # -------------------------
    # POST REQUEST (UPLOAD)
    # -------------------------
    if request.method == 'POST' and request.FILES.get('image'):

        image = request.FILES['image']

        # safety check
        if not image.content_type.startswith("image"):
            return render(request, 'index.html', {
                "error": "Please upload a valid image file."
            })

        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        file_path = fs.path(filename)

        try:
            pred_class, confidence = predict(file_path)
        except Exception:
            return render(request, 'index.html', {
                "error": "Failed to process image. Please try another image."
            })

        recommendation = RECOMMENDATIONS.get(pred_class, {})

        # store in session (prevents refresh reprocessing bug)
        request.session['result'] = {
            "prediction": pred_class,
            "confidence": confidence,
            "image_url": fs.url(filename),
            "recommendation": recommendation
        }

        return redirect('index')


    # -------------------------
    # GET REQUEST (DISPLAY RESULT)
    # -------------------------
    result = request.session.pop('result', None)

    return render(request, 'index.html', result or {})
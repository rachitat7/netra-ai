
import os
import numpy as np
import tensorflow as tf

from PIL import Image

# --------------------------------------------------
# MODEL CONFIGURATION
# --------------------------------------------------

APP_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    APP_DIR,
    "netra_mobilenetv2.keras"
)

# Load model once and reuse it
_model = None


def load_model():

    global _model

    if _model is None:

        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                "Netra AI trained model was not found."
            )

        _model = tf.keras.models.load_model(MODEL_PATH)

    return _model


# --------------------------------------------------
# IMAGE PREPROCESSING
# --------------------------------------------------

def preprocess_eye_image(image_path):

    image = Image.open(image_path).convert("RGB")

    image = image.resize((224, 224))

    image_array = np.array(image, dtype=np.float32)

    image_array = tf.keras.applications.mobilenet_v2.preprocess_input(
        image_array
    )

    image_array = np.expand_dims(image_array, axis=0)

    return image_array


# --------------------------------------------------
# AI PREDICTION
# --------------------------------------------------

def predict_image(image_path):

    model = load_model()

    processed_image = preprocess_eye_image(image_path)

    prediction = model.predict(
        processed_image,
        verbose=0
    )

    # Training class mapping:
    # blepharitis = 0
    # normal = 1

    normal_score = float(prediction[0][0])

    if normal_score >= 0.5:

        predicted_class = "Normal"

        model_score = normal_score

    else:

        predicted_class = "Blepharitis"

        model_score = 1 - normal_score

    return {
        "status": "Experimental model output",
        "predicted_class": predicted_class,
        "model_score": round(model_score * 100, 2),
        "message": (
            "Experimental image classification only. "
            "This result is not a medical diagnosis."
        )
    }

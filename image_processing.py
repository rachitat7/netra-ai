
from PIL import Image
import numpy as np
import cv2


def prepare_image(image):

    # Convert image into RGB format
    image = image.convert("RGB")

    # Save original dimensions
    original_size = image.size

    # Resize image for model input
    resized_image = image.resize((224, 224))

    return resized_image, original_size


def check_image_quality(image):

    # Convert image into a NumPy array
    image_array = np.array(image)

    # Convert RGB image into grayscale
    gray_image = cv2.cvtColor(
        image_array,
        cv2.COLOR_RGB2GRAY
    )

    height, width = gray_image.shape

    messages = []

    # Check image dimensions
    if width < 224 or height < 224:
        messages.append("Image resolution is low.")
    else:
        messages.append("Image dimensions meet the basic size check.")

    # Check brightness
    brightness = np.mean(gray_image)

    if brightness < 40:
        messages.append("Image may be too dark.")
    elif brightness > 220:
        messages.append("Image may be overexposed.")
    else:
        messages.append("Brightness is within the basic check range.")

    # Estimate blur using Laplacian variance
    blur_score = cv2.Laplacian(
        gray_image,
        cv2.CV_64F
    ).var()

    if blur_score < 50:
        messages.append("Image may be blurry.")
    else:
        messages.append("No obvious blur detected by the basic check.")

    # These are heuristic checks, not validated clinical thresholds.
    issues = (
        width < 224
        or height < 224
        or brightness < 40
        or brightness > 220
        or blur_score < 50
    )

    status = "Review required" if issues else "Basic checks passed"

    return {
        "status": status,
        "messages": messages,
        "brightness": round(float(brightness), 2),
        "blur_score": round(float(blur_score), 2)
    }

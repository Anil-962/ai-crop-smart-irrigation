import base64

from app.utils.errors import ValidationError


def decode_base64_image(image_base64: str) -> bytes:
    if not image_base64:
        raise ValidationError("image_base64 must not be empty.")
    try:
        if "," in image_base64:
            image_base64 = image_base64.split(",", 1)[1]
        return base64.b64decode(image_base64, validate=True)
    except Exception as err:
        raise ValidationError(f"Invalid base64 image payload: {err}") from err


def extract_image_bytes(req) -> bytes:
    if req.files and "image" in req.files:
        image_file = req.files["image"]
        data = image_file.read()
        if not data:
            raise ValidationError("Uploaded image file is empty.")
        return data

    payload = req.get_json(silent=True) or {}
    image_base64 = payload.get("image_base64")
    if not image_base64:
        raise ValidationError("image_base64 is required for JSON requests.")
    return decode_base64_image(image_base64)

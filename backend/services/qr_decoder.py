"""QR code decoder for photos."""

import io
from PIL import Image, ImageOps, ImageEnhance
from pyzbar.pyzbar import decode
from typing import Optional


def decode_qr_from_bytes(image_bytes: bytes) -> Optional[str]:
    """Decode QR code from image bytes. Handles colored QR codes."""
    try:
        image = Image.open(io.BytesIO(image_bytes))

        # Try original image first
        result = _try_decode(image)
        if result:
            return result

        # Convert to grayscale and try again
        grayscale = ImageOps.grayscale(image)
        result = _try_decode(grayscale)
        if result:
            return result

        # Try with increased contrast
        enhancer = ImageEnhance.Contrast(grayscale)
        high_contrast = enhancer.enhance(2.0)
        result = _try_decode(high_contrast)
        if result:
            return result

        # Try inverted (for light QR on dark background)
        inverted = ImageOps.invert(grayscale)
        result = _try_decode(inverted)
        if result:
            return result

        # Try binary threshold
        threshold = grayscale.point(lambda x: 255 if x > 128 else 0)
        result = _try_decode(threshold)
        if result:
            return result

        return None
    except Exception as e:
        print(f"QR decode error: {e}")
        return None


def _try_decode(image: Image.Image) -> Optional[str]:
    """Try to decode QR from image."""
    decoded_objects = decode(image)
    if decoded_objects:
        return decoded_objects[0].data.decode('utf-8')
    return None

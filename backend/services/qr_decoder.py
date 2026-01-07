"""QR code decoder for photos."""

import io
from PIL import Image
from pyzbar.pyzbar import decode
from typing import Optional


def decode_qr_from_bytes(image_bytes: bytes) -> Optional[str]:
    """Decode QR code from image bytes."""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        decoded_objects = decode(image)

        if decoded_objects:
            # Return the first QR code found
            return decoded_objects[0].data.decode('utf-8')
        return None
    except Exception as e:
        print(f"QR decode error: {e}")
        return None

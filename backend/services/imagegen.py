"""Image generation service using OpenRouter."""

import httpx
import base64
from typing import Optional

from config.settings import settings


async def upload_to_catbox(image_data: bytes) -> Optional[str]:
    """Upload image to catbox.moe and return URL."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://catbox.moe/user/api.php",
                data={"reqtype": "fileupload"},
                files={"fileToUpload": ("image.png", image_data, "image/png")}
            )
            if response.status_code == 200:
                url = response.text.strip()
                if url.startswith("https://"):
                    return url
    except Exception as e:
        print(f"Catbox upload error: {e}")
    return None


async def generate_image(prompt: str) -> Optional[str]:
    """
    Generate image using OpenRouter's FLUX model.
    Returns the image data URL (base64) or None if failed.
    """
    if not settings.openrouter_api_key:
        return None

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openrouter_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "black-forest-labs/flux.2-klein-4b",
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "modalities": ["image", "text"],
                }
            )

            print(f"OpenRouter response: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                choices = data.get("choices", [])
                if choices:
                    message = choices[0].get("message", {})

                    # images are in message.images array
                    images = message.get("images", [])
                    data_url = None

                    if images:
                        img = images[0]
                        if isinstance(img, dict):
                            data_url = img.get("image_url", {}).get("url")

                    # fallback: check content
                    if not data_url:
                        content = message.get("content")
                        if isinstance(content, str) and content.startswith("data:image"):
                            data_url = content

                    # upload base64 to catbox
                    if data_url and data_url.startswith("data:image"):
                        # extract base64 data
                        base64_data = data_url.split(",", 1)[1] if "," in data_url else data_url
                        image_bytes = base64.b64decode(base64_data)
                        hosted_url = await upload_to_catbox(image_bytes)
                        if hosted_url:
                            return hosted_url

            print(f"OpenRouter error response: {response.text}")
            return None
    except Exception as e:
        print(f"Image generation error: {e}")
        return None

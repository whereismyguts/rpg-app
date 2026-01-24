"""Image generation service using OpenRouter."""

import httpx
from typing import Optional

from config.settings import settings


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
                    if images:
                        img = images[0]
                        if isinstance(img, dict):
                            url = img.get("image_url", {}).get("url")
                            if url:
                                return url

                    # fallback: check content
                    content = message.get("content")
                    if isinstance(content, str) and content.startswith("data:image"):
                        return content

            print(f"OpenRouter error response: {response.text}")
            return None
    except Exception as e:
        print(f"Image generation error: {e}")
        return None

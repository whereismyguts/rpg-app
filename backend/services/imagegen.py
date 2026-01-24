"""Image generation service using OpenRouter."""

import httpx
from typing import Optional

from config.settings import settings


async def generate_image(prompt: str) -> Optional[str]:
    """
    Generate image using OpenRouter's FLUX model.
    Returns the image URL or None if failed.
    """
    if not settings.openrouter_api_key:
        return None

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/images/generations",
                headers={
                    "Authorization": f"Bearer {settings.openrouter_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "black-forest-labs/flux-1.1-pro",
                    "prompt": prompt,
                    "n": 1,
                    "size": "512x512",
                }
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("data") and len(data["data"]) > 0:
                    return data["data"][0].get("url")

            return None
    except Exception as e:
        print(f"Image generation error: {e}")
        return None

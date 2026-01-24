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
                # extract image from response
                choices = data.get("choices", [])
                if choices:
                    message = choices[0].get("message", {})
                    content = message.get("content")

                    # content can be string (data URL) or list
                    if isinstance(content, str) and content.startswith("data:image"):
                        return content
                    elif isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get("type") == "image_url":
                                url = item.get("image_url", {}).get("url")
                                if url:
                                    return url

            print(f"OpenRouter error response: {response.text}")
            return None
    except Exception as e:
        print(f"Image generation error: {e}")
        return None

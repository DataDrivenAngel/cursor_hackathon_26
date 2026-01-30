"""
MiniMax Image Generation Service.
Generates AI images for events using the MiniMax API.
"""
import base64
import httpx
from typing import Optional
from app.config import settings


async def generate_event_image(
    event_title: str,
    event_topic: Optional[str] = None,
    event_description: Optional[str] = None
) -> Optional[str]:
    """
    Generate an event image using MiniMax API.
    
    Args:
        event_title: The title of the event
        event_topic: The topic/theme of the event
        event_description: A description of the event
        
    Returns:
        URL of the generated image, or None if generation failed
    """
    if not settings.MINIMAX_API_KEY:
        return None
    
    try:
        # Build a detailed prompt for the image
        prompt_parts = [f"Event: {event_title}"]
        
        if event_topic:
            prompt_parts.append(f"Theme/Topic: {event_topic}")
        
        if event_description:
            prompt_parts.append(f"Description: {event_description}")
        
        # Add style guidance
        prompt_parts.append("Style: Modern, professional, vibrant, promotional banner style")
        prompt_parts.append("Quality: High quality, photorealistic, well-lit")
        
        prompt = ", ".join(prompt_parts)
        
        # Make API request
        url = "https://api.minimax.io/v1/image_generation"
        
        headers = {
            "Authorization": f"Bearer {settings.MINIMAX_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "image-01",
            "prompt": prompt,
            "aspect_ratio": "16:9",
            "response_format": "base64",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
                timeout=60.0
            )
            
            if response.status_code == 200:
                data = response.json()
                images = data.get("data", {}).get("image_base64", [])
                
                if images:
                    # Decode the first image
                    image_data = base64.b64decode(images[0])
                    
                    # In a real implementation, you would upload this to cloud storage
                    # For now, we'll return a placeholder URL
                    # The image data could be saved to a file or cloud storage
                    return f"data:image/jpeg;base64,{images[0]}"
            
            return None
            
    except Exception as e:
        print(f"Error generating image with MiniMax: {e}")
        return None


def generate_image_prompt(event_title: str, topic: str = None) -> str:
    """
    Generate a detailed prompt for event image generation.
    
    Args:
        event_title: The title of the event
        topic: The topic/theme of the event
        
    Returns:
        A detailed prompt for image generation
    """
    prompt = f"Professional event promotional image for: {event_title}"
    
    if topic:
        prompt += f", focused on {topic}"
    
    prompt += """,
    vibrant colors, modern design, suitable for social media and promotional materials,
    high quality, well-composed, engaging visual,
    16:9 aspect ratio, photorealistic, professional lighting"""
    
    return prompt

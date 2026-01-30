"""
MiniMax Image Generation Service via Replicate.
Generates AI images for events using the MiniMax model through Replicate API.
"""
import os
from typing import Optional
from app.config import settings


async def generate_event_image(
    event_title: str,
    event_topic: Optional[str] = None,
    event_description: Optional[str] = None
) -> Optional[str]:
    """
    Generate an event image using MiniMax via Replicate API.
    
    Args:
        event_title: The title of the event
        event_topic: The topic/theme of the event
        event_description: A description of the event
        
    Returns:
        URL of the generated image, or None if generation failed
    """
    # Check for Replicate API token in environment or settings
    api_token = os.getenv("REPLICATE_API_TOKEN") or settings.REPLICATE_API_KEY
    
    if not api_token:
        print("Replicate API token not configured. Set REPLICATE_API_TOKEN in .env")
        return None
    
    try:
        import replicate
        
        # Configure Replicate
        os.environ["REPLICATE_API_TOKEN"] = api_token
        
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
        
        # Run the MiniMax Image-01 model through Replicate
        output = replicate.run(
            "minimax/image-01",
            input={
                "prompt": prompt,
                "aspect_ratio": "16:9",
                "number_of_images": 1,
                "prompt_optimizer": True
            }
        )
        
        if output and len(output) > 0:
            # Get the image URL from the output
            image_url = output[0].url if hasattr(output[0], 'url') else str(output[0])
            
            # If it's a file-like object, read it
            if hasattr(output[0], 'read'):
                image_data = output[0].read()
                # Return as base64 data URL
                import base64
                return f"data:image/png;base64,{base64.b64encode(image_data).decode()}"
            
            # Otherwise return the URL directly
            return image_url
        
        return None
        
    except ImportError:
        print("Replicate package not installed. Run: pip install replicate")
        return None
    except Exception as e:
        print(f"Error generating image with Replicate: {e}")
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

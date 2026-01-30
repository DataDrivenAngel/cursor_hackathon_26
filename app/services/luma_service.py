"""
Luma API integration service.
"""
import httpx
from app.config import settings


LUMA_API_BASE = "https://api.lu.ma/v1"


async def create_luma_event(event) -> str:
    """
    Create an event on Luma.
    
    Returns the Luma event ID.
    """
    if not settings.LUMA_API_KEY:
        # Return a placeholder if no API key configured
        return f"luma_{hash(event.title) % 100000}"
    
    url = f"{LUMA_API_BASE}/events"
    
    event_data = {
        "name": event.title,
        "description": event.description or "",
        "start_at": event.scheduled_date.isoformat() if event.scheduled_date else None,
        "status": "draft"
    }
    
    headers = {
        "Authorization": f"Bearer {settings.LUMA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=event_data, headers=headers)
        
        if response.status_code == 201:
            return response.json().get("id")
        elif response.status_code == 401:
            raise Exception("Invalid Luma API key")
        else:
            raise Exception(f"Luma API error: {response.text}")


async def sync_luma_status(luma_id: str) -> dict:
    """Get event status from Luma."""
    if not settings.LUMA_API_KEY:
        return {"status": "unknown", "message": "API key not configured"}
    
    url = f"{LUMA_API_BASE}/events/{luma_id}"
    
    headers = {
        "Authorization": f"Bearer {settings.LUMA_API_KEY}"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "status": data.get("status", "unknown"),
                "name": data.get("name"),
                "start_at": data.get("start_at"),
                "end_at": data.get("end_at"),
                "guest_count": data.get("guest_count", 0)
            }
        elif response.status_code == 404:
            return {"status": "not_found"}
        else:
            raise Exception(f"Luma API error: {response.text}")


async def get_luma_events() -> list:
    """Get events from Luma."""
    if not settings.LUMA_API_KEY:
        return []
    
    url = f"{LUMA_API_BASE}/events"
    
    headers = {
        "Authorization": f"Bearer {settings.LUMA_API_KEY}"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json().get("items", [])
        else:
            return []

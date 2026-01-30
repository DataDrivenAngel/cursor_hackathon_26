"""
Meetup API integration service.
"""
import httpx
from app.config import settings


MEETUP_API_BASE = "https://api.meetup.com/v3"


async def create_meetup_event(event) -> str:
    """
    Create an event on Meetup.
    
    Returns the Meetup event ID.
    """
    if not settings.MEETUP_API_KEY:
        # Return a placeholder if no API key configured
        return f"meetup_{hash(event.title) % 100000}"
    
    url = f"{MEETUP_API_BASE}/groups/{settings.MEETUP_GROUP_URL}/events"
    
    event_data = {
        "name": event.title,
        "description": event.description or "",
        "time": int(event.scheduled_date.timestamp() * 1000) if event.scheduled_date else None,
        "venue_visibility": "public",
        "publish_status": "draft"
    }
    
    headers = {
        "Authorization": f"Bearer {settings.MEETUP_API_KEY}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=event_data, headers=headers)
        
        if response.status_code == 201:
            return response.json().get("id")
        elif response.status_code == 401:
            raise Exception("Invalid Meetup API key")
        else:
            raise Exception(f"Meetup API error: {response.text}")


async def sync_meetup_status(meetup_id: str) -> dict:
    """Get event status from Meetup."""
    if not settings.MEETUP_API_KEY:
        return {"status": "unknown", "message": "API key not configured"}
    
    url = f"{MEETUP_API_BASE}/events/{meetup_id}"
    
    headers = {
        "Authorization": f"Bearer {settings.MEETUP_API_KEY}"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "status": data.get("status", "unknown"),
                "name": data.get("name"),
                "time": data.get("time"),
                "venue": data.get("venue"),
                "yes_rsvp_count": data.get("yes_rsvp_count", 0)
            }
        elif response.status_code == 404:
            return {"status": "not_found"}
        else:
            raise Exception(f"Meetup API error: {response.text}")


async def get_meetup_events(group_urlname: str = None) -> list:
    """Get events from Meetup for a group."""
    if not settings.MEETUP_API_KEY:
        return []
    
    url = f"{MEETUP_API_BASE}/groups/{group_urlname or settings.MEETUP_GROUP_URL}/events"
    
    headers = {
        "Authorization": f"Bearer {settings.MEETUP_API_KEY}"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json().get("events", [])
        else:
            return []

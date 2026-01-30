"""
Venue research agent - searches for venues using Perplexity and local database.
"""
import httpx
import json
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config import settings
from app.agents.base_agent import BaseAgent, Tool


class VenueResearchAgent(BaseAgent):
    """Agent for researching and finding suitable venues."""
    
    def __init__(self, api_key: str = None):
        super().__init__(api_key)
    
    def get_available_tools(self) -> List[Tool]:
        """Return tools available for venue research."""
        return [
            Tool(
                name="search_existing_venues",
                description="Search for venues in the local database",
                parameters={
                    "type": "object",
                    "properties": {
                        "capacity": {"type": "integer", "description": "Minimum capacity required"},
                        "city": {"type": "string", "description": "City to search in"},
                        "amenities": {"type": "array", "items": {"type": "string"}, "description": "Required amenities"}
                    }
                }
            ),
            Tool(
                name="perplexity_search",
                description="Search the web for venues using Perplexity API",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query for venues"}
                    }
                }
            ),
            Tool(
                name="save_venue",
                description="Save a new venue to the database",
                parameters={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Venue name"},
                        "address": {"type": "string", "description": "Full address"},
                        "city": {"type": "string", "description": "City"},
                        "capacity": {"type": "integer", "description": "Maximum capacity"},
                        "amenities": {"type": "array", "items": {"type": "string"}, "description": "List of amenities"},
                        "website": {"type": "string", "description": "Venue website"},
                        "contact_email": {"type": "string", "description": "Contact email"}
                    }
                }
            ),
            Tool(
                name="summarize_findings",
                description="Generate a summary of venue research findings",
                parameters={
                    "type": "object",
                    "properties": {
                        "existing_venues": {"type": "array", "description": "Existing venues found"},
                        "new_venues": {"type": "array", "description": "New venues from web search"}
                    }
                }
            )
        ]
    
    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute venue research workflow."""
        # This is a simplified version - in production, you would use
        # an LLM with tool calling capabilities
        pass


async def research_venues(
    capacity: Optional[int] = None,
    location: str = None,
    amenities: List[str] = None,
    event_type: str = None
) -> Dict[str, Any]:
    """
    Research venues based on requirements.
    
    This function:
    1. Searches existing venues in the database
    2. Uses Perplexity to find additional venues if needed
    3. Returns research results with recommendations
    """
    results = {
        "existing_venues": [],
        "new_venues": [],
        "recommendations": []
    }
    
    # Search existing venues
    if location:
        query = "SELECT * FROM venues WHERE city LIKE :city"
        params = {"city": f"%{location}%"}
        
        # In a real implementation, you would execute this query
        # For now, we'll simulate the search
        existing = await search_local_venues(location, capacity, amenities)
        results["existing_venues"] = existing
    
    # If we don't have enough venues, search the web
    if len(results["existing_venues"]) < 3 and settings.PERPLEXITY_API_KEY:
        new_venues = await perplexity_search_venues(
            capacity=capacity,
            location=location,
            event_type=event_type,
            amenities=amenities
        )
        results["new_venues"] = new_venues
    
    # Generate recommendations
    results["recommendations"] = generate_venue_recommendations(
        results["existing_venues"],
        results["new_venues"]
    )
    
    return results


async def search_local_venues(
    city: str,
    capacity: Optional[int] = None,
    amenities: List[str] = None
) -> List[Dict[str, Any]]:
    """Search for venues in the local database."""
    # This would query the database in a real implementation
    # For now, return empty list as placeholder
    return []


async def perplexity_search_venues(
    capacity: Optional[int] = None,
    location: str = None,
    event_type: str = None,
    amenities: List[str] = None
) -> List[Dict[str, Any]]:
    """Search for venues using Perplexity API."""
    if not settings.PERPLEXITY_API_KEY:
        return []
    
    # Build search query
    query_parts = []
    if event_type:
        query_parts.append(f"{event_type} event")
    query_parts.append(f"venue in {location}")
    if capacity:
        query_parts.append(f"capacity {capacity}+")
    if amenities:
        query_parts.append(f"amenities: {', '.join(amenities)}")
    
    query = " ".join(query_parts)
    
    headers = {
        "Authorization": f"Bearer {settings.PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "user",
                "content": f"Find venues for {query}. Return results as JSON array with: name, address, city, capacity, amenities, website, contact_email, pricing"
            }
        ]
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.perplexity.ai/chat/completions",
            json=payload,
            headers=headers,
            timeout=60.0
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            # Parse JSON from response
            try:
                # Try to extract JSON from the response
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                venues = json.loads(content)
                if isinstance(venues, list):
                    return venues
                elif isinstance(venues, dict) and "venues" in venues:
                    return venues["venues"]
            except json.JSONDecodeError:
                # If parsing fails, return empty list
                return []
        
        return []


def generate_venue_recommendations(
    existing: List[Dict],
    new: List[Dict]
) -> List[Dict[str, Any]]:
    """Generate venue recommendations based on research."""
    recommendations = []
    
    # Recommend existing venues first (lower cost, known quality)
    for venue in existing[:3]:
        recommendations.append({
            "venue": venue,
            "reason": "Known venue - lower risk",
            "priority": "high"
        })
    
    # Then new venues
    for venue in new[:2]:
        recommendations.append({
            "venue": venue,
            "reason": "New option - requires verification",
            "priority": "medium"
        })
    
    return recommendations

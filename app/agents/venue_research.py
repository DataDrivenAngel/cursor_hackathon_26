"""
Venue research agent - searches for venues using JigsawStack and local database.
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
                name="jigsawstack_search",
                description="Search the web for venues using JigsawStack AI Scrape",
                parameters={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to scrape for venue information"},
                        "element_prompts": {"type": "array", "items": {"type": "string"}, "description": "Prompts to extract venue details"}
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
    2. Uses JigsawStack to find additional venues if needed
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
    if len(results["existing_venues"]) < 3 and settings.JIGSAWSTACK_API_KEY:
        new_venues = await jigsawstack_search_venues(
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


async def jigsawstack_search_venues(
    capacity: Optional[int] = None,
    location: str = None,
    event_type: str = None,
    amenities: List[str] = None
) -> List[Dict[str, Any]]:
    """Search for venues using JigsawStack AI Scrape."""
    if not settings.JIGSAWSTACK_API_KEY:
        return []
    
    try:
        # Import JigsawStack
        from jigsawstack import JigsawStack
        
        # Initialize JigsawStack client
        jigsaw = JigsawStack(api_key=settings.JIGSAWSTACK_API_KEY)
        
        # Build a search query URL for venue listing websites
        # We'll search for venues in the specified location
        search_query = f"{event_type or 'event'} venues in {location}"
        search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
        
        # Define element prompts to extract venue information
        element_prompts = [
            "venue name",
            "venue address",
            "venue capacity", 
            "venue amenities",
            "venue contact email",
            "venue website"
        ]
        
        # Use JigsawStack AI Scrape to extract venue information
        response = jigsaw.web.ai_scrape({
            "url": search_url,
            "element_prompts": element_prompts
        })
        
        if response.get("success"):
            # Parse the extracted data
            extracted_data = response.get("data", {})
            venues = parse_jigsawstack_venues(extracted_data, location)
            return venues
        
        return []
        
    except ImportError:
        # If jigsawstack is not installed, return empty list
        print("JigsawStack package not installed. Run: pip install jigsawstack")
        return []
    except Exception as e:
        print(f"Error searching venues with JigsawStack: {e}")
        return []


def parse_jigsawstack_venues(
    extracted_data: Dict[str, Any],
    location: str
) -> List[Dict[str, Any]]:
    """Parse venues from JigsawStack extraction results."""
    venues = []
    
    # The response structure depends on what JigsawStack returns
    # This is a simplified parser - adjust based on actual response format
    if isinstance(extracted_data, dict):
        # Try to extract venues from the response
        for key, value in extracted_data.items():
            if isinstance(value, dict):
                venue = {
                    "name": value.get("venue name", ""),
                    "address": value.get("venue address", ""),
                    "city": location,
                    "capacity": value.get("venue capacity", 0),
                    "amenities": value.get("venue amenities", []),
                    "website": value.get("venue website", ""),
                    "contact_email": value.get("venue contact email", ""),
                    "research_data": value
                }
                if venue.get("name"):
                    venues.append(venue)
            elif isinstance(value, list):
                # Maybe the venues are in a list
                for item in value:
                    if isinstance(item, dict):
                        venue = {
                            "name": item.get("venue name", "") or item.get("name", ""),
                            "address": item.get("venue address", "") or item.get("address", ""),
                            "city": location,
                            "capacity": item.get("venue capacity", 0) or item.get("capacity", 0),
                            "amenities": item.get("venue amenities", []) or item.get("amenities", []),
                            "website": item.get("venue website", "") or item.get("website", ""),
                            "contact_email": item.get("venue contact email", "") or item.get("contact_email", ""),
                            "research_data": item
                        }
                        if venue.get("name"):
                            venues.append(venue)
    
    return venues


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

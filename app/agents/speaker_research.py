"""
Speaker research agent - searches for potential speakers using Perplexity.
"""
import httpx
import json
from typing import Optional, List, Dict, Any
from app.config import settings


class SpeakerResearchAgent(BaseAgent):
    """Agent for researching and finding potential speakers."""
    
    def __init__(self, api_key: str = None):
        super().__init__(api_key)
    
    def get_available_tools(self) -> List[Tool]:
        """Return tools available for speaker research."""
        return [
            Tool(
                name="search_local_speakers",
                description="Search for potential local speakers",
                parameters={
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "Event topic"},
                        "location": {"type": "string", "description": "City or region"}
                    }
                }
            ),
            Tool(
                name="enrich_attendee",
                description="Enrich attendee data using web search",
                parameters={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Attendee name"},
                        "email": {"type": "string", "description": "Attendee email"}
                    }
                }
            ),
            Tool(
                name="save_speaker",
                description="Save a new speaker to the database",
                parameters={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Speaker name"},
                        "email": {"type": "string", "description": "Speaker email"},
                        "bio": {"type": "string", "description": "Speaker bio"},
                        "expertise": {"type": "array", "items": {"type": "string"}},
                        "company": {"type": "string", "description": "Company or organization"},
                        "role": {"type": "string", "description": "Job title"}
                    }
                }
            ),
            Tool(
                name="generate_outreach_message",
                description="Generate an outreach message for speaker invitation",
                parameters={
                    "type": "object",
                    "properties": {
                        "speaker_name": {"type": "string", "description": "Speaker name"},
                        "topic": {"type": "string", "description": "Event topic"},
                        "event_date": {"type": "string", "description": "Event date"}
                    }
                }
            )
        ]
    
    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute speaker research workflow."""
        pass


async def research_speakers(
    topic: str,
    location: Optional[str] = None
) -> Dict[str, Any]:
    """
    Research potential speakers for a topic.
    
    This function:
    1. Uses Perplexity to search for local speakers on the topic
    2. Generates outreach templates
    3. Returns speaker recommendations
    """
    results = {
        "speakers": [],
        "outreach_templates": [],
        "enriched_attendees": []
    }
    
    # Search for speakers
    if settings.PERPLEXITY_API_KEY:
        speakers = await perplexity_search_speakers(topic, location)
        results["speakers"] = speakers
    
    # Generate outreach templates for each speaker
    for speaker in results["speakers"]:
        template = generate_outreach_template(
            speaker_name=speaker.get("name", ""),
            topic=topic
        )
        results["outreach_templates"].append({
            "speaker": speaker.get("name"),
            "template": template
        })
    
    return results


async def enrich_attendee(
    name: str,
    email: str
) -> Dict[str, Any]:
    """
    Enrich attendee data using web search.
    
    Returns company, role, social profiles, and bio information.
    """
    if not settings.PERPLEXITY_API_KEY:
        return {}
    
    query = f"Find information about {name}. Include: company, job title, bio, LinkedIn profile, Twitter/X handle, expertise, speaking experience"
    
    headers = {
        "Authorization": f"Bearer {settings.PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "user",
                "content": f"{query}. Return as JSON with fields: company, role, bio, social_profiles (object with linkedin, twitter), expertise (array), speaking_experience"
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
            
            try:
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                enriched_data = json.loads(content)
                return enriched_data
            except json.JSONDecodeError:
                return {}
        
        return {}


async def perplexity_search_speakers(
    topic: str,
    location: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search for potential speakers using Perplexity API."""
    if not settings.PERPLEXITY_API_KEY:
        return []
    
    # Build search query
    query_parts = [f"experts on {topic}"]
    if location:
        query_parts.append(f"in {location}")
    query_parts.append("who speak at conferences, are thought leaders, or have expertise to share")
    
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
                "content": f"Find potential speakers for {query}. Return as JSON array with: name, email (if available), company, role, bio, expertise (array), social_profiles (linkedin, twitter), speaking_experience"
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
            
            try:
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                speakers = json.loads(content)
                if isinstance(speakers, list):
                    return speakers
                elif isinstance(speakers, dict) and "speakers" in speakers:
                    return speakers["speakers"]
            except json.JSONDecodeError:
                return []
        
        return []


def generate_outreach_template(
    speaker_name: str,
    topic: str,
    event_name: str = "our meetup",
    event_description: str = "an engaging community event"
) -> str:
    """Generate an outreach message for inviting a speaker."""
    return f"""Subject: Speaking Opportunity: {topic}

Hi {speaker_name},

I hope this message finds you well. I'm reaching out on behalf of {event_name}.

We are organizing {event_description} focused on {topic}, and we believe your expertise would be incredibly valuable to our community.

Would you be interested in:
- Giving a talk (15-30 minutes)
- Leading a workshop
- Participating in a panel discussion

We can discuss scheduling, compensation, and any other details that would make this work for you.

Best regards,
The Meetup Team
"""

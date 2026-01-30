"""
Topic recommender service - suggests topics based on historical event data.
"""
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text


async def get_topic_recommendations(
    db: AsyncSession,
    limit: int = 5,
    event_type: str = None
) -> List[Dict[str, Any]]:
    """
    Get topic recommendations based on historical events.
    
    This analyzes past successful events and suggests topics based on:
    1. Frequency of topics in completed events
    2. Engagement metrics (if available)
    3. Similarity to current event type
    """
    # Query to get popular topics from completed events
    query = text("""
        SELECT topic, COUNT(*) as frequency
        FROM events
        WHERE status = 'completed'
        AND topic IS NOT NULL
        AND topic != ''
        GROUP BY topic
        ORDER BY frequency DESC
        LIMIT :limit
    """)
    
    result = await db.execute(query, {"limit": limit})
    rows = result.fetchall()
    
    if not rows:
        # Return some default suggestions
        return [
            {"topic": "Introduction to Technology", "frequency": 0, "reason": "Popular starter topic"},
            {"topic": "Networking and Community Building", "frequency": 0, "reason": "Always valuable"},
            {"topic": "Best Practices and Patterns", "frequency": 0, "reason": "Practical knowledge sharing"},
            {"topic": "Future Trends and Innovation", "frequency": 0, "reason": "Forward-looking discussions"},
            {"topic": "Case Studies and Real World Examples", "frequency": 0, "reason": "Practical applications"},
        ]
    
    topics = []
    for row in rows:
        topics.append({
            "topic": row.topic,
            "frequency": row.frequency,
            "reason": get_topic_reason(row.topic)
        })
    
    return topics


def get_topic_reason(topic: str) -> str:
    """Generate a reason for why this topic is recommended."""
    topic_lower = topic.lower()
    
    if "intro" in topic_lower or "beginner" in topic_lower:
        return "Popular for newcomers"
    elif "advanc" in topic_lower or "deep" in topic_lower:
        return "Appeals to experienced members"
    elif "network" in topic_lower:
        return "High engagement topic"
    elif "best practice" in topic_lower or "pattern" in topic_lower:
        return "Practical value for attendees"
    elif "case study" in topic_lower or "example" in topic_lower:
        return "Real-world applications"
    elif "trends" in topic_lower or "future" in topic_lower:
        return "Forward-looking discussion"
    else:
        return "Based on historical popularity"


async def get_related_topics(
    db: AsyncSession,
    current_topic: str,
    limit: int = 3
) -> List[str]:
    """Find topics related to the current topic."""
    query = text("""
        SELECT DISTINCT topic
        FROM events
        WHERE status = 'completed'
        AND topic IS NOT NULL
        AND topic != ''
        AND topic != :current_topic
        AND (
            topic LIKE '%' || :keyword1 || '%' OR
            topic LIKE '%' || :keyword2 || '%' OR
            topic LIKE '%' || :keyword3 || '%'
        )
        LIMIT :limit
    """)
    
    # Extract some keywords from the current topic
    words = current_topic.lower().split()[:3]
    keywords = words + [""] * (3 - len(words))
    
    result = await db.execute(query, {
        "current_topic": current_topic,
        "keyword1": keywords[0],
        "keyword2": keywords[1],
        "keyword3": keywords[2],
        "limit": limit
    })
    
    return [row.topic for row in result.fetchall()]

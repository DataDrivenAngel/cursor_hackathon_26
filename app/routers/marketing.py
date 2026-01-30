"""
Marketing router - Generate and manage marketing materials for events.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.database.connection import get_db
from app.database.schemas import MarketingMaterialCreate, MarketingMaterialUpdate, MarketingMaterialResponse
from app.auth.dependencies import get_current_user, require_admin_or_organizer
from app.models.database_models import User, Event, MarketingMaterial
from app.services.topic_recommender import get_topic_recommendations


router = APIRouter()


@router.get("/{event_id}", response_model=List[MarketingMaterialResponse])
async def get_marketing_materials(
    event_id: int,
    material_type: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all marketing materials for an event."""
    # Verify event exists
    event_result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    if event_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    query = select(MarketingMaterial).where(MarketingMaterial.event_id == event_id)
    
    if material_type:
        query = query.where(MarketingMaterial.material_type == material_type)
    
    query = query.order_by(MarketingMaterial.generated_at)
    result = await db.execute(query)
    materials = result.scalars().all()
    return materials


@router.get("/material/{material_id}", response_model=MarketingMaterialResponse)
async def get_marketing_material(material_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single marketing material by ID."""
    result = await db.execute(
        select(MarketingMaterial).where(MarketingMaterial.id == material_id)
    )
    material = result.scalar_one_or_none()
    
    if material is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marketing material not found"
        )
    
    return material


@router.post("/{event_id}/generate", response_model=MarketingMaterialResponse, status_code=status.HTTP_201_CREATED)
async def generate_marketing_material(
    event_id: int,
    material_data: MarketingMaterialCreate,
    current_user: User = Depends(require_admin_or_organizer),
    db: AsyncSession = Depends(get_db)
):
    """Generate marketing material for an event."""
    # Verify event exists
    event_result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    event = event_result.scalar_one_or_none()
    
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Get topic recommendations for context
    topics = await get_topic_recommendations(db, limit=3)
    
    # Generate content based on material type
    content = generate_content_for_material(event, material_data.material_type, topics)
    title = generate_title_for_material(event, material_data.material_type)
    
    material = MarketingMaterial(
        event_id=event_id,
        material_type=material_data.material_type,
        title=title,
        content=content,
        created_by=current_user.id
    )
    
    db.add(material)
    await db.commit()
    await db.refresh(material)
    
    return material


@router.put("/{material_id}", response_model=MarketingMaterialResponse)
async def update_marketing_material(
    material_id: int,
    material_data: MarketingMaterialUpdate,
    current_user: User = Depends(require_admin_or_organizer),
    db: AsyncSession = Depends(get_db)
):
    """Update marketing material content."""
    result = await db.execute(
        select(MarketingMaterial).where(MarketingMaterial.id == material_id)
    )
    material = result.scalar_one_or_none()
    
    if material is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marketing material not found"
        )
    
    update_data = material_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(material, field, value)
    
    material.edited_at = datetime.utcnow()
    await db.commit()
    await db.refresh(material)
    
    return material


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_marketing_material(
    material_id: int,
    current_user: User = Depends(require_admin_or_organizer),
    db: AsyncSession = Depends(get_db)
):
    """Delete a marketing material."""
    result = await db.execute(
        select(MarketingMaterial).where(MarketingMaterial.id == material_id)
    )
    material = result.scalar_one_or_none()
    
    if material is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marketing material not found"
        )
    
    await db.delete(material)
    await db.commit()


def generate_content_for_material(event: Event, material_type: str, topics: list) -> str:
    """Generate marketing content based on event details."""
    base_content = f"""
# {event.title}

{event.description or 'Join us for an exciting meetup!'}

"""
    
    if material_type == "post":
        content = f"""
{event.title}

{event.description or 'Join us for an exciting meetup!'}

{'Topic: ' + event.topic if event.topic else ''}

📅 {'Date: ' + event.scheduled_date.strftime('%B %d, %Y at %I:%M %p') if event.scheduled_date else 'Date TBD'}

#meetup #tech #community
"""
    elif material_type == "email":
        content = f"""
Subject: You're Invited: {event.title}

Hi there,

You're invited to our upcoming meetup!

**{event.title}**

{event.description or 'Join us for an engaging session with fellow enthusiasts.'}

{'We will be discussing: ' + event.topic if event.topic else ''}

{'📅 Date: ' + event.scheduled_date.strftime('%B %d, %Y at %I:%M %p') if event.scheduled_date else 'Date: TBD'}

Don't miss out! Register now.

Best regards,
The Meetup Team
"""
    elif material_type == "social":
        content = f"""
🎉 Upcoming Event: {event.title}!

{event.description or 'Join us!'}

{'📍 Topic: ' + event.topic if event.topic else ''}
{'📅 ' + event.scheduled_date.strftime('%B %d') if event.scheduled_date else ''}

#community #events #networking
"""
    else:
        content = base_content
    
    return content


def generate_title_for_material(event: Event, material_type: str) -> str:
    """Generate a title for the marketing material."""
    type_labels = {
        "post": "Social Media Post",
        "email": "Email Announcement",
        "social": "Social Media Update"
    }
    
    return f"{event.title} - {type_labels.get(material_type, 'Marketing Material')}"

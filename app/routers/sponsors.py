"""
Sponsors router - CRUD operations and event-sponsor linking.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.connection import get_db
from app.database.schemas import SponsorCreate, SponsorUpdate, SponsorResponse, EventSponsorCreate
from app.auth.dependencies import get_current_user, require_admin_or_organizer
from app.models.database_models import User, Sponsor, Event, EventSponsor


router = APIRouter()


@router.get("/", response_model=List[SponsorResponse])
async def list_sponsors(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all sponsors."""
    result = await db.execute(
        select(Sponsor)
        .offset(skip)
        .limit(limit)
        .order_by(Sponsor.name)
    )
    sponsors = result.scalars().all()
    return sponsors


@router.get("/{sponsor_id}", response_model=SponsorResponse)
async def get_sponsor(sponsor_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single sponsor by ID."""
    result = await db.execute(
        select(Sponsor).where(Sponsor.id == sponsor_id)
    )
    sponsor = result.scalar_one_or_none()
    
    if sponsor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sponsor not found"
        )
    
    return sponsor


@router.post("/", response_model=SponsorResponse, status_code=status.HTTP_201_CREATED)
async def create_sponsor(
    sponsor_data: SponsorCreate,
    current_user: User = Depends(require_admin_or_organizer),
    db: AsyncSession = Depends(get_db)
):
    """Create a new sponsor."""
    sponsor = Sponsor(
        name=sponsor_data.name,
        contact_email=sponsor_data.contact_email,
        contact_phone=sponsor_data.contact_phone,
        website=sponsor_data.website,
        description=sponsor_data.description,
        created_by=current_user.id
    )
    
    db.add(sponsor)
    await db.commit()
    await db.refresh(sponsor)
    
    return sponsor


@router.put("/{sponsor_id}", response_model=SponsorResponse)
async def update_sponsor(
    sponsor_id: int,
    sponsor_data: SponsorUpdate,
    current_user: User = Depends(require_admin_or_organizer),
    db: AsyncSession = Depends(get_db)
):
    """Update an existing sponsor."""
    result = await db.execute(
        select(Sponsor).where(Sponsor.id == sponsor_id)
    )
    sponsor = result.scalar_one_or_none()
    
    if sponsor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sponsor not found"
        )
    
    update_data = sponsor_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sponsor, field, value)
    
    await db.commit()
    await db.refresh(sponsor)
    
    return sponsor


@router.delete("/{sponsor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sponsor(
    sponsor_id: int,
    current_user: User = Depends(require_admin_or_organizer),
    db: AsyncSession = Depends(get_db)
):
    """Delete a sponsor."""
    result = await db.execute(
        select(Sponsor).where(Sponsor.id == sponsor_id)
    )
    sponsor = result.scalar_one_or_none()
    
    if sponsor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sponsor not found"
        )
    
    await db.delete(sponsor)
    await db.commit()


# ==================== Event-Sponsor Linking ====================

@router.post("/events/{event_id}/sponsors/{sponsor_id}", status_code=status.HTTP_201_CREATED)
async def link_sponsor_to_event(
    event_id: int,
    sponsor_id: int,
    link_data: EventSponsorCreate = None,
    current_user: User = Depends(require_admin_or_organizer),
    db: AsyncSession = Depends(get_db)
):
    """Link a sponsor to an event."""
    # Verify event exists
    event_result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    if event_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Verify sponsor exists
    sponsor_result = await db.execute(
        select(Sponsor).where(Sponsor.id == sponsor_id)
    )
    if sponsor_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sponsor not found"
        )
    
    # Check if already linked
    link_result = await db.execute(
        select(EventSponsor).where(
            EventSponsor.event_id == event_id,
            EventSponsor.sponsor_id == sponsor_id
        )
    )
    if link_result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sponsor is already linked to this event"
        )
    
    # Create link
    event_sponsor = EventSponsor(
        event_id=event_id,
        sponsor_id=sponsor_id,
        sponsorship_level=link_data.sponsorship_level if link_data else None,
        notes=link_data.notes if link_data else None
    )
    
    db.add(event_sponsor)
    await db.commit()
    
    return {"message": "Sponsor linked to event successfully"}


@router.delete("/events/{event_id}/sponsors/{sponsor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_sponsor_from_event(
    event_id: int,
    sponsor_id: int,
    current_user: User = Depends(require_admin_or_organizer),
    db: AsyncSession = Depends(get_db)
):
    """Unlink a sponsor from an event."""
    result = await db.execute(
        select(EventSponsor).where(
            EventSponsor.event_id == event_id,
            EventSponsor.sponsor_id == sponsor_id
        )
    )
    event_sponsor = result.scalar_one_or_none()
    
    if event_sponsor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sponsor is not linked to this event"
        )
    
    await db.delete(event_sponsor)
    await db.commit()

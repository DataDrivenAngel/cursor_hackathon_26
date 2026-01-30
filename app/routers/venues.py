"""
Venues router - CRUD operations and venue research agent.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.connection import get_db
from app.database.schemas import VenueCreate, VenueUpdate, VenueResponse, VenueResearchRequest
from app.auth.dependencies import get_current_user, require_admin_or_organizer
from app.models.database_models import User, Venue
from app.agents.venue_research import research_venues


router = APIRouter()


@router.get("/", response_model=List[VenueResponse])
async def list_venues(
    skip: int = 0,
    limit: int = 100,
    city: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all venues with optional filtering."""
    query = select(Venue)
    
    if city:
        query = query.where(Venue.city.ilike(f"%{city}%"))
    
    query = query.offset(skip).limit(limit).order_by(Venue.name)
    result = await db.execute(query)
    venues = result.scalars().all()
    return venues


@router.get("/{venue_id}", response_model=VenueResponse)
async def get_venue(venue_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single venue by ID."""
    result = await db.execute(
        select(Venue).where(Venue.id == venue_id)
    )
    venue = result.scalar_one_or_none()
    
    if venue is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )
    
    return venue


@router.post("/", response_model=VenueResponse, status_code=status.HTTP_201_CREATED)
async def create_venue(
    venue_data: VenueCreate,
    current_user: User = Depends(require_admin_or_organizer),
    db: AsyncSession = Depends(get_db)
):
    """Create a new venue."""
    venue = Venue(
        name=venue_data.name,
        address=venue_data.address,
        city=venue_data.city,
        state=venue_data.state,
        country=venue_data.country,
        capacity=venue_data.capacity,
        amenities=venue_data.amenities,
        contact_email=venue_data.contact_email,
        contact_phone=venue_data.contact_phone,
        website=venue_data.website,
        created_by=current_user.id
    )
    
    db.add(venue)
    await db.commit()
    await db.refresh(venue)
    
    return venue


@router.put("/{venue_id}", response_model=VenueResponse)
async def update_venue(
    venue_id: int,
    venue_data: VenueUpdate,
    current_user: User = Depends(require_admin_or_organizer),
    db: AsyncSession = Depends(get_db)
):
    """Update an existing venue."""
    result = await db.execute(
        select(Venue).where(Venue.id == venue_id)
    )
    venue = result.scalar_one_or_none()
    
    if venue is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )
    
    update_data = venue_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(venue, field, value)
    
    await db.commit()
    await db.refresh(venue)
    
    return venue


@router.delete("/{venue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_venue(
    venue_id: int,
    current_user: User = Depends(require_admin_or_organizer),
    db: AsyncSession = Depends(get_db)
):
    """Delete a venue."""
    result = await db.execute(
        select(Venue).where(Venue.id == venue_id)
    )
    venue = result.scalar_one_or_none()
    
    if venue is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )
    
    await db.delete(venue)
    await db.commit()


@router.post("/research", response_model=dict)
async def research_venue(
    request: VenueResearchRequest,
    current_user: User = Depends(require_admin_or_organizer),
    db: AsyncSession = Depends(get_db)
):
    """
    Run venue research agent to find suitable venues.
    
    This endpoint:
    1. Searches existing venues in the database
    2. Uses Perplexity to find additional venues
    3. Returns research results with recommendations
    """
    try:
        results = await research_venues(
            capacity=request.capacity,
            location=request.location,
            amenities=request.amenities,
            event_type=request.event_type
        )
        
        # Save new venues to database
        saved_venues = []
        for venue_data in results.get("new_venues", []):
            venue = Venue(
                name=venue_data["name"],
                address=venue_data.get("address", ""),
                city=request.location,
                country="Unknown",
                capacity=venue_data.get("capacity"),
                research_data=str(venue_data),
                created_by=current_user.id
            )
            db.add(venue)
            saved_venues.append(venue)
        
        if saved_venues:
            await db.commit()
        
        return results
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Venue research failed: {str(e)}"
        )

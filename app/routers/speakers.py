"""
Speakers router - CRUD operations, speaker research agent, and attendee enrichment.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.connection import get_db
from app.database.schemas import (
    SpeakerCreate, SpeakerUpdate, SpeakerResponse,
    AttendeeProfileCreate, AttendeeProfileUpdate, AttendeeProfileResponse,
    AttendeeEnrichRequest, SpeakerResearchRequest, SpeakerResearchResponse
)
from app.auth.dependencies import get_current_user, require_admin_or_organizer
from app.models.database_models import User, Speaker, AttendeeProfile
from app.agents.speaker_research import research_speakers, enrich_attendee


router = APIRouter()


# ==================== Speakers ====================

@router.get("/", response_model=List[SpeakerResponse])
async def list_speakers(
    skip: int = 0,
    limit: int = 100,
    expertise: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all speakers with optional filtering."""
    query = select(Speaker)
    
    if expertise:
        query = query.where(Speaker.expertise.ilike(f"%{expertise}%"))
    
    query = query.offset(skip).limit(limit).order_by(Speaker.name)
    result = await db.execute(query)
    speakers = result.scalars().all()
    return speakers


@router.get("/{speaker_id}", response_model=SpeakerResponse)
async def get_speaker(speaker_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single speaker by ID."""
    result = await db.execute(
        select(Speaker).where(Speaker.id == speaker_id)
    )
    speaker = result.scalar_one_or_none()
    
    if speaker is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Speaker not found"
        )
    
    return speaker


@router.post("/", response_model=SpeakerResponse, status_code=status.HTTP_201_CREATED)
async def create_speaker(
    speaker_data: SpeakerCreate,
    current_user: User = Depends(require_admin_or_organizer),
    db: AsyncSession = Depends(get_db)
):
    """Create a new speaker."""
    speaker = Speaker(
        name=speaker_data.name,
        email=speaker_data.email,
        bio=speaker_data.bio,
        expertise=speaker_data.expertise,
        social_profiles=speaker_data.social_profiles,
        company=speaker_data.company,
        role=speaker_data.role,
        created_by=current_user.id
    )
    
    db.add(speaker)
    await db.commit()
    await db.refresh(speaker)
    
    return speaker


@router.put("/{speaker_id}", response_model=SpeakerResponse)
async def update_speaker(
    speaker_id: int,
    speaker_data: SpeakerUpdate,
    current_user: User = Depends(require_admin_or_organizer),
    db: AsyncSession = Depends(get_db)
):
    """Update an existing speaker."""
    result = await db.execute(
        select(Speaker).where(Speaker.id == speaker_id)
    )
    speaker = result.scalar_one_or_none()
    
    if speaker is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Speaker not found"
        )
    
    update_data = speaker_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(speaker, field, value)
    
    await db.commit()
    await db.refresh(speaker)
    
    return speaker


@router.delete("/{speaker_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_speaker(
    speaker_id: int,
    current_user: User = Depends(require_admin_or_organizer),
    db: AsyncSession = Depends(get_db)
):
    """Delete a speaker."""
    result = await db.execute(
        select(Speaker).where(Speaker.id == speaker_id)
    )
    speaker = result.scalar_one_or_none()
    
    if speaker is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Speaker not found"
        )
    
    await db.delete(speaker)
    await db.commit()


# ==================== Speaker Research ====================

@router.post("/research", response_model=SpeakerResearchResponse)
async def research_speaker(
    request: SpeakerResearchRequest,
    current_user: User = Depends(require_admin_or_organizer),
    db: AsyncSession = Depends(get_db)
):
    """
    Run speaker research agent to find potential speakers.
    
    This endpoint:
    1. Uses Perplexity to search for local speakers on the topic
    2. Enriches attendee data from previous events
    3. Returns speaker recommendations and outreach templates
    """
    try:
        results = await research_speakers(
            topic=request.topic,
            location=request.location
        )
        
        # Save new speakers to database
        saved_speakers = []
        for speaker_data in results.get("speakers", []):
            speaker = Speaker(
                name=speaker_data["name"],
                email=speaker_data.get("email"),
                bio=speaker_data.get("bio"),
                expertise=request.topic,
                company=speaker_data.get("company"),
                role=speaker_data.get("role"),
                created_by=current_user.id
            )
            db.add(speaker)
            saved_speakers.append(speaker)
        
        if saved_speakers:
            await db.commit()
        
        return results
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speaker research failed: {str(e)}"
        )


# ==================== Attendee Profiles ====================

@router.get("/attendees", response_model=List[AttendeeProfileResponse])
async def list_attendees(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all attendee profiles."""
    result = await db.execute(
        select(AttendeeProfile)
        .offset(skip)
        .limit(limit)
        .order_by(AttendeeProfile.name)
    )
    attendees = result.scalars().all()
    return attendees


@router.post("/attendees", response_model=AttendeeProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_attendee(
    attendee_data: AttendeeProfileCreate,
    current_user: User = Depends(require_admin_or_organizer),
    db: AsyncSession = Depends(get_db)
):
    """Create a new attendee profile."""
    attendee = AttendeeProfile(
        name=attendee_data.name,
        email=attendee_data.email,
        company=attendee_data.company,
        role=attendee_data.role,
        bio=attendee_data.bio,
        social_profiles=attendee_data.social_profiles
    )
    
    db.add(attendee)
    await db.commit()
    await db.refresh(attendee)
    
    return attendee


@router.post("/enrich", response_model=AttendeeProfileResponse)
async def enrich_attendee_profile(
    request: AttendeeEnrichRequest,
    current_user: User = Depends(require_admin_or_organizer),
    db: AsyncSession = Depends(get_db)
):
    """
    Enrich attendee data using AI search.
    
    Finds the attendee profile and enriches it with:
    - Company information
    - Role/position
    - Social profiles
    - Bio
    """
    # Find or create attendee profile
    result = await db.execute(
        select(AttendeeProfile).where(AttendeeProfile.email == request.email)
    )
    attendee = result.scalar_one_or_none()
    
    if attendee is None:
        # Create new profile
        attendee = AttendeeProfile(
            name=request.name,
            email=request.email
        )
        db.add(attendee)
        await db.commit()
        await db.refresh(attendee)
    
    try:
        # Enrich the attendee
        enriched_data = await enrich_attendee(request.name, request.email)
        
        # Update profile with enriched data
        if enriched_data.get("company"):
            attendee.company = enriched_data["company"]
        if enriched_data.get("role"):
            attendee.role = enriched_data["role"]
        if enriched_data.get("bio"):
            attendee.bio = enriched_data["bio"]
        if enriched_data.get("social_profiles"):
            attendee.social_profiles = str(enriched_data["social_profiles"])
        
        attendee.enriched_at = __import__('datetime').datetime.utcnow()
        
        await db.commit()
        await db.refresh(attendee)
        
        return attendee
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Attendee enrichment failed: {str(e)}"
        )

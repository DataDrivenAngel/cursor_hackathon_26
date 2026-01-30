"""
Events router - CRUD operations, topic recommendations, and integrations.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from sqlalchemy.orm import selectinload
from app.database.connection import get_db
from app.database.schemas import (
    EventCreate, EventUpdate, EventResponse, TopicRecommendationResponse,
    VenueResearchRequest, VenueResearchResponse, SpeakerResearchRequest,
    SpeakerResearchResponse
)
from app.auth.dependencies import get_current_user, bypass_admin_check
from app.models.database_models import (
    User, Event, Organizer, Venue, Speaker, Task, MarketingMaterial, EventSponsor
)
from app.models.workflow_models import WorkflowStage, WorkflowSubtask
from app.services.topic_recommender import get_topic_recommendations
from app.services.meetup_service import create_meetup_event, sync_meetup_status
from app.services.luma_service import create_luma_event, sync_luma_status
from app.services.minimax_service import generate_event_image
from app.agents.venue_research import research_venues
from app.agents.speaker_research import research_speakers


router = APIRouter()

# Templates
templates = Jinja2Templates(directory="app/templates")


# ==================== HTML Pages ====================

@router.get("/{event_id}/page", response_class=HTMLResponse)
async def get_event_page(
    request: Request,
    event_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get event detail page."""
    result = await db.execute(
        select(Event).options(
            selectinload(Event.venue),
            selectinload(Event.organizers).selectinload(Organizer.user),
            selectinload(Event.tasks),
            selectinload(Event.event_sponsors).selectinload(EventSponsor.sponsor),
            selectinload(Event.marketing_materials)
        ).where(Event.id == event_id)
    )
    event = result.scalar_one_or_none()
    
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return templates.TemplateResponse("event_detail.html", {
        "request": request,
        "event": event
    })


@router.get("/{event_id}/workflow/page", response_class=HTMLResponse)
async def get_workflow_page(
    request: Request,
    event_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get event workflow tracker page."""
    from app.services.workflow_service import WorkflowService
    from app.services.workflow_templates import PHASE_CONFIG
    from app.models.workflow_models import WorkflowSubtask
    
    # Get event
    result = await db.execute(
        select(Event).options(
            selectinload(Event.venue),
            selectinload(Event.organizers).selectinload(Organizer.user)
        ).where(Event.id == event_id)
    )
    event = result.scalar_one_or_none()
    
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Get workflow data
    service = WorkflowService(db)
    workflow_data = await service.get_workflow_summary(event_id)
    
    # Get all subtasks
    subtasks_result = await db.execute(
        select(WorkflowSubtask).options(
            selectinload(WorkflowSubtask.stage)
        ).join(WorkflowStage).where(
            and_(
                WorkflowStage.event_id == event_id
            )
        )
    )
    subtasks = subtasks_result.scalars().all()
    
    return templates.TemplateResponse("event_workflow.html", {
        "request": request,
        "event": event,
        "workflow": workflow_data,
        "subtasks": subtasks,
        "PHASE_CONFIG": PHASE_CONFIG
    })

@router.get("/", response_model=List[EventResponse])
async def list_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all events with optional filtering."""
    query = select(Event).options(selectinload(Event.venue))
    
    if status_filter:
        query = query.where(Event.status == status_filter)
    
    query = query.offset(skip).limit(limit).order_by(desc(Event.created_at))
    result = await db.execute(query)
    events = result.scalars().all()
    return events


@router.get("/page", response_class=HTMLResponse)
async def get_events_page(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Get events list page."""
    result = await db.execute(
        select(Event).options(
            selectinload(Event.venue),
            selectinload(Event.organizers).selectinload(Organizer.user)
        ).order_by(desc(Event.created_at))
    )
    events = result.scalars().all()
    
    return templates.TemplateResponse("events.html", {
        "request": request,
        "events": events
    })


@router.get("/list", response_class=HTMLResponse)
async def get_events_list(
    request: Request,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get events list HTML partial for HTMX updates.
    
    This endpoint returns just the events grid HTML fragment for dynamic
    updates without refreshing the entire page. Supports optional status filtering.
    """
    query = select(Event).options(
        selectinload(Event.venue),
        selectinload(Event.organizers).selectinload(Organizer.user)
    )
    
    if status_filter and status_filter != "all":
        query = query.where(Event.status == status_filter)
    
    query = query.order_by(desc(Event.created_at))
    result = await db.execute(query)
    events = result.scalars().all()
    
    return templates.TemplateResponse("components/events-list.html", {
        "request": request,
        "events": events
    })


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single event by ID."""
    result = await db.execute(
        select(Event).options(
            selectinload(Event.venue),
            selectinload(Event.organizers).selectinload(Organizer.user),
            selectinload(Event.tasks)
        ).where(Event.id == event_id)
    )
    event = result.scalar_one_or_none()
    
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return event


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    current_user: User = Depends(bypass_admin_check),
    db: AsyncSession = Depends(get_db)
):
    """Create a new event."""
    # Validate venue if provided
    if event_data.venue_id:
        venue_result = await db.execute(
            select(Venue).where(Venue.id == event_data.venue_id)
        )
        if venue_result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Venue not found"
            )
    
    # Create event
    event = Event(
        title=event_data.title,
        description=event_data.description,
        topic=event_data.topic,
        scheduled_date=event_data.scheduled_date,
        venue_id=event_data.venue_id,
        created_by=current_user.id
    )
    
    db.add(event)
    await db.commit()
    await db.refresh(event)
    
    # Generate event image if requested
    if event_data.generate_image:
        image_url = await generate_event_image(
            event_title=event.title,
            event_topic=event.topic,
            event_description=event.description
        )
        if image_url:
            event.image_url = image_url
            await db.commit()
            await db.refresh(event)
    
    # Add creator as primary organizer
    organizer = Organizer(
        user_id=current_user.id,
        event_id=event.id,
        role="primary"
    )
    db.add(organizer)
    await db.commit()
    
    return event


@router.post("/htmx", response_class=HTMLResponse)
async def create_event_htmx(
    request: Request,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    topic: Optional[str] = Form(None),
    scheduled_date: Optional[str] = Form(None),
    current_user: User = Depends(bypass_admin_check),
    db: AsyncSession = Depends(get_db)
):
    """Create a new event via HTMX - returns HTML snippet."""
    from datetime import datetime
    
    # Parse scheduled_date if provided
    parsed_date = None
    if scheduled_date:
        try:
            parsed_date = datetime.fromisoformat(scheduled_date.replace('T', ' '))
        except ValueError:
            pass
    
    # Create event
    event = Event(
        title=title,
        description=description,
        topic=topic,
        scheduled_date=parsed_date,
        created_by=current_user.id
    )
    
    db.add(event)
    await db.commit()
    await db.refresh(event)
    
    # Add creator as primary organizer
    organizer = Organizer(
        user_id=current_user.id,
        event_id=event.id,
        role="primary"
    )
    db.add(organizer)
    await db.commit()
    
    # Return HTML for the new event card
    return f"""
    <div class="event-card" data-status="{event.status}">
        <div class="event-header">
            <h3>{event.title}</h3>
            <span class="event-status status-{event.status}">{event.status}</span>
        </div>
        <p class="event-description">{event.description or "No description"}</p>
        <div class="event-meta">
            <span class="event-topic">{event.topic or "No topic"}</span>
            <span class="event-date">
                {event.scheduled_date.strftime('%B %d, %Y') if event.scheduled_date else "Date TBD"}
            </span>
        </div>
        <div class="event-actions">
            <a href="/events/{event.id}/page" class="btn btn-sm">View Details</a>
            <button class="btn btn-sm btn-secondary" 
                    hx-delete="/events/{event.id}"
                    hx-confirm="Are you sure you want to delete this event?"
                    hx-target="closest .event-card">
                Delete
            </button>
        </div>
    </div>
    """


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    current_user: User = Depends(bypass_admin_check),
    db: AsyncSession = Depends(get_db)
):
    """Update an existing event."""
    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    event = result.scalar_one_or_none()
    
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Update fields
    update_data = event_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    event.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(event)
    
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int,
    current_user: User = Depends(bypass_admin_check),
    db: AsyncSession = Depends(get_db)
):
    """Delete an event."""
    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    event = result.scalar_one_or_none()
    
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    await db.delete(event)
    await db.commit()


# ==================== Topic Recommendations ====================

@router.get("/{event_id}/recommendations", response_model=TopicRecommendationResponse)
async def get_recommendations(
    event_id: int,
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Get topic recommendations based on historical events."""
    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    event = result.scalar_one_or_none()
    
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    topics = await get_topic_recommendations(db, limit)
    return {"topics": topics}


# ==================== Meetup Integration ====================

@router.post("/{event_id}/meetup")
async def push_to_meetup(
    event_id: int,
    current_user: User = Depends(bypass_admin_check),
    db: AsyncSession = Depends(get_db)
):
    """Create event on Meetup and store the meetup_id."""
    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    event = result.scalar_one_or_none()
    
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    try:
        meetup_id = await create_meetup_event(event)
        event.meetup_id = meetup_id
        await db.commit()
        return {"message": "Event pushed to Meetup", "meetup_id": meetup_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to push to Meetup: {str(e)}"
        )


@router.get("/{event_id}/meetup/status")
async def get_meetup_status(
    event_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get event status from Meetup."""
    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    event = result.scalar_one_or_none()
    
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    if not event.meetup_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event not pushed to Meetup"
        )
    
    try:
        status_data = await sync_meetup_status(event.meetup_id)
        return status_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Meetup status: {str(e)}"
        )


# ==================== Luma Integration ====================

@router.post("/{event_id}/luma")
async def push_to_luma(
    event_id: int,
    current_user: User = Depends(bypass_admin_check),
    db: AsyncSession = Depends(get_db)
):
    """Create event on Luma and store the luma_id."""
    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    event = result.scalar_one_or_none()
    
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    try:
        luma_id = await create_luma_event(event)
        event.luma_id = luma_id
        await db.commit()
        return {"message": "Event pushed to Luma", "luma_id": luma_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to push to Luma: {str(e)}"
        )


@router.get("/{event_id}/integrations/status")
async def get_integration_status(
    event_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get sync status for all integrations."""
    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    event = result.scalar_one_or_none()
    
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    status_data = {
        "meetup": {
            "id": event.meetup_id,
            "synced": event.meetup_id is not None
        },
        "luma": {
            "id": event.luma_id,
            "synced": event.luma_id is not None
        }
    }
    
    return status_data


# ==================== Image Generation ====================

@router.post("/{event_id}/generate-image")
async def generate_event_image_endpoint(
    event_id: int,
    current_user: User = Depends(bypass_admin_check),
    db: AsyncSession = Depends(get_db)
):
    """Generate an AI image for an event using MiniMax."""
    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    event = result.scalar_one_or_none()
    
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Generate the image
    image_url = await generate_event_image(
        event_title=event.title,
        event_topic=event.topic,
        event_description=event.description
    )
    
    if image_url:
        event.image_url = image_url
        await db.commit()
        return {"message": "Image generated successfully", "image_url": image_url}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate image. Check API key configuration."
        )

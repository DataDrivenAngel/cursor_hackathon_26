"""
Workflow API Router - Event workflow management endpoints.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.auth.dependencies import get_current_user, bypass_admin_check
from app.models.database_models import User, Event
from app.services.workflow_service import WorkflowService
from app.services.workflow_templates import get_workflow_template, generate_subtasks_for_phase


router = APIRouter()


@router.post("/events/{event_id}/workflow/initialize")
async def initialize_workflow(
    event_id: int,
    event_type: str = Query("meetup", description="Event type: meetup, workshop, conference"),
    current_user: User = Depends(bypass_admin_check),
    db: AsyncSession = Depends(get_db)
):
    """Initialize workflow for an event."""
    
    # Verify event exists
    event_result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    event = event_result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    service = WorkflowService(db)
    progress = await service.initialize_workflow(event_id, event_type)
    
    return {
        "message": "Workflow initialized successfully",
        "progress": progress.to_dict(),
        "template": get_workflow_template(event_type)
    }


@router.get("/events/{event_id}/workflow/progress")
async def get_workflow_progress(
    event_id: int,
    current_user: User = Depends(bypass_admin_check),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive workflow progress for an event."""
    
    service = WorkflowService(db)
    progress = await service.calculate_progress(event_id)
    
    return progress


@router.get("/events/{event_id}/workflow/progress/frontend")
async def get_frontend_workflow_progress(
    event_id: int,
    current_user: User = Depends(bypass_admin_check),
    db: AsyncSession = Depends(get_db)
):
    """Get workflow progress formatted for frontend consumption."""
    
    service = WorkflowService(db)
    progress = await service.get_frontend_workflow_progress(event_id)
    
    return progress


@router.get("/events/{event_id}/workflow/milestones/frontend")
async def get_frontend_milestones(
    event_id: int,
    current_user: User = Depends(bypass_admin_check),
    db: AsyncSession = Depends(get_db)
):
    """Get milestones formatted for frontend consumption."""
    
    service = WorkflowService(db)
    milestones = await service.get_frontend_milestones(event_id)
    
    return milestones


@router.get("/events/{event_id}/workflow/summary")
async def get_workflow_summary(
    event_id: int,
    current_user: User = Depends(bypass_admin_check),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed workflow summary with stages and subtasks."""
    
    service = WorkflowService(db)
    summary = await service.get_workflow_summary(event_id)
    
    return summary


@router.put("/events/{event_id}/workflow/stages/{stage_id}/start")
async def start_stage(
    event_id: int,
    stage_id: int,
    current_user: User = Depends(bypass_admin_check),
    db: AsyncSession = Depends(get_db)
):
    """Mark a workflow stage as in progress."""
    
    from app.models.workflow_models import WorkflowStage
    
    result = await db.execute(
        select(WorkflowStage).where(
            and_(
                WorkflowStage.id == stage_id,
                WorkflowStage.event_id == event_id
            )
        )
    )
    stage = result.scalar_one_or_none()
    
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow stage not found"
        )
    
    stage.status = "in_progress"
    stage.started_at = datetime.utcnow()
    await db.commit()
    
    # Recalculate progress
    service = WorkflowService(db)
    await service.calculate_progress(event_id)
    
    return {"message": "Stage started", "stage": stage.to_dict()}


@router.put("/events/{event_id}/workflow/stages/{stage_id}/complete")
async def complete_stage(
    event_id: int,
    stage_id: int,
    current_user: User = Depends(bypass_admin_check),
    db: AsyncSession = Depends(get_db)
):
    """Mark a workflow stage as completed."""
    
    from app.models.workflow_models import WorkflowStage
    
    result = await db.execute(
        select(WorkflowStage).where(
            and_(
                WorkflowStage.id == stage_id,
                WorkflowStage.event_id == event_id
            )
        )
    )
    stage = result.scalar_one_or_none()
    
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow stage not found"
        )
    
    # Check all subtasks are done
    from app.models.workflow_models import WorkflowSubtask
    subtasks_result = await db.execute(
        select(WorkflowSubtask).where(WorkflowSubtask.stage_id == stage_id)
    )
    subtasks = subtasks_result.scalars().all()
    
    incomplete = [s for s in subtasks if s.status not in ["done", "blocked"]]
    if incomplete:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot complete stage. {len(incomplete)} subtask(s) remaining."
        )
    
    stage.status = "completed"
    stage.completed_at = datetime.utcnow()
    stage.progress = 100.0
    
    await db.commit()
    
    # Recalculate progress
    service = WorkflowService(db)
    await service.calculate_progress(event_id)
    
    return {"message": "Stage completed", "stage": stage.to_dict()}


@router.put("/events/{event_id}/workflow/subtasks/{subtask_id}")
async def update_subtask(
    event_id: int,
    subtask_id: int,
    status: str = Query(..., description="New status: todo, in_progress, review, done, blocked"),
    current_user: User = Depends(bypass_admin_check),
    db: AsyncSession = Depends(get_db)
):
    """Update a subtask status."""
    
    service = WorkflowService(db)
    subtask = await service.update_subtask_status(subtask_id, status, current_user.id)
    
    return subtask.to_dict()


@router.post("/events/{event_id}/workflow/subtasks/{subtask_id}/block")
async def block_subtask(
    event_id: int,
    subtask_id: int,
    reason: str = Query(..., description="Reason for blocking"),
    current_user: User = Depends(bypass_admin_check),
    db: AsyncSession = Depends(get_db)
):
    """Mark a subtask as blocked."""
    
    from app.models.workflow_models import WorkflowSubtask
    
    result = await db.execute(
        select(WorkflowSubtask).where(WorkflowSubtask.id == subtask_id)
    )
    subtask = result.scalar_one_or_none()
    
    if not subtask:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subtask not found"
        )
    
    subtask.status = "blocked"
    subtask.is_blocked = True
    subtask.notes = f"BLOCKED: {reason}"
    
    await db.commit()
    
    # Recalculate progress
    service = WorkflowService(db)
    await service.calculate_progress(event_id)
    
    return {"message": "Subtask blocked", "subtask": subtask.to_dict()}


@router.post("/events/{event_id}/workflow/subtasks/{subtask_id}/unblock")
async def unblock_subtask(
    event_id: int,
    subtask_id: int,
    current_user: User = Depends(bypass_admin_check),
    db: AsyncSession = Depends(get_db)
):
    """Remove blocking from a subtask."""
    
    from app.models.workflow_models import WorkflowSubtask
    
    result = await db.execute(
        select(WorkflowSubtask).where(WorkflowSubtask.id == subtask_id)
    )
    subtask = result.scalar_one_or_none()
    
    if not subtask:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subtask not found"
        )
    
    subtask.status = "todo"
    subtask.is_blocked = False
    subtask.notes = None
    
    await db.commit()
    
    service = WorkflowService(db)
    await service.calculate_progress(event_id)
    
    return {"message": "Subtask unblocked", "subtask": subtask.to_dict()}


@router.put("/events/{event_id}/workflow/milestones/{milestone_id}/complete")
async def complete_milestone(
    event_id: int,
    milestone_id: int,
    current_user: User = Depends(bypass_admin_check),
    db: AsyncSession = Depends(get_db)
):
    """Mark a milestone as completed."""
    
    from app.models.workflow_models import EventMilestone
    
    result = await db.execute(
        select(EventMilestone).where(
            and_(
                EventMilestone.id == milestone_id,
                EventMilestone.event_id == event_id
            )
        )
    )
    milestone = result.scalar_one_or_none()
    
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )
    
    milestone.is_completed = True
    milestone.completed_at = datetime.utcnow()
    
    await db.commit()
    
    service = WorkflowService(db)
    await service.calculate_progress(event_id)
    
    return {"message": "Milestone completed", "milestone": milestone.to_dict()}


@router.get("/events/{event_id}/workflow/suggestions")
async def get_workflow_suggestions(
    event_id: int,
    current_user: User = Depends(bypass_admin_check),
    db: AsyncSession = Depends(get_db)
):
    """Get AI-generated suggestions for the event workflow."""
    
    service = WorkflowService(db)
    progress = await service.calculate_progress(event_id)
    
    return {
        "suggestions": progress.get("suggestions", []),
        "warnings": progress.get("warnings", []),
        "overall_progress": progress.get("overall_progress", 0),
        "is_on_track": progress.get("timeline", {}).get("is_on_track", True)
    }


@router.get("/workflow/templates")
async def get_workflow_templates(
    event_type: Optional[str] = Query(None, description="Filter by event type")
):
    """Get available workflow templates."""
    
    templates = {
        "meetup": get_workflow_template("meetup"),
        "workshop": get_workflow_template("workshop"),
        "conference": get_workflow_template("conference")
    }
    
    if event_type:
        if event_type in templates:
            return templates[event_type]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template not found for event type: {event_type}"
            )
    
    return templates

"""
Workflow API Router - Event workflow management endpoints.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database.connection import get_db
from app.auth.dependencies import get_current_user, bypass_admin_check
from app.models.database_models import User, Event
from app.services.workflow_service import WorkflowService
from app.services.workflow_templates import get_workflow_template, generate_subtasks_for_phase
from app.services.ai_workflow_service import AIWorkflowAnalyzer, AITask


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


# ==================== AI Workflow Endpoints ====================

@router.get("/events/{event_id}/workflow/ai-analysis")
async def get_ai_workflow_analysis(
    event_id: int,
    current_user: User = Depends(bypass_admin_check),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI-powered workflow analysis with intelligent insights and recommendations.
    
    This endpoint analyzes all tasks in the workflow and provides:
    - Smart insights about blockers, overdue tasks, and risks
    - Priority recommendations based on timeline and dependencies
    - Timeline predictions and risk assessments
    - Resource optimization suggestions
    """
    from app.models.workflow_models import WorkflowSubtask, WorkflowStage, EventMilestone
    
    # Get event with scheduled date
    event_result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    event = event_result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Get all stages for this event
    stages_result = await db.execute(
        select(WorkflowStage).where(WorkflowStage.event_id == event_id)
    )
    stages = stages_result.scalars().all()
    
    # Get all subtasks
    stage_ids = [s.id for s in stages]
    if stage_ids:
        subtasks_result = await db.execute(
            select(WorkflowSubtask).where(WorkflowSubtask.stage_id.in_(stage_ids))
        )
        subtasks = subtasks_result.scalars().all()
    else:
        subtasks = []
    
    # Get milestones
    milestones_result = await db.execute(
        select(EventMilestone).where(EventMilestone.event_id == event_id)
    )
    milestones = milestones_result.scalars().all()
    
    # Convert subtasks to AI tasks
    ai_tasks = []
    for subtask in subtasks:
        # Find stage for this subtask
        stage = next((s for s in stages if s.id == subtask.stage_id), None)
        
        ai_task = AITask(
            id=str(subtask.id),
            title=subtask.title,
            description=subtask.description or "",
            status=subtask.status,
            priority=subtask.priority or "medium",
            category=subtask.category or "general",
            phase=stage.phase if stage else "ideation",
            due_date=subtask.due_date,
            is_blocked=subtask.is_blocked or False,
            blocking_reason=subtask.notes if subtask.is_blocked else None,
            assignee=str(subtask.assignee_id) if subtask.assignee_id else None,
            created_at=subtask.created_at or datetime.utcnow(),
            updated_at=subtask.updated_at or datetime.utcnow()
        )
        ai_tasks.append(ai_task)
    
    # Get current phase
    workflow_service = WorkflowService(db)
    progress = await workflow_service.get_frontend_workflow_progress(event_id)
    current_phase = progress.get("current_phase", "ideation")
    
    # Run AI analysis
    analyzer = AIWorkflowAnalyzer()
    analysis_result = await analyzer.analyze_workflow(
        tasks=ai_tasks,
        event_date=event.scheduled_date,
        current_phase=current_phase
    )
    
    return {
        "event_id": event_id,
        "analysis_timestamp": datetime.utcnow().isoformat(),
        **analysis_result
    }


@router.get("/events/{event_id}/workflow/ai-insights")
async def get_ai_insights(
    event_id: int,
    insight_type: Optional[str] = Query(None, description="Filter by insight type: suggestion, warning, tip, prediction"),
    category: Optional[str] = Query(None, description="Filter by category: priority, timeline, resources, dependencies, quality"),
    current_user: User = Depends(bypass_admin_check),
    db: AsyncSession = Depends(get_db)
):
    """
    Get filtered AI insights for the workflow.
    
    Allows filtering insights by type and category for more focused recommendations.
    """
    from app.models.workflow_models import WorkflowSubtask, WorkflowStage
    
    # Get event
    event_result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    event = event_result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Get all stages and subtasks
    stages_result = await db.execute(
        select(WorkflowStage).where(WorkflowStage.event_id == event_id)
    )
    stages = stages_result.scalars().all()
    
    stage_ids = [s.id for s in stages]
    if stage_ids:
        subtasks_result = await db.execute(
            select(WorkflowSubtask).where(WorkflowSubtask.stage_id.in_(stage_ids))
        )
        subtasks = subtasks_result.scalars().all()
    else:
        subtasks = []
    
    # Convert to AI tasks
    ai_tasks = []
    for subtask in subtasks:
        stage = next((s for s in stages if s.id == subtask.stage_id), None)
        ai_tasks.append(AITask(
            id=str(subtask.id),
            title=subtask.title,
            description=subtask.description or "",
            status=subtask.status,
            priority=subtask.priority or "medium",
            category=subtask.category or "general",
            phase=stage.phase if stage else "ideation",
            due_date=subtask.due_date,
            is_blocked=subtask.is_blocked or False,
            blocking_reason=subtask.notes if subtask.is_blocked else None,
            assignee=str(subtask.assignee_id) if subtask.assignee_id else None,
            created_at=subtask.created_at or datetime.utcnow(),
            updated_at=subtask.updated_at or datetime.utcnow()
        ))
    
    # Run analysis
    analyzer = AIWorkflowAnalyzer()
    analysis_result = await analyzer.analyze_workflow(
        tasks=ai_tasks,
        event_date=event.scheduled_date,
        current_phase="ideation"
    )
    
    # Filter insights
    insights = analysis_result.get("insights", [])
    
    if insight_type:
        insights = [i for i in insights if i.get("type") == insight_type]
    
    if category:
        insights = [i for i in insights if i.get("category") == category]
    
    return {
        "event_id": event_id,
        "insights": insights,
        "total_count": len(insights),
        "health_score": analysis_result.get("health_score", 0)
    }


@router.get("/events/{event_id}/workflow/ai-priorities")
async def get_ai_priority_recommendations(
    event_id: int,
    current_user: User = Depends(bypass_admin_check),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI-generated priority recommendations for tasks.
    
    Analyzes all incomplete tasks and suggests priority adjustments
    based on timeline, dependencies, and event proximity.
    """
    from app.models.workflow_models import WorkflowSubtask, WorkflowStage
    
    # Get event
    event_result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    event = event_result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Get stages and subtasks
    stages_result = await db.execute(
        select(WorkflowStage).where(WorkflowStage.event_id == event_id)
    )
    stages = stages_result.scalars().all()
    
    stage_ids = [s.id for s in stages]
    if stage_ids:
        subtasks_result = await db.execute(
            select(WorkflowSubtask).where(WorkflowSubtask.stage_id.in_(stage_ids))
        )
        subtasks = subtasks_result.scalars().all()
    else:
        subtasks = []
    
    # Convert to AI tasks
    ai_tasks = []
    for subtask in subtasks:
        stage = next((s for s in stages if s.id == subtask.stage_id), None)
        ai_tasks.append(AITask(
            id=str(subtask.id),
            title=subtask.title,
            description=subtask.description or "",
            status=subtask.status,
            priority=subtask.priority or "medium",
            category=subtask.category or "general",
            phase=stage.phase if stage else "ideation",
            due_date=subtask.due_date,
            is_blocked=subtask.is_blocked or False,
            blocking_reason=subtask.notes if subtask.is_blocked else None,
            assignee=str(subtask.assignee_id) if subtask.assignee_id else None,
            created_at=subtask.created_at or datetime.utcnow(),
            updated_at=subtask.updated_at or datetime.utcnow()
        ))
    
    # Get recommendations
    analyzer = AIWorkflowAnalyzer()
    analysis_result = await analyzer.analyze_workflow(
        tasks=ai_tasks,
        event_date=event.scheduled_date,
        current_phase="ideation"
    )
    
    recommendations = analysis_result.get("priority_recommendations", [])
    
    # Add task details to recommendations
    task_map = {t.id: t for t in ai_tasks}
    for rec in recommendations:
        task = task_map.get(rec.get("task_id"))
        if task:
            rec["task_title"] = task.title
            rec["current_priority"] = task.priority
            rec["current_status"] = task.status
    
    return {
        "event_id": event_id,
        "recommendations": recommendations,
        "total_count": len(recommendations),
        "timeline_prediction": analysis_result.get("timeline_prediction")
    }


@router.get("/events/{event_id}/workflow/ai-health")
async def get_workflow_health(
    event_id: int,
    current_user: User = Depends(bypass_admin_check),
    db: AsyncSession = Depends(get_db)
):
    """
    Get quick workflow health assessment.
    
    Returns a summary of workflow health including:
    - Overall health score (0-100)
    - Critical issues count
    - Warning count
    - Timeline risk level
    """
    from app.models.workflow_models import WorkflowSubtask, WorkflowStage
    
    # Get event
    event_result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    event = event_result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Get stages and subtasks
    stages_result = await db.execute(
        select(WorkflowStage).where(WorkflowStage.event_id == event_id)
    )
    stages = stages_result.scalars().all()
    
    stage_ids = [s.id for s in stages]
    if stage_ids:
        subtasks_result = await db.execute(
            select(WorkflowSubtask).where(WorkflowSubtask.stage_id.in_(stage_ids))
        )
        subtasks = subtasks_result.scalars().all()
    else:
        subtasks = []
    
    # Convert to AI tasks
    ai_tasks = []
    for subtask in subtasks:
        stage = next((s for s in stages if s.id == subtask.stage_id), None)
        ai_tasks.append(AITask(
            id=str(subtask.id),
            title=subtask.title,
            description=subtask.description or "",
            status=subtask.status,
            priority=subtask.priority or "medium",
            category=subtask.category or "general",
            phase=stage.phase if stage else "ideation",
            due_date=subtask.due_date,
            is_blocked=subtask.is_blocked or False,
            blocking_reason=subtask.notes if subtask.is_blocked else None,
            assignee=str(subtask.assignee_id) if subtask.assignee_id else None,
            created_at=subtask.created_at or datetime.utcnow(),
            updated_at=subtask.updated_at or datetime.utcnow()
        ))
    
    # Get health score
    analyzer = AIWorkflowAnalyzer()
    health_score = analyzer._calculate_workflow_health(ai_tasks, event.scheduled_date)
    
    # Get summary insights
    analysis_result = await analyzer.analyze_workflow(
        tasks=ai_tasks,
        event_date=event.scheduled_date,
        current_phase="ideation"
    )
    
    insights = analysis_result.get("insights", [])
    critical_issues = [i for i in insights if i.get("impact") in ["critical", "high"] and i.get("type") == "warning"]
    warnings = [i for i in insights if i.get("type") == "warning"]
    suggestions = [i for i in insights if i.get("type") == "suggestion"]
    
    # Determine health status
    if health_score >= 90:
        health_status = "excellent"
    elif health_score >= 70:
        health_status = "good"
    elif health_score >= 50:
        health_status = "needs_attention"
    else:
        health_status = "critical"
    
    return {
        "event_id": event_id,
        "health_score": health_score,
        "health_status": health_status,
        "critical_issues": len(critical_issues),
        "warnings": len(warnings),
        "suggestions": len(suggestions),
        "timeline_risk": analysis_result.get("timeline_prediction", {}).get("risk_level", "unknown") if analysis_result.get("timeline_prediction") else "unknown",
        "summary": analysis_result.get("summary", ""),
        "last_analyzed": datetime.utcnow().isoformat()
    }

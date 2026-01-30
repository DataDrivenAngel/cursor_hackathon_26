"""
Workflow Service - Progress calculation and workflow management.
"""
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.database_models import Event, User, Task
from app.models.workflow_models import (
    EventWorkflowProgress, WorkflowStage, WorkflowSubtask, 
    EventMilestone, WorkflowPhase, PhaseStatus, TaskStatus
)
from app.services.workflow_templates import (
    PHASE_CONFIG, SUBTASK_TEMPLATES, MILESTONE_TEMPLATES,
    generate_milestones_for_event
)


class WorkflowService:
    """Service for managing event workflows."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def initialize_workflow(self, event_id: int, event_type: str = "meetup") -> EventWorkflowProgress:
        """Initialize workflow for a new event."""
        
        # Create workflow progress tracker
        progress = EventWorkflowProgress(
            event_id=event_id,
            current_phase="ideation",
            completion_percentage=0.0,
            is_on_track=True,
            total_tasks=0,
            completed_tasks=0,
            total_milestones=0,
            completed_milestones=0
        )
        self.db.add(progress)
        
        # Get event to calculate dates
        event_result = await self.db.execute(
            select(Event).where(Event.id == event_id)
        )
        event = event_result.scalar_one_or_none()
        
        if not event:
            raise ValueError("Event not found")
        
        # Create workflow stages for each phase
        for phase, config in PHASE_CONFIG.items():
            stage = WorkflowStage(
                event_id=event_id,
                phase=phase,
                status="pending",
                progress=0.0,
                total_tasks=0,
                completed_tasks=0,
                order=config["order"],
                due_date=event.scheduled_date - timedelta(days=config.get("buffer_days", 7))
            )
            self.db.add(stage)
        
        # Create milestones
        milestones_data = generate_milestones_for_event(
            event_type, 
            event.scheduled_date or datetime.utcnow()
        )
        
        for milestone_data in milestones_data:
            milestone = EventMilestone(**milestone_data)
            self.db.add(milestone)
        
        await self.db.commit()
        await self.db.refresh(progress)
        
        return progress
    
    async def calculate_progress(self, event_id: int) -> Dict[str, Any]:
        """Calculate comprehensive workflow progress."""
        
        # Get all stages
        stages_result = await self.db.execute(
            select(WorkflowStage)
            .options(selectinload(WorkflowSubtask))
            .where(WorkflowStage.event_id == event_id)
            .order_by(WorkflowStage.order)
        )
        stages = stages_result.scalars().all()
        
        # Get all subtasks
        subtasks_result = await self.db.execute(
            select(WorkflowSubtask)
            .where(WorkflowSubtask.stage_id.in_([s.id for s in stages]))
        )
        subtasks = subtasks_result.scalars().all()
        
        # Get milestones
        milestones_result = await self.db.execute(
            select(EventMilestone)
            .where(EventMilestone.event_id == event_id)
            .order_by(EventMilestone.due_date)
        )
        milestones = milestones_result.scalars().all()
        
        # Get event for date calculations
        event_result = await self.db.execute(
            select(Event).where(Event.id == event_id)
        )
        event = event_result.scalar_one_or_none()
        
        # Calculate phase progress
        phase_progress = {}
        total_weighted_progress = 0
        total_weight = 0
        
        for stage in stages:
            stage_subtasks = [s for s in subtasks if s.stage_id == stage.id]
            completed = sum(1 for s in stage_subtasks if s.status in ["done", "review"])
            total = len(stage_subtasks)
            
            stage.total_tasks = total
            stage.completed_tasks = completed
            
            if total > 0:
                stage.progress = (completed / total) * 100
            else:
                stage.progress = 0
            
            if stage.status == "completed":
                stage.progress = 100
            
            # Calculate weighted progress
            weight = PHASE_CONFIG.get(stage.phase, {}).get("weight", 0)
            total_weighted_progress += stage.progress * (weight / 100)
            total_weight += weight
            
            phase_progress[stage.phase] = {
                "status": stage.status,
                "progress": stage.progress,
                "total_tasks": total,
                "completed_tasks": completed,
                "color": PHASE_CONFIG.get(stage.phase, {}).get("color", "#888"),
                "icon": PHASE_CONFIG.get(stage.phase, {}).get("icon", "📌"),
                "name": PHASE_CONFIG.get(stage.phase, {}).get("name", stage.phase)
            }
        
        # Calculate overall progress
        overall_progress = (total_weighted_progress / total_weight * 100) if total_weight > 0 else 0
        
        # Count subtasks by status
        todo_count = sum(1 for s in subtasks if s.status == "todo")
        in_progress_count = sum(1 for s in subtasks if s.status == "in_progress")
        review_count = sum(1 for s in subtasks if s.status == "review")
        done_count = sum(1 for s in subtasks if s.status == "done")
        blocked_count = sum(1 for s in subtasks if s.status == "blocked")
        
        # Calculate days
        now = datetime.utcnow()
        if event and event.scheduled_date:
            days_until = (event.scheduled_date - now).days
            days_into = (now - event.created_at).days if event.created_at else 0
        else:
            days_until = 0
            days_into = 0
        
        # Find upcoming milestone
        upcoming_milestone = None
        for milestone in milestones:
            if not milestone.is_completed and milestone.due_date > now:
                upcoming_milestone = milestone.due_date.isoformat()
                break
        
        # Check if on track
        is_on_track = await self._check_on_track(event_id, subtasks, days_until)
        
        # Generate suggestions and warnings
        suggestions, warnings = await self._generate_insights(
            event_id, subtasks, milestones, days_until, phase_progress
        )
        
        # Update progress record
        progress_result = await self.db.execute(
            select(EventWorkflowProgress)
            .where(EventWorkflowProgress.event_id == event_id)
        )
        progress = progress_result.scalar_one_or_none()
        
        if progress:
            progress.completion_percentage = overall_progress
            progress.current_phase = self._get_current_phase(phase_progress)
            progress.total_tasks = len(subtasks)
            progress.completed_tasks = done_count
            progress.overdue_tasks = sum(1 for s in subtasks if s.due_date and s.due_date < now and s.status not in ["done", "blocked"])
            progress.blocked_tasks = blocked_count
            progress.days_until_event = days_until
            progress.days_into_planning = days_into
            progress.total_milestones = len(milestones)
            progress.completed_milestones = sum(1 for m in milestones if m.is_completed)
            progress.upcoming_milestone = upcoming_milestone
            progress.is_on_track = is_on_track
            progress.suggestions = suggestions
            progress.warnings = warnings
            progress.last_updated = datetime.utcnow()
            
            await self.db.commit()
        
        return {
            "overall_progress": overall_progress,
            "current_phase": self._get_current_phase(phase_progress),
            "phases": phase_progress,
            "tasks": {
                "total": len(subtasks),
                "todo": todo_count,
                "in_progress": in_progress_count,
                "review": review_count,
                "done": done_count,
                "blocked": blocked_count
            },
            "milestones": {
                "total": len(milestones),
                "completed": sum(1 for m in milestones if m.is_completed),
                "upcoming": upcoming_milestone
            },
            "timeline": {
                "days_until_event": days_until,
                "days_into_planning": days_into,
                "is_on_track": is_on_track
            },
            "suggestions": suggestions,
            "warnings": warnings
        }
    
    def _get_current_phase(self, phase_progress: Dict[str, Any]) -> str:
        """Determine current active phase."""
        for phase in ["ideation", "logistics", "marketing", "preparation", "execution", "review"]:
            if phase in phase_progress:
                status = phase_progress[phase]["status"]
                if status == "in_progress":
                    return phase
                if status == "pending" and phase_progress[phase]["progress"] > 0:
                    return phase
        
        # Default to ideation if nothing started
        return "ideation"
    
    async def _check_on_track(
        self, 
        event_id: int, 
        subtasks: List[WorkflowSubtask], 
        days_until: int
    ) -> bool:
        """Check if event is on track based on progress and deadlines."""
        
        # Check for blocked tasks
        blocked = [s for s in subtasks if s.status == "blocked"]
        if blocked:
            return False
        
        # Check for overdue tasks
        now = datetime.utcnow()
        overdue = [s for s in subtasks if s.due_date and s.due_date < now and s.status not in ["done"]]
        if len(overdue) > 3:
            return False
        
        # Check if too many tasks remain
        remaining = [s for s in subtasks if s.status not in ["done"]]
        if days_until > 0 and len(remaining) > days_until * 2:
            return False
        
        return True
    
    async def _generate_insights(
        self,
        event_id: int,
        subtasks: List[WorkflowSubtask],
        milestones: List[EventMilestone],
        days_until: int,
        phase_progress: Dict[str, Any]
    ) -> tuple:
        """Generate AI-like suggestions and warnings."""
        
        suggestions = []
        warnings = []
        now = datetime.utcnow()
        
        # Check for blocked tasks
        blocked = [s for s in subtasks if s.status == "blocked"]
        if blocked:
            warnings.append(f"{len(blocked)} task(s) are blocked. Resolve dependencies to continue.")
            suggestions.append("Review blocked tasks and remove obstacles or reassign.")
        
        # Check for overdue tasks
        overdue = [s for s in subtasks if s.due_date and s.due_date < now and s.status not in ["done"]]
        if overdue:
            warnings.append(f"{len(overdue)} task(s) are overdue.")
            suggestions.append("Prioritize completing overdue tasks to stay on track.")
        
        # Check marketing progress
        if phase_progress.get("marketing", {}).get("progress", 0) < 50 and days_until < 30:
            warnings.append("Marketing is behind schedule with less than 30 days to go.")
            suggestions.append("Increase marketing efforts and launch campaigns soon.")
        
        # Check speaker confirmations
        speaker_tasks = [s for s in subtasks if "speaker" in s.title.lower() and "confirm" in s.title.lower()]
        incomplete_speakers = [s for s in speaker_tasks if s.status != "done"]
        if incomplete_speakers and days_until < 21:
            warnings.append(f"{len(incomplete_speakers)} speaker confirmation(s) pending.")
            suggestions.append("Send follow-up emails to unconfirmed speakers.")
        
        # Check venue booking
        venue_tasks = [s for s in subtasks if "venue" in s.title.lower() and "book" in s.title.lower()]
        if venue_tasks and venue_tasks[0].status != "done" and days_until < 45:
            warnings.append("Venue not yet booked with less than 45 days remaining.")
            suggestions.append("Book a venue immediately to secure your date.")
        
        # Check upcoming milestones
        upcoming_milestones = [m for m in milestones if not m.is_completed and m.due_date > now]
        if upcoming_milestones:
            next_milestone = min(upcoming_milestones, key=lambda m: m.due_date)
            days_to_milestone = (next_milestone.due_date - now).days
            if days_to_milestone < 7:
                warnings.append(f"Next milestone '{next_milestone.title}' is in {days_to_milestone} days!")
                suggestions.append(f"Focus on completing tasks related to: {next_milestone.title}")
        
        # Positive reinforcement
        if phase_progress.get("execution", {}).get("progress", 0) == 100:
            suggestions.append("🎉 All preparation complete! You're ready for event day!")
        
        if all(phase_progress.get(p, {}).get("progress", 0) > 50 for p in ["ideation", "logistics"]):
            suggestions.append("Great progress on planning and logistics! Keep the momentum going.")
        
        return suggestions[:5], warnings[:5]  # Limit to 5 each
    
    async def update_subtask_status(
        self, 
        subtask_id: int, 
        status: str,
        user_id: int = None
    ) -> WorkflowSubtask:
        """Update a subtask status."""
        
        result = await self.db.execute(
            select(WorkflowSubtask).where(WorkflowSubtask.id == subtask_id)
        )
        subtask = result.scalar_one_or_none()
        
        if not subtask:
            raise ValueError("Subtask not found")
        
        subtask.status = status
        
        if status == "done":
            subtask.completed_at = datetime.utcnow()
            subtask.completed_by = user_id
        
        await self.db.commit()
        await self.db.refresh(subtask)
        
        # Recalculate progress
        await self.calculate_progress(subtask.stage_id)
        
        return subtask
    
    async def get_workflow_summary(self, event_id: int) -> Dict[str, Any]:
        """Get complete workflow summary for an event."""
        
        # Get progress
        progress_data = await self.calculate_progress(event_id)
        
        # Get stages with subtasks
        stages_result = await self.db.execute(
            select(WorkflowStage)
            .options(
                selectinload(WorkflowSubtask),
                selectinload(WorkflowStage).selectinload(EventMilestone)
            )
            .where(WorkflowStage.event_id == event_id)
            .order_by(WorkflowStage.order)
        )
        stages = stages_result.scalars().all()
        
        # Build detailed summary
        stages_detail = []
        for stage in stages:
            stage_subtasks = stage.subtasks if stage.subtasks else []
            
            # Group subtasks by category
            categories = {}
            for subtask in stage_subtasks:
                cat = subtask.category or "general"
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append({
                    "id": subtask.id,
                    "title": subtask.title,
                    "status": subtask.status,
                    "priority": subtask.priority,
                    "due_date": subtask.due_date.isoformat() if subtask.due_date else None,
                    "assignee_id": subtask.assignee_id
                })
            
            stage_milestones = [m for m in (getattr(stage, 'milestones', []) or [])]
            
            stages_detail.append({
                "id": stage.id,
                "phase": stage.phase,
                "name": PHASE_CONFIG.get(stage.phase, {}).get("name", stage.phase),
                "icon": PHASE_CONFIG.get(stage.phase, {}).get("icon", "📌"),
                "color": PHASE_CONFIG.get(stage.phase, {}).get("color", "#888"),
                "status": stage.status,
                "progress": stage.progress,
                "categories": categories,
                "milestones": [m.to_dict() for m in stage_milestones]
            })
        
        return {
            "summary": progress_data,
            "stages": stages_detail
        }

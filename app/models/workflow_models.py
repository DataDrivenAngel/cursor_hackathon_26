"""
Workflow Models - Event Planning Workflow with Subtasks
Comprehensive workflow tracking for event management.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float, Enum
from sqlalchemy.orm import relationship
from app.database.connection import Base
import enum


class WorkflowPhase(enum.Enum):
    """Main workflow phases for event planning."""
    IDEATION = "ideation"
    LOGISTICS = "logistics"
    MARKETING = "marketing"
    PREPARATION = "preparation"
    EXECUTION = "execution"
    REVIEW = "review"


class PhaseStatus(enum.Enum):
    """Status of a workflow phase."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class TaskStatus(enum.Enum):
    """Task status enum."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"


class TaskPriority(enum.Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventWorkflowProgress(Base):
    """Tracks overall workflow progress for an event."""
    __tablename__ = "event_workflow_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), unique=True, nullable=False)
    
    # Current state
    current_phase = Column(String(50), default="ideation")
    completion_percentage = Column(Float, default=0.0)
    is_on_track = Column(Boolean, default=True)
    
    # Task metrics
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    overdue_tasks = Column(Integer, default=0)
    blocked_tasks = Column(Integer, default=0)
    
    # Timeline metrics
    days_until_event = Column(Integer)
    days_into_planning = Column(Integer, default=0)
    
    # Milestone metrics
    total_milestones = Column(Integer, default=0)
    completed_milestones = Column(Integer, default=0)
    upcoming_milestone = Column(DateTime)
    
    # AI suggestions
    blockers = Column(JSON)  # List of current blockers
    suggestions = Column(JSON)  # AI-generated suggestions
    warnings = Column(JSON)  # Warning messages
    
    # Timestamps
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationship
    event = relationship("Event", back_populates="workflow_progress")
    
    def to_dict(self):
        return {
            "id": self.id,
            "event_id": self.event_id,
            "current_phase": self.current_phase,
            "completion_percentage": self.completion_percentage,
            "is_on_track": self.is_on_track,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "overdue_tasks": self.overdue_tasks,
            "blocked_tasks": self.blocked_tasks,
            "days_until_event": self.days_until_event,
            "total_milestones": self.total_milestones,
            "completed_milestones": self.completed_milestones,
            "blockers": self.blockers or [],
            "suggestions": self.suggestions or [],
            "warnings": self.warnings or [],
        }


class WorkflowStage(Base):
    """Individual workflow stage for an event."""
    __tablename__ = "workflow_stages"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    phase = Column(String(50), nullable=False)  # ideation, logistics, etc.
    
    status = Column(String(20), default="pending")
    progress = Column(Float, default=0.0)  # 0-100 percentage
    
    # Task counts
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    
    # Timestamps
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    due_date = Column(DateTime)
    
    # Notes
    notes = Column(Text)
    blockers = Column(Text)
    
    # Order for display
    order = Column(Integer, default=0)
    
    # Relationship
    event = relationship("Event", back_populates="workflow_stages")
    subtasks = relationship("WorkflowSubtask", back_populates="stage", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "event_id": self.event_id,
            "phase": self.phase,
            "status": self.status,
            "progress": self.progress,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "notes": self.notes,
            "blockers": self.blockers,
        }


class WorkflowSubtask(Base):
    """Detailed subtasks within each workflow stage."""
    __tablename__ = "workflow_subtasks"
    
    id = Column(Integer, primary_key=True, index=True)
    stage_id = Column(Integer, ForeignKey("workflow_stages.id"), nullable=False)
    
    # Task details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50))  # For grouping subtasks
    
    # Status and priority
    status = Column(String(20), default="todo")
    priority = Column(String(20), default="medium")
    
    # Dependencies
    depends_on = Column(Integer, ForeignKey("workflow_subtasks.id"), nullable=True)
    is_blocked = Column(Boolean, default=False)
    
    # Assignment
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timing
    due_date = Column(DateTime)
    estimated_hours = Column(Float)
    actual_hours = Column(Float)
    
    # Completion
    completed_at = Column(DateTime)
    completed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Order
    order = Column(Integer, default=0)
    
    # Notes
    notes = Column(Text)
    attachments = Column(JSON)  # List of file URLs
    
    # Relationship
    stage = relationship("WorkflowStage", back_populates="subtasks")
    assignee = relationship("User", foreign_keys=[assignee_id])
    dependency = relationship("WorkflowSubtask", remote_side=[id], backref="dependents")
    
    def to_dict(self):
        return {
            "id": self.id,
            "stage_id": self.stage_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "status": self.status,
            "priority": self.priority,
            "depends_on": self.depends_on,
            "is_blocked": self.is_blocked,
            "assignee_id": self.assignee_id,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "estimated_hours": self.estimated_hours,
            "actual_hours": self.actual_hours,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "order": self.order,
            "notes": self.notes,
        }


class EventMilestone(Base):
    """Key milestones for event planning."""
    __tablename__ = "event_milestones"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    
    # Milestone details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    milestone_type = Column(String(50))  # deadline, deliverable, decision_point
    
    # Timing
    due_date = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    
    # Status
    is_completed = Column(Boolean, default=False)
    is_critical = Column(Boolean, default=False)  # Critical path milestone
    
    # Impact
    impact_description = Column(Text)  # What happens if missed
    
    # Order
    order = Column(Integer, default=0)
    
    # Relationship
    event = relationship("Event", back_populates="milestones")
    
    def to_dict(self):
        return {
            "id": self.id,
            "event_id": self.event_id,
            "title": self.title,
            "description": self.description,
            "milestone_type": self.milestone_type,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "is_completed": self.is_completed,
            "is_critical": self.is_critical,
            "impact_description": self.impact_description,
            "order": self.order,
        }


class WorkflowTemplate(Base):
    """Predefined workflow templates for different event types."""
    __tablename__ = "workflow_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Template details
    name = Column(String(100), nullable=False)
    description = Column(Text)
    event_type = Column(String(50))  # meetup, workshop, conference, hackathon
    
    # Configuration
    phases = Column(JSON)  # List of phase configurations
    default_tasks = Column(JSON)  # Default task templates
    default_milestones = Column(JSON)  # Default milestones
    
    # Timing defaults
    typical_duration_days = Column(Integer)  # How long event planning typically takes
    marketing_start_days_before = Column(Integer)  # Days before event to start marketing
    
    # Usage
    usage_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "event_type": self.event_type,
            "phases": self.phases,
            "typical_duration_days": self.typical_duration_days,
            "marketing_start_days_before": self.marketing_start_days_before,
            "usage_count": self.usage_count,
        }


# Update Event model to include new relationships
def update_event_model():
    """Add new relationships to Event model."""
    # Add these relationships to the Event class:
    """
    # Workflow relationships
    workflow_progress = relationship("EventWorkflowProgress", uselist=False, cascade="all, delete-orphan")
    workflow_stages = relationship("WorkflowStage", back_populates="event", cascade="all, delete-orphan")
    milestones = relationship("EventMilestone", back_populates="event", cascade="all, delete-orphan")
    
    # New event fields
    workflow_phase = Column(String(50), default="ideation")
    event_format = Column(String(50))  # in_person, virtual, hybrid
    max_attendees = Column(Integer)
    registration_deadline = Column(DateTime)
    is_featured = Column(Boolean, default=False)
    cover_image_url = Column(String(500))
    """
    pass

"""
SQLAlchemy database models for the Meetup Organizing Information Support System.
Designed in 4th Normal Form with history tracking.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.connection import Base


class User(Base):
    """User accounts with role-based permissions."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    role = Column(String(20), default="assistant")  # admin, organizer, assistant, volunteer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    organized_events = relationship("Event", back_populates="creator", foreign_keys="Event.created_by")
    organizers = relationship("Organizer", back_populates="user")
    tasks_created = relationship("Task", back_populates="creator", foreign_keys="Task.created_by")
    agent_workflows = relationship("AgentWorkflow", back_populates="user")
    marketing_materials = relationship("MarketingMaterial", back_populates="creator")
    permissions_granted = relationship("Permission", back_populates="granted_by_user", foreign_keys="[Permission.granted_by]")
    permissions = relationship("Permission", back_populates="user", foreign_keys="[Permission.user_id]")
    venues = relationship("Venue", back_populates="creator")
    sponsors = relationship("Sponsor", back_populates="creator")
    speakers = relationship("Speaker", back_populates="creator")


class Event(Base):
    """Event information with scheduling, topics, and status."""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    topic = Column(String(100))
    status = Column(String(20), default="planning")  # planning, scheduled, completed, cancelled
    meetup_id = Column(String(100))
    luma_id = Column(String(100))
    image_url = Column(String(500))  # AI-generated event image
    scheduled_date = Column(DateTime)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Workflow fields
    workflow_phase = Column(String(50), default="ideation")
    event_format = Column(String(50))  # in_person, virtual, hybrid
    max_attendees = Column(Integer)
    registration_deadline = Column(DateTime)
    is_featured = Column(Boolean, default=False)
    cover_image_url = Column(String(500))
    
    # Relationships
    creator = relationship("User", back_populates="organized_events", foreign_keys=[created_by])
    venue = relationship("Venue", back_populates="events")
    organizers = relationship("Organizer", back_populates="event", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="event", cascade="all, delete-orphan")
    event_sponsors = relationship("EventSponsor", back_populates="event", cascade="all, delete-orphan")
    event_attendees = relationship("EventAttendee", back_populates="event", cascade="all, delete-orphan")
    marketing_materials = relationship("MarketingMaterial", back_populates="event", cascade="all, delete-orphan")
    agent_workflows = relationship("AgentWorkflow", back_populates="event")
    
    # Workflow relationships
    workflow_progress = relationship("EventWorkflowProgress", uselist=False, cascade="all, delete-orphan")
    workflow_stages = relationship("WorkflowStage", back_populates="event", cascade="all, delete-orphan")
    milestones = relationship("EventMilestone", back_populates="event", cascade="all, delete-orphan")


class Organizer(Base):
    """Link users to events they organize (supports multiple organizers per event)."""
    __tablename__ = "organizers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    role = Column(String(20), default="assistant")  # primary, assistant
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="organizers")
    event = relationship("Event", back_populates="organizers")
    
    # Unique constraint for user-event combination
    __table_args__ = (
        UniqueConstraint("user_id", "event_id", name="uq_organizer_user_event"),
    )


class Venue(Base):
    """Known venues with research data."""
    __tablename__ = "venues"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    address = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100))
    country = Column(String(100), nullable=False)
    capacity = Column(Integer)
    amenities = Column(JSON)  # Store as JSON array
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    website = Column(String(500))
    research_data = Column(JSON)  # Store research results as JSON
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", back_populates="venues")
    events = relationship("Event", back_populates="venue")


class Speaker(Base):
    """Speaker information for events."""
    __tablename__ = "speakers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(255))
    bio = Column(Text)
    expertise = Column(JSON)  # Store as JSON array
    social_profiles = Column(JSON)  # Store as JSON object
    company = Column(String(200))
    role = Column(String(100))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", back_populates="speakers")


class Task(Base):
    """Kanban tasks for event planning."""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="todo")  # todo, in_progress, review, done
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    due_date = Column(DateTime)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    event = relationship("Event", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assignee_id])
    creator = relationship("User", back_populates="tasks_created", foreign_keys=[created_by])


class Sponsor(Base):
    """Sponsor information."""
    __tablename__ = "sponsors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(50))
    website = Column(String(500))
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", back_populates="sponsors")
    event_sponsors = relationship("EventSponsor", back_populates="sponsor", cascade="all, delete-orphan")


class EventSponsor(Base):
    """Link sponsors to events with sponsorship details."""
    __tablename__ = "event_sponsors"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    sponsor_id = Column(Integer, ForeignKey("sponsors.id"), nullable=False)
    sponsorship_level = Column(String(50))  # gold, silver, bronze, etc.
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    event = relationship("Event", back_populates="event_sponsors")
    sponsor = relationship("Sponsor", back_populates="event_sponsors")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint("event_id", "sponsor_id", name="uq_event_sponsor"),
    )


class AgentWorkflow(Base):
    """Agentic workflow execution history."""
    __tablename__ = "agent_workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_type = Column(String(50), nullable=False)  # venue_research, speaker_research
    status = Column(String(20), default="pending")  # pending, running, completed, failed, cancelled
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    input_data = Column(JSON, nullable=False)  # Store request parameters
    output_data = Column(JSON)  # Store results
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    event = relationship("Event", back_populates="agent_workflows")
    user = relationship("User", back_populates="agent_workflows")


class MarketingMaterial(Base):
    """Generated marketing content for events."""
    __tablename__ = "marketing_materials"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    material_type = Column(String(50), nullable=False)  # post, email, social
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    edited_at = Column(DateTime)
    
    # Relationships
    event = relationship("Event", back_populates="marketing_materials")
    creator = relationship("User", back_populates="marketing_materials")


class Permission(Base):
    """Role-based access control permissions."""
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resource_type = Column(String(50), nullable=False)  # event, system
    resource_id = Column(Integer, nullable=True)  # Null for system-wide permissions
    permission_level = Column(String(20), nullable=False)  # read, write, admin
    granted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    granted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="permissions", foreign_keys=[user_id])
    granted_by_user = relationship("User", back_populates="permissions_granted", foreign_keys=[granted_by])


class AttendeeProfile(Base):
    """Global attendee profiles with enrichment data."""
    __tablename__ = "attendee_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(255), nullable=False)
    company = Column(String(200))
    role = Column(String(100))
    bio = Column(Text)
    social_profiles = Column(JSON)  # LinkedIn, Twitter, etc.
    enriched_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    event_attendees = relationship("EventAttendee", back_populates="attendee_profile")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint("email", name="uq_attendee_email"),
    )


class EventAttendee(Base):
    """Link attendees to specific events with registration status."""
    __tablename__ = "event_attendees"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    attendee_profile_id = Column(Integer, ForeignKey("attendee_profiles.id"), nullable=False)
    registration_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="registered")  # registered, attended, cancelled
    
    # Relationships
    event = relationship("Event", back_populates="event_attendees")
    attendee_profile = relationship("AttendeeProfile", back_populates="event_attendees")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint("event_id", "attendee_profile_id", name="uq_event_attendee"),
    )


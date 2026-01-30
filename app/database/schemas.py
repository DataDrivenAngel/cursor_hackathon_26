"""
Pydantic schemas for API request/response validation.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ==================== User Schemas ====================

class UserBase(BaseModel):
    """Base user schema."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr]
    role: Optional[str]


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Event Schemas ====================

class EventBase(BaseModel):
    """Base event schema."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    topic: Optional[str] = None


class EventCreate(EventBase):
    """Schema for creating an event."""
    scheduled_date: Optional[datetime] = None
    venue_id: Optional[int] = None


class EventUpdate(BaseModel):
    """Schema for updating an event."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str]
    topic: Optional[str]
    status: Optional[str]
    scheduled_date: Optional[datetime] = None
    venue_id: Optional[int] = None
    meetup_id: Optional[str] = None
    luma_id: Optional[str] = None


class EventResponse(EventBase):
    """Schema for event response."""
    id: int
    status: str
    scheduled_date: Optional[datetime]
    venue_id: Optional[int]
    meetup_id: Optional[str]
    luma_id: Optional[str]
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ==================== Organizer Schemas ====================

class OrganizerBase(BaseModel):
    """Base organizer schema."""
    user_id: int
    event_id: int


class OrganizerCreate(OrganizerBase):
    """Schema for creating an organizer."""
    role: str = "assistant"


class OrganizerResponse(OrganizerBase):
    """Schema for organizer response."""
    id: int
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Venue Schemas ====================

class VenueBase(BaseModel):
    """Base venue schema."""
    name: str = Field(..., min_length=1, max_length=200)
    address: str = Field(..., min_length=1, max_length=500)
    city: str = Field(..., min_length=1, max_length=100)
    state: Optional[str] = None
    country: str = Field(..., min_length=1, max_length=100)


class VenueCreate(VenueBase):
    """Schema for creating a venue."""
    capacity: Optional[int] = None
    amenities: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None


class VenueUpdate(BaseModel):
    """Schema for updating a venue."""
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    capacity: Optional[int] = None
    amenities: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    research_data: Optional[str] = None


class VenueResponse(VenueBase):
    """Schema for venue response."""
    id: int
    capacity: Optional[int]
    amenities: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    website: Optional[str]
    research_data: Optional[str]
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Speaker Schemas ====================

class SpeakerBase(BaseModel):
    """Base speaker schema."""
    name: str = Field(..., min_length=1, max_length=200)


class SpeakerCreate(SpeakerBase):
    """Schema for creating a speaker."""
    email: Optional[EmailStr] = None
    bio: Optional[str] = None
    expertise: Optional[str] = None
    social_profiles: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None


class SpeakerUpdate(BaseModel):
    """Schema for updating a speaker."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    bio: Optional[str] = None
    expertise: Optional[str] = None
    social_profiles: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None


class SpeakerResponse(SpeakerBase):
    """Schema for speaker response."""
    id: int
    email: Optional[str]
    bio: Optional[str]
    expertise: Optional[str]
    social_profiles: Optional[str]
    company: Optional[str]
    role: Optional[str]
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Task Schemas ====================

class TaskBase(BaseModel):
    """Base task schema."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class TaskCreate(TaskBase):
    """Schema for creating a task."""
    event_id: int
    status: str = "todo"
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskResponse(TaskBase):
    """Schema for task response."""
    id: int
    event_id: int
    status: str
    assignee_id: Optional[int]
    due_date: Optional[datetime]
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ==================== Sponsor Schemas ====================

class SponsorBase(BaseModel):
    """Base sponsor schema."""
    name: str = Field(..., min_length=1, max_length=200)
    contact_email: EmailStr


class SponsorCreate(SponsorBase):
    """Schema for creating a sponsor."""
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None


class SponsorUpdate(BaseModel):
    """Schema for updating a sponsor."""
    name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None


class SponsorResponse(SponsorBase):
    """Schema for sponsor response."""
    id: int
    contact_phone: Optional[str]
    website: Optional[str]
    description: Optional[str]
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class EventSponsorCreate(BaseModel):
    """Schema for linking a sponsor to an event."""
    sponsorship_level: Optional[str] = None
    notes: Optional[str] = None


# ==================== Agent Workflow Schemas ====================

class AgentWorkflowBase(BaseModel):
    """Base agent workflow schema."""
    workflow_type: str
    event_id: Optional[int] = None


class AgentWorkflowCreate(AgentWorkflowBase):
    """Schema for creating an agent workflow."""
    input_data: str


class AgentWorkflowResponse(AgentWorkflowBase):
    """Schema for agent workflow response."""
    id: int
    status: str
    user_id: int
    input_data: str
    output_data: Optional[str]
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Marketing Material Schemas ====================

class MarketingMaterialBase(BaseModel):
    """Base marketing material schema."""
    material_type: str
    title: str
    content: str


class MarketingMaterialCreate(MarketingMaterialBase):
    """Schema for creating marketing material."""
    event_id: int


class MarketingMaterialUpdate(BaseModel):
    """Schema for updating marketing material."""
    title: Optional[str] = None
    content: Optional[str] = None


class MarketingMaterialResponse(MarketingMaterialBase):
    """Schema for marketing material response."""
    id: int
    event_id: int
    edited_at: Optional[datetime]
    created_by: int
    generated_at: datetime

    class Config:
        from_attributes = True


# ==================== Attendee Profile Schemas ====================

class AttendeeProfileBase(BaseModel):
    """Base attendee profile schema."""
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr


class AttendeeProfileCreate(AttendeeProfileBase):
    """Schema for creating an attendee profile."""
    company: Optional[str] = None
    role: Optional[str] = None
    bio: Optional[str] = None
    social_profiles: Optional[str] = None


class AttendeeProfileUpdate(BaseModel):
    """Schema for updating an attendee profile."""
    company: Optional[str] = None
    role: Optional[str] = None
    bio: Optional[str] = None
    social_profiles: Optional[str] = None
    enriched_at: Optional[datetime] = None


class AttendeeProfileResponse(AttendeeProfileBase):
    """Schema for attendee profile response."""
    id: int
    company: Optional[str]
    role: Optional[str]
    bio: Optional[str]
    social_profiles: Optional[str]
    enriched_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AttendeeEnrichRequest(BaseModel):
    """Schema for enriching an attendee."""
    name: str
    email: EmailStr


# ==================== Permission Schemas ====================

class PermissionBase(BaseModel):
    """Base permission schema."""
    user_id: int
    resource_type: str
    resource_id: Optional[int] = None
    permission_level: str


class PermissionCreate(PermissionBase):
    """Schema for creating a permission."""
    pass


class PermissionResponse(PermissionBase):
    """Schema for permission response."""
    id: int
    granted_by: int
    granted_at: datetime

    class Config:
        from_attributes = True


# ==================== Authentication Schemas ====================

class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data."""
    user_id: Optional[int] = None
    username: Optional[str] = None


# ==================== Venue Research Schemas ====================

class VenueResearchRequest(BaseModel):
    """Schema for venue research request."""
    capacity: Optional[int] = None
    location: str
    amenities: Optional[List[str]] = None
    event_type: Optional[str] = None


class VenueResearchResponse(BaseModel):
    """Schema for venue research response."""
    existing_venues: List[dict]
    new_venues: List[dict]
    recommendations: List[dict]


# ==================== Speaker Research Schemas ====================

class SpeakerResearchRequest(BaseModel):
    """Schema for speaker research request."""
    topic: str
    location: Optional[str] = None


class SpeakerResearchResponse(BaseModel):
    """Schema for speaker research response."""
    speakers: List[dict]
    outreach_templates: List[dict]
    enriched_attendees: List[dict]


# ==================== Topic Recommendation Schemas ====================

class TopicRecommendationResponse(BaseModel):
    """Schema for topic recommendation response."""
    topics: List[dict]

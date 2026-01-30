# Meetup Organizing Information Support System

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                            │
│   Minimal HTML/CSS + HTMX (SPA-like experience)                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                              │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Auth Router │  │ Events Router│  │ Agentic Workflows    │   │
│  └─────────────┘  └──────────────┘  └──────────────────────┘   │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Kanban API  │  │ Marketing    │  │ API Integrations     │   │
│  └─────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SQLite Database                              │
│  Relational schema: Users, Events, Organizers, Attendees,       │
│  Venues, Sponsors, Tasks, Permissions, Agent Workflows          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              External Services (Agent Tools)                     │
│  ┌──────────┐  ┌────────────┐  ┌──────────────┐  ┌────────┐   │
│  │ MiniMax  │  │ Perplexity │  │ Meetup API   │  │ Luma   │   │
│  │ API      │  │ Search     │  │              │  │ API    │   │
│  └──────────┘  └────────────┘  └──────────────┘  └────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Database Schema

### Core Tables
- **users**: User accounts with role-based permissions
- **events**: Event information with scheduling, topics, status
- **organizers**: Link users to events they organize
- **attendees**: Event attendees with enrichment data
- **venues**: Known venues with research data
- **sponsors**: Sponsor information and event associations
- **tasks**: Kanban tasks for event planning
- **permissions**: Role-based access control
- **agent_workflows**: Agentic workflow execution history
- **marketing_materials**: Generated marketing content

### Key Relationships
```
users ──┬──> organizers ──┬──> events
        │                 │
        └──> permissions  └──> tasks
                      │
                      └──> events (via venue research)
events ──┬──> attendees
         ├──> venues
         ├──> sponsors
         ├──> marketing_materials
         └──> tasks (kanban)
```

## Project Structure

```
cursor_hackathon_26/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration and API placeholders
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py          # SQLite connection management
│   │   └── schemas.py             # SQLAlchemy/Pydantic schemas
│   ├── models/
│   │   ├── __init__.py
│   │   └── database_models.py     # SQLAlchemy ORM models
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── router.py              # Auth endpoints (login, register)
│   │   ├── dependencies.py        # Auth dependencies and guards
│   │   └── utils.py               # Password hashing, JWT handling
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── events.py              # Event CRUD and topic recommendations
│   │   ├── venues.py              # Venue management and research
│   │   ├── speakers.py            # Speaker research and attendee enrichment
│   │   ├── marketing.py           # Marketing material generation
│   │   ├── kanban.py              # Kanban board operations
│   │   ├── integrations.py        # Meetup/Luma API integrations
│   │   └── admin.py               # Permission management
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py          # Base agent class with tool calling
│   │   ├── venue_research.py      # Venue research agent (Perplexity + MiniMax)
│   │   └── speaker_research.py    # Speaker research agent
│   ├── services/
│   │   ├── __init__.py
│   │   ├── topic_recommender.py   # Historical event-based recommendations
│   │   ├── meetup_service.py      # Meetup API integration
│   │   └── luma_service.py        # Luma API integration
│   └── templates/
│       ├── base.html              # Base HTML template
│       ├── auth.html              # Login/register forms
│       ├── dashboard.html         # Main dashboard with kanban
│       ├── events.html            # Event management
│       ├── venues.html            # Venue research interface
│       └── marketing.html         # Marketing material editor
├── static/
│   ├── style.css                  # Minimal CSS framework
│   └── htmx.min.js                # HTMX library
├── planning/
│   └── planning_prompt.md         # This planning document
└── requirements.txt               # Python dependencies
```

## Implementation Plan

### Phase 1: Foundation (Days 1-2)

#### 1.1 Setup and Database
- **File: `requirements.txt`**
  - fastapi, uvicorn, sqlalchemy, pydantic, python-jose, passlib
  - aiosqlite, python-multipart, httpx
  - Additional: openai (MiniMax compatible), perplexity-api

- **File: `app/config.py`**
  - Environment variables for API keys (MEETUP_API_KEY, LUMA_API_KEY, MINIMAX_API_KEY, PERPLEXITY_API_KEY)
  - JWT secret configuration
  - Database path configuration

- **File: `app/database/connection.py`**
  - SQLite connection with SQLAlchemy async support
  - Session management
  - Base model class

- **File: `app/models/database_models.py`**
  ```python
  class User(Base):
      id: int, username: str, email: str, hashed_password: str
      role: str (admin, organizer, assistant, volunteer)
      created_at: datetime
  
  class Event(Base):
      id: int, title: str, description: str, topic: str
      status: str (planning, scheduled, completed, cancelled)
      meetup_id: Optional[str], luma_id: Optional[str]
      scheduled_date: datetime, venue_id: int
      created_by: int
  
  class Task(Base):
      id: int, event_id: int, title: str, description: str
      status: str (todo, in_progress, review, done)
      assignee_id: Optional[int], due_date: Optional[datetime]
  ```

#### 1.2 Authentication System
- **File: `app/auth/router.py`**
  - POST `/auth/register` - User registration
  - POST `/auth/login` - JWT token generation
  - POST `/auth/logout` - Token blacklisting
  - GET `/auth/me` - Current user info

- **File: `app/auth/dependencies.py`**
  - `get_current_user()` - JWT verification dependency
  - `require_role(roles: List[str])` - Role-based access guard
  - Permission checking decorators

### Phase 2: Core Event Management (Days 2-3)

#### 2.1 Event CRUD Operations
- **File: `app/routers/events.py`**
  - CRUD endpoints for events
  - Topic recommendations based on historical events using SQL queries
  - Event-organizer linking

- **File: `app/services/topic_recommender.py`**
  ```python
  def get_topic_recommendations(event_type: str, limit: int = 5) -> List[str]:
      """Query historical events by type to suggest topics"""
      # Analyze past successful events and extract common topics
      pass
  ```

#### 2.2 Kanban Interface
- **File: `app/routers/kanban.py`**
  - GET `/kanban/{event_id}` - Retrieve tasks by status
  - PATCH `/kanban/tasks/{task_id}` - Update task status
  - POST `/kanban/tasks` - Create new task

- **File: `app/templates/dashboard.html`**
  - Four-column layout: Todo, In Progress, Review, Done
  - HTMX modal for creating/editing tasks
  - Drag-and-drop via HTMX enhancements

### Phase 3: API Integrations (Days 3-4)

#### 3.1 Meetup Integration
- **File: `app/services/meetup_service.py`**
  ```python
  async def create_meetup_event(event: Event) -> str:
      """Create event on Meetup using API key"""
      # POST to Meetup API, return meetup_id
  
  async def sync_event_status(meetup_id: str) -> dict:
      """Fetch event status from Meetup"""
      pass
  ```

#### 3.2 Luma Integration
- **File: `app/services/luma_service.py`**
  - Similar structure to Meetup service
  - Event creation and status sync

#### 3.3 Integration Router
- **File: `app/routers/integrations.py`**
  - POST `/integrations/meetup/{event_id}` - Push to Meetup
  - POST `/integrations/luma/{event_id}` - Push to Luma
  - GET `/integrations/status/{event_id}` - Check sync status

### Phase 4: Agentic Workflows (Days 4-6)

#### 4.1 Base Agent Framework
- **File: `app/agents/base_agent.py`**
  ```python
  class BaseAgent:
      def __init__(self, api_key: str):
          self.api_key = api_key
  
      async def execute(self, task: str, context: dict) -> dict:
          """Execute agent with tool calling capabilities"""
          pass
  
      def get_available_tools(self) -> List[Tool]:
          """Return available tools for this agent"""
          pass
  ```

#### 4.2 Venue Research Agent
- **File: `app/agents/venue_research.py`**
  - **Tools:**
    1. `search_existing_venues()` - Query local SQLite venues
    2. `perplexity_search(query)` - Web search via Perplexity API
    3. `save_venue(data)` - Persist new venue to database
    4. `summarize_findings()` - Generate research summary

- **Workflow:**
  1. Receive venue requirements (capacity, location, amenities)
  2. Search existing venues in database
  3. If insufficient, use Perplexity to find additional venues
  4. Compile research report with recommendations

#### 4.3 Speaker Research Agent
- **File: `app/agents/speaker_research.py`**
  - **Tools:**
    1. `search_local_speakers(topic, location)` - Find potential speakers
    2. `enrich_attendee(name, email)` - Enrich attendee data via search
    3. `save_speaker(data)` - Store speaker information
    4. `generate_outreach_message()` - Draft outreach template

- **Workflow:**
  1. Receive event topic and location
  2. Search for relevant local speakers using Perplexity
  3. Enrich previous attendees by name/email
  4. Generate speaker outreach materials

### Phase 5: Marketing Materials (Day 6)

- **File: `app/routers/marketing.py`**
  - POST `/marketing/generate/{event_id}` - Generate marketing copy
  - GET `/marketing/{material_id}` - Retrieve generated material
  - PUT `/marketing/{material_id}` - Edit and save materials

- **Integration with Topic Recommender:**
  - Use historical event data to generate relevant marketing copy
  - Include hashtags, descriptions, call-to-action

### Phase 6: Permission Management (Day 7)

- **File: `app/routers/admin.py`**
  - GET `/admin/permissions/{user_id}` - Get user permissions
  - PUT `/admin/permissions/{user_id}` - Update user role
  - GET `/admin/users` - List all users
  - DELETE `/admin/users/{user_id}` - Deactivate user

- **Role Hierarchy:**
  - admin: Full system access
  - organizer: Manage events, venues, speakers
  - assistant: Edit events, view sensitive data
  - volunteer: Read-only access to assigned events

### Phase 7: Frontend Implementation (Ongoing)

#### 7.1 Minimal CSS Framework
- **File: `static/style.css`**
  - CSS variables for theming
  - Utility classes for layout (flexbox/grid)
  - Form styling
  - Kanban card styling
  - Modal styling
  - No external frameworks - pure minimal CSS

#### 7.2 HTMX-Powered Templates
- All templates use HTMX for:
  - Modal forms (hx-get, hx-post)
  - Kanban updates (hx-patch)
  - Search with debouncing
  - Infinite scroll for large datasets

- **Example HTMX pattern:**
  ```html
  <div hx-get="/events/1/tasks" hx-trigger="load">
    <!-- Tasks loaded via HTMX -->
  </div>
  ```

## API Endpoints Summary

### Authentication
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`
- `GET /auth/me`

### Events
- `GET /events` - List all events
- `POST /events` - Create event
- `GET /events/{id}` - Event details
- `PUT /events/{id}` - Update event
- `DELETE /events/{id}` - Delete event
- `GET /events/recommendations` - Topic recommendations

### Kanban
- `GET /kanban/{event_id}` - Get all tasks
- `POST /kanban/tasks` - Create task
- `PATCH /kanban/tasks/{id}` - Update task status
- `PUT /kanban/tasks/{id}` - Edit task

### Venues
- `GET /venues` - List venues
- `POST /venues` - Add venue
- `POST /venues/research` - Trigger venue research agent
- `GET /venues/{id}` - Venue details

### Speakers
- `GET /speakers` - List speakers
- `POST /speakers/research` - Trigger speaker research
- `POST /speakers/enrich` - Enrich attendee data
- `GET /speakers/{id}` - Speaker details

### Marketing
- `GET /marketing/{event_id}` - Get materials
- `POST /marketing/{event_id}/generate` - Generate marketing copy
- `PUT /marketing/{material_id}` - Edit material

### Integrations
- `POST /integrations/meetup/{event_id}`
- `POST /integrations/luma/{event_id}`
- `GET /integrations/status/{event_id}`

### Admin
- `GET /admin/users`
- `GET /admin/users/{id}`
- `PUT /admin/users/{id}/permissions`
- `DELETE /admin/users/{id}`

## Key Features Implementation

### 1. Topic Recommendations
```python
# In topic_recommender.py
async def get_topic_recommendations(
    event_type: str,
    user_interests: List[str],
    limit: int = 5
) -> List[dict]:
    """Get topic recommendations based on:
    1. Historical event success data
    2. User interests
    3. Current trends (via agent if configured)
    """
    query = """
    SELECT topic, COUNT(*) as frequency
    FROM events
    WHERE status = 'completed'
    AND topic IS NOT NULL
    GROUP BY topic
    ORDER BY frequency DESC
    LIMIT :limit
    """
    # Return top topics with engagement metrics
```

### 2. Agentic Venue Research
```python
# In venue_research.py
class VenueResearchAgent(BaseAgent):
    async def research_venue(self, requirements: VenueRequirements) -> dict:
        # 1. Check existing venues
        existing = await self.search_existing_venues(requirements)
        
        # 2. If needed, search web
        if len(existing) < 3:
            web_results = await self.perplexity_search(
                f"venue for {requirements.event_type} in {requirements.location}"
            )
        
        # 3. Compile and save results
        return self.summarize_findings(existing, web_results)
```

### 3. Kanban with HTMX
```html
<!-- In dashboard.html -->
<div class="kanban-board">
    <div class="column" id="todo">
        <h3>To Do</h3>
        <div hx-get="/kanban/1/tasks?status=todo" 
             hx-trigger="load, taskCreated from:body">
        </div>
    </div>
    <div class="column" id="in_progress">
        <h3>In Progress</h3>
        <div hx-get="/kanban/1/tasks?status=in_progress"
             hx-trigger="load, taskUpdated from:body">
        </div>
    </div>
    <!-- More columns... -->
</div>
```

## Dependencies to Install

```txt
fastapi==0.109.0
uvicorn==0.27.0
sqlalchemy==2.0.25
aiosqlite==0.19.0
pydantic==2.5.3
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
httpx==0.26.0
openai==1.12.0
```

## Next Steps After Confirmation

1. Create project structure and `requirements.txt`
2. Implement database models and connection
3. Build authentication system
4. Create event and kanban APIs
5. Implement Meetup/Luma integrations
6. Build agent framework and research agents
7. Create marketing material generation
8. Build minimal HTML/CSS templates
9. Add HTMX interactivity
10. Test and refine

## Estimated Timeline
- **Phase 1-2 (Foundation + Events)**: 3-4 days
- **Phase 3 (Integrations)**: 1-2 days
- **Phase 4 (Agentic Workflows)**: 2-3 days
- **Phase 5-7 (Marketing + Frontend)**: 2-3 days
- **Total**: 8-12 days for full implementation

# Event Workflow Progress Tracker - Implementation Plan

## Executive Summary

Transform the current basic event management system into a visually engaging, workflow-driven experience with real-time progress tracking, interactive timelines, and intelligent automation suggestions.

---

## Phase 1: Current State Analysis

### What Exists Today
- **Event Model**: Basic event data (title, description, topic, status, dates)
- **Status Field**: Simple enum (planning, scheduled, completed, cancelled)
- **Related Data**: Tasks, organizers, sponsors, marketing materials, agent workflows
- **Integrations**: Meetup, Luma, MiniMax image generation
- **UI**: Basic event cards with minimal metadata

### Gaps Identified
1. No workflow stages or phases
2. No visual progress indicators
3. No timeline/timeline view
4. No task dependencies or critical path
5. No milestone tracking
6. No automation suggestions
7. No event-specific dashboard
8. Poor visual hierarchy and engagement

---

## Phase 2: New Workflow Architecture

### Event Workflow Stages (6 Phases)

```
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 1        PHASE 2        PHASE 3        PHASE 4    PHASE 5  PHASE 6│
│  📋 Planning    🎯 Planning    📢 Marketing    ✅ Ready   🎉 Live   📊 Review │
│  ────────────   ────────────   ────────────   ─────────  ───────   ─────── │
│  • Define       • Book venue   • Create       • All tasks • Event    • Feedback│
│    scope          & date         content        complete   day       collection│
│  • Set budget   • Invite       • Social       • Venue     • Attendee • Metrics │
│                   speakers        posts        confirmed  management  analysis │
│  • Form team    • Send save    • Email        • AV/tech   • Real-time• Report  │
│                   the date        campaigns     ready      support   generation│
└─────────────────────────────────────────────────────────────────────┘
```

### Detailed Stage Definitions

#### Phase 1: Ideation & Planning (Planning Status)
- Event concept definition
- Topic/theme selection
- Target audience identification
- Initial budget planning
- Team formation

#### Phase 2: Logistics & Planning (Scheduled Status)
- Venue booking
- Date confirmation
- Speaker outreach and confirmation
- Initial speaker abstract collection
- AV/technical requirements

#### Phase 3: Marketing & Promotion
- Event branding and imagery
- Website/landing page
- Social media campaigns
- Email marketing sequence
- Community announcements
- CFP (Call for Proposals) if applicable

#### Phase 4: Final Preparation
- All tasks completion check
- Final speaker communications
- Attendee logistics
- Registration closure
- Material finalization

#### Phase 5: Event Execution
- Real-time attendee management
- Live session support
- Q&A moderation
- Networking facilitation
- Recording management

#### Phase 6: Post-Event
- Attendee feedback collection
- Survey distribution
- Recording upload and processing
- Metrics calculation
- Team retrospective
- Report generation

---

## Phase 3: Database Schema Extensions

### New Models Required

```python
class EventWorkflowStage(Base):
    """Workflow stages specific to each event."""
    __tablename__ = "event_workflow_stages"
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    stage = Column(String(50))  # ideation, logistics, marketing, preparation, execution, review
    status = Column(String(20), default="pending")  # pending, in_progress, completed, blocked
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    notes = Column(Text)


class EventMilestone(Base):
    """Key milestones for event."""
    __tablename__ = "event_milestones"
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    title = Column(String(200))
    description = Column(Text)
    due_date = Column(DateTime)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)


class EventWorkflowProgress(Base):
    """Tracks overall workflow progress."""
    __tablename__ = "event_workflow_progress"
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"), unique=True)
    current_phase = Column(String(50), default="ideation")
    completion_percentage = Column(Integer, default=0)
    tasks_completed = Column(Integer, default=0)
    total_tasks = Column(Integer, default=0)
    days_until_event = Column(Integer)
    is_on_track = Column(Boolean, default=True)
    blockers = Column(JSON)  # List of current blockers
    suggestions = Column(JSON)  # AI-generated suggestions
    last_updated = Column(DateTime, default=datetime.utcnow)
```

### Existing Model Updates

```python
class Event(Base):
    # ... existing fields ...
    
    # New fields
    workflow_phase = Column(String(50), default="ideation")
    event_format = Column(String(50))  # in_person, virtual, hybrid
    max_attendees = Column(Integer)
    registration_deadline = Column(DateTime)
    is_featured = Column(Boolean, default=False)
    cover_image_url = Column(String(500))
    
    # Relationships
    workflow_stages = relationship("EventWorkflowStage", cascade="all, delete-orphan")
    milestones = relationship("EventMilestone", cascade="all, delete-orphan")
    workflow_progress = relationship("EventWorkflowProgress", uselist=False, cascade="all, delete-orphan")
```

---

## Phase 4: Backend API Enhancements

### New Endpoints

```
# Workflow Management
POST   /events/{id}/workflow/stages/{stage}/start
POST   /events/{id}/workflow/stages/{stage}/complete
POST   /events/{id}/workflow/stages/{stage}/block

# Milestone Management
GET    /events/{id}/milestones
POST   /events/{id}/milestones
PUT    /events/{id}/milestones/{milestone_id}
DELETE /events/{id}/milestones/{milestone_id}
POST   /events/{id}/milestones/{milestone_id}/complete

# Progress Tracking
GET    /events/{id}/progress
GET    /events/{id}/timeline
GET    /events/{id}/suggestions

# Workflow Templates
GET    /workflow/templates
POST   /workflow/templates
```

### Progress Calculation Logic

```python
async def calculate_workflow_progress(event_id: int) -> dict:
    """Calculate overall workflow progress for an event."""
    
    # Phase completion weights
    PHASE_WEIGHTS = {
        "ideation": 10,
        "logistics": 25,
        "marketing": 25,
        "preparation": 20,
        "execution": 15,
        "review": 5
    }
    
    # Calculate per-phase completion
    phase_progress = {}
    for phase, weight in PHASE_WEIGHTS.items():
        stage = await get_workflow_stage(event_id, phase)
        if stage.status == "completed":
            phase_progress[phase] = 100
        elif stage.status == "in_progress":
            # Calculate based on completed tasks in this phase
            tasks_in_phase = await get_tasks_for_phase(event_id, phase)
            completed = sum(1 for t in tasks_in_phase if t.status == "done")
            phase_progress[phase] = (completed / len(tasks_in_phase) * 100) if tasks_in_phase else 0
        else:
            phase_progress[phase] = 0
    
    # Calculate weighted overall progress
    overall = sum(
        phase_progress[phase] * (weight / 100)
        for phase, weight in PHASE_WEIGHTS.items()
    )
    
    return {
        "overall_percentage": int(overall),
        "phases": phase_progress,
        "current_phase": get_current_phase(phase_progress),
        "is_on_track": await check_if_on_track(event_id),
        "suggestions": await generate_suggestions(event_id)
    }
```

---

## Phase 5: Frontend Implementation

### Visual Components

#### 1. Workflow Progress Bar
```
┌────────────────────────────────────────────────────────────────────────────┐
│  🎯 Planning    📅 Logistics    📢 Marketing    ✅ Prep    🎉 Live    📊 Review │
│  [██████████]   [██████░░░░]   [████████░░]   [██░░░░░░]  [░░░░░░░░]  [░░░░░░░░] │
│      100%          60%            80%           20%        0%         0%           │
│  ✓ Complete     ⟳ In Progress   ⟳ In Progress   ○ Pending   ○ Pending   ○ Pending │
└────────────────────────────────────────────────────────────────────────────┘
```

#### 2. Interactive Timeline View
```
January 2025
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 Jan 15    Event Created                    ▪️ Initial planning started
📌 Jan 20    Venue Booked                      ▪️ TechHub Conf Center
📌 Jan 25    Speaker Confirmed (3/5)           ▪️ Dr. Chen, Marcus, Emily
📌 Jan 30    ▸ TODAY                          ▪️ Marketing campaign launch
📌 Feb 5     Registration Opens                
📌 Feb 10    Website Live                      
📌 Feb 15    ▸ Milestone: CFP Deadline         
📌 Feb 20    ▸ Milestone: Speaker Deck Due     
📌 Mar 1     ▸ EVENT DAY                       ▪️ AI Workshop Summit
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### 3. Task Board with Drag-and-Drop
```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│    TODO (5)      │  │  IN PROGRESS (2) │  │    REVIEW (1)    │  │     DONE (8)     │
├──────────────────┤  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤
│ ○ Send reminders │  │ ○ Create slides  │  │ ○ Review venue   │  │ ○ Book venue ✓   │
│ ○ Update website │  │ ○ Send CFP       │  │ ○ Approve logo   │  │ ○ Confirm Dr.    │
│ ○ Contact spnsrs │  │                  │  │                  │  │   Chen ✓         │
│ ○ ...            │  │                  │  │                  │  │ ○ ...            │
└──────────────────┘  └──────────────────┘  └──────────────────┘  └──────────────────┘
```

#### 4. AI Assistant Panel
```
┌─────────────────────────────────────────┐
│ 🤖 AI Event Assistant                   │
├─────────────────────────────────────────┤
│ 💡 Suggestion:                          │
│ 3 speakers haven't confirmed yet.       │
│ Consider sending follow-up emails.      │
│                                         │
│ ⚠️ Warning:                             │
│ Registration opens in 5 days but        │
│ marketing materials are 60% complete.   │
│                                         │
│ 🚀 Action Items:                        │
│ • Finalize event description            │
│ • Upload event banner image             │
│ • Schedule social media posts           │
│                                         │
│ [Apply Suggestions]  [Dismiss]          │
└─────────────────────────────────────────┘
```

### Page Layout Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ EVENT DASHBOARD - AI Workshop Summit                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ 🎉 Event in 45 days │ 📊 67% Complete │ ⚠️ 3 Blockers │ 😊 On Track  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────────────────────────────────────┐   │
│  │                  │  │                                                  │   │
│  │  EVENT CARD      │  │           WORKFLOW PROGRESS BAR                  │   │
│  │                  │  │                                                  │   │
│  │  [Cover Image]   │  │  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐       │   │
│  │                  │  │  │ 100%│ │ 60%│ │ 80%│ │ 20%│ │ 0% │ │ 0% │       │   │
│  │  📅 Mar 1, 2025  │  │  └────┘ └────┘ └────┘ └────┘ └────┘ └────┘       │   │
│  │  📍 San Francisco│  │                                                  │   │
│  │  👥 150/200      │  │  📍 Logistics Phase - In Progress                │   │
│  │  registered     │  │                                                  │   │
│  │                  │  └──────────────────────────────────────────────────┘   │
│  │  [View Details] │                                                   │
│  └──────────────────┘                                                   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ 🗓️ TIMELINE                    │  ┌─────────────────────────────────────┐│
│  │                                 │  │  📋 TASK BOARD                      ││
│  │ Jan 15 ── Event Created        │  │                                     ││
│  │ Jan 20 ── Venue Booked ✓       │  │  [TODO] [IN PROGRESS] [REVIEW] [DONE]││
│  │ Jan 25 ── 3 Speakers Conf ✓    │  │                                     ││
│  │ Jan 30 ── ◉ TODAY              │  │  [+ New Task]                       ││
│  │ Feb 5  ── Registration Opens   │  │                                     ││
│  │ Feb 15 ── ⚑ Milestone          │  │                                     ││
│  │ Mar 1  ── 🎉 EVENT DAY          │  │                                     ││
│  │                                 │  │                                     ││
│  └─────────────────────────────────┘  └─────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 6: Implementation Tasks

### Week 1: Database & Backend
- [ ] Add new workflow models
- [ ] Create migration script
- [ ] Implement progress calculation logic
- [ ] Add new API endpoints
- [ ] Create workflow template system

### Week 2: Frontend Components
- [ ] Build workflow progress bar component
- [ ] Create interactive timeline view
- [ ] Implement task board with HTMX
- [ ] Add milestone tracking UI
- [ ] Integrate AI suggestions panel

### Week 3: Integration & Polish
- [ ] Connect event detail page to new workflow
- [ ] Add automation suggestions
- [ ] Implement real-time updates with HTMX
- [ ] Add animations and transitions
- [ ] Mobile responsive design

### Week 4: Testing & Launch
- [ ] Write unit tests for progress calculation
- [ ] Test all workflow transitions
- [ ] Performance optimization
- [ ] User acceptance testing
- [ ] Deploy and monitor

---

## Success Metrics

1. **Adoption**: 80% of users interact with workflow tracker
2. **Completion Rate**: 25% increase in event completion
3. **Time Savings**: 30% reduction in planning time
4. **Engagement**: Average 5+ minutes on event page
5. **Satisfaction**: 4.5+ star rating for new workflow features

---

## Technical Considerations

### HTMX Integration
- Use `hx-post` for stage transitions
- Use `hx-trigger` for real-time updates
- Implement optimistic UI updates
- Add loading states with skeletons

### Performance
- Cache workflow progress calculations
- Use pagination for task lists
- Implement lazy loading for timeline
- Debounce form submissions

### Accessibility
- ARIA labels for workflow stages
- Keyboard navigation for task board
- Color-blind friendly status indicators
- Screen reader support

---

## Next Steps

1. **Approve this plan** - Confirm the workflow design
2. **Database migration** - Create initial schema
3. **Backend implementation** - Start with progress calculation
4. **Frontend components** - Build the progress bar
5. **Iterate** - Gather feedback and improve

---

## Appendices

### A. Workflow Template Examples

#### Tech Meetup Template
- **Ideation**: Define topic, target audience, budget
- **Logistics**: Book venue (2 months out), set date
- **Marketing**: Create branding, launch website (6 weeks out)
- **Preparation**: Finalize speakers, prepare materials (2 weeks out)
- **Execution**: Run event, collect feedback
- **Review**: Share recordings, analyze metrics

#### Workshop Template
- **Ideation**: Define curriculum, learning objectives
- **Logistics**: Secure venue with AV, recruit instructors
- **Marketing**: Create course page, open registration
- **Preparation**: Develop materials, test exercises
- **Execution**: Facilitate workshop, support participants
- **Review**: Gather feedback, improve curriculum

### B. Color Scheme for Workflow Stages

| Phase | Color | Hex Code |
|-------|-------|----------|
| Ideation | 🟣 Purple | #8B5CF6 |
| Logistics | 🔵 Blue | #3B82F6 |
| Marketing | 🟡 Yellow | #F59E0B |
| Preparation | 🟠 Orange | #F97316 |
| Execution | 🟢 Green | #22C55E |
| Review | ⚪ Gray | #6B7280 |

### C. AI Prompt Suggestions

```python
SUGGESTION_PROMPTS = {
    "logistics": [
        "Based on your event size ({attendees}), consider a venue with capacity {capacity}+",
        "You have {days} days until event. Average venue booking time is 2 weeks - consider booking soon",
        "Only {confirmed}/{total} speakers confirmed. Typical follow-up sequence includes 3 touchpoints"
    ],
    "marketing": [
        "Your event is in {days} days. Best time to start marketing was {weeks_ago} weeks ago",
        "Consider creating {count} social media posts per platform leading up to the event",
        "Email open rates typically peak at 35-40% for event announcements - your current template looks good"
    ],
    "tasks": [
        "You have {blocked} blocked tasks. The most common blocker is speaker confirmation",
        "Consider prioritizing tasks on the critical path: venue → speakers → marketing → materials",
        "{overdue} tasks are overdue. Would you like help rescheduling?"
    ]
}
```

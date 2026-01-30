"""
Workflow Templates - Predefined event planning workflows with subtasks.
Contains comprehensive task breakdowns for different event types.
"""
from typing import Dict, List, Any
from datetime import datetime, timedelta


# Subtask categories for each phase
SUBTASK_TEMPLATES = {
    "ideation": {
        "category_name": "Event Concept & Planning",
        "subtasks": [
            {
                "title": "Define Event Concept & Vision",
                "description": "Write a clear event vision statement and key objectives",
                "category": "concept",
                "priority": "critical",
                "estimated_hours": 4,
                "order": 1
            },
            {
                "title": "Identify Target Audience",
                "description": "Define attendee personas, experience level, interests",
                "category": "audience",
                "priority": "high",
                "estimated_hours": 3,
                "order": 2
            },
            {
                "title": "Set Budget Framework",
                "description": "Estimate costs for venue, food, speakers, marketing",
                "category": "budget",
                "priority": "high",
                "estimated_hours": 4,
                "order": 3
            },
            {
                "title": "Determine Event Format",
                "description": "Choose in-person, virtual, or hybrid format",
                "category": "logistics",
                "priority": "critical",
                "estimated_hours": 2,
                "order": 4
            },
            {
                "title": "Select Potential Dates",
                "description": "Identify 3-5 potential dates avoiding conflicts",
                "category": "logistics",
                "priority": "high",
                "estimated_hours": 2,
                "order": 5
            },
            {
                "title": "Define Success Metrics",
                "description": "Set KPIs: attendance, engagement, satisfaction score",
                "category": "metrics",
                "priority": "high",
                "estimated_hours": 3,
                "order": 6
            },
            {
                "title": "Form Planning Team",
                "description": "Identify and recruit core team members",
                "category": "team",
                "priority": "high",
                "estimated_hours": 3,
                "order": 7
            },
            {
                "title": "Research Similar Events",
                "description": "Analyze 3-5 similar events for best practices",
                "category": "research",
                "priority": "medium",
                "estimated_hours": 4,
                "order": 8
            }
        ]
    },
    "logistics": {
        "category_name": "Venue, Speakers & Logistics",
        "subtasks": [
            {
                "title": "Create Venue Requirements List",
                "description": "Capacity, AV needs, accessibility, parking, amenities",
                "category": "venue",
                "priority": "critical",
                "estimated_hours": 2,
                "order": 1
            },
            {
                "title": "Research & Shortlist Venues",
                "description": "Find 5-7 venues matching requirements",
                "category": "venue",
                "priority": "critical",
                "estimated_hours": 6,
                "order": 2
            },
            {
                "title": "Schedule Venue Tours",
                "description": "Book and complete tours of top 3 venues",
                "category": "venue",
                "priority": "high",
                "estimated_hours": 4,
                "order": 3
            },
            {
                "title": "Negotiate & Book Venue",
                "description": "Finalize contract, deposit, and confirm booking",
                "category": "venue",
                "priority": "critical",
                "estimated_hours": 4,
                "order": 4
            },
            {
                "title": "Define Speaker Criteria",
                "description": "Experience, topics, diversity, availability",
                "category": "speakers",
                "priority": "high",
                "estimated_hours": 2,
                "order": 5
            },
            {
                "title": "Research & Identify Speakers",
                "description": "Create target list of 10-15 potential speakers",
                "category": "speakers",
                "priority": "high",
                "estimated_hours": 8,
                "order": 6
            },
            {
                "title": "Create Speaker Outreach Plan",
                "description": "Draft emails, timeline, and follow-up strategy",
                "category": "speakers",
                "priority": "high",
                "estimated_hours": 3,
                "order": 7
            },
            {
                "title": "Send Speaker Invitations",
                "description": "Send personalized invitations to top choices",
                "category": "speakers",
                "priority": "high",
                "estimated_hours": 4,
                "order": 8
            },
            {
                "title": "Create Speaker Agreement Template",
                "description": "Define compensation, travel, content rights",
                "category": "speakers",
                "priority": "medium",
                "estimated_hours": 3,
                "order": 9
            },
            {
                "title": "Finalize Speaker Lineup",
                "description": "Confirm all speakers and collect bios/photos",
                "category": "speakers",
                "priority": "critical",
                "estimated_hours": 4,
                "order": 10
            },
            {
                "title": "Arrange AV & Technical Needs",
                "description": "Confirm projectors, microphones, streaming setup",
                "category": "technical",
                "priority": "high",
                "estimated_hours": 3,
                "order": 11
            },
            {
                "title": "Arrange Catering",
                "description": "Menu selection, dietary restrictions, delivery",
                "category": "catering",
                "priority": "medium",
                "estimated_hours": 4,
                "order": 12
            },
            {
                "title": "Plan Registration Process",
                "description": "Create registration flow, confirm attendee limits",
                "category": "registration",
                "priority": "high",
                "estimated_hours": 3,
                "order": 13
            }
        ]
    },
    "marketing": {
        "category_name": "Marketing & Promotion",
        "subtasks": [
            {
                "title": "Develop Event Brand Identity",
                "description": "Logo, color scheme, fonts, visual style",
                "category": "branding",
                "priority": "critical",
                "estimated_hours": 8,
                "order": 1
            },
            {
                "title": "Write Event Copy",
                "description": "Description, tagline, key selling points",
                "category": "content",
                "priority": "critical",
                "estimated_hours": 4,
                "order": 2
            },
            {
                "title": "Generate AI Event Image",
                "description": "Create promotional image using MiniMax/Replicate",
                "category": "branding",
                "priority": "high",
                "estimated_hours": 1,
                "order": 3
            },
            {
                "title": "Create Landing Page",
                "description": "Design and build event registration page",
                "category": "website",
                "priority": "critical",
                "estimated_hours": 8,
                "order": 4
            },
            {
                "title": "Set Up Registration System",
                "description": "Configure ticket types, pricing tiers, limits",
                "category": "website",
                "priority": "critical",
                "estimated_hours": 4,
                "order": 5
            },
            {
                "title": "Create Social Media Strategy",
                "description": "Platforms, content calendar, posting schedule",
                "category": "social",
                "priority": "high",
                "estimated_hours": 4,
                "order": 6
            },
            {
                "title": "Design Social Media Assets",
                "description": "Create graphics for all platforms",
                "category": "social",
                "priority": "high",
                "estimated_hours": 8,
                "order": 7
            },
            {
                "title": "Create Email Campaign Sequence",
                "description": "Write 5-7 emails for announcement, reminders",
                "category": "email",
                "priority": "high",
                "estimated_hours": 8,
                "order": 8
            },
            {
                "title": "Set Up Email Automation",
                "description": "Configure drip campaigns and triggers",
                "category": "email",
                "priority": "high",
                "estimated_hours": 4,
                "order": 9
            },
            {
                "title": "Create Press Release",
                "description": "Write and distribute press announcement",
                "category": "pr",
                "priority": "medium",
                "estimated_hours": 4,
                "order": 10
            },
            {
                "title": "Reach Out to Partners",
                "description": "Contact sponsors, community partners for promotion",
                "category": "partners",
                "priority": "high",
                "estimated_hours": 4,
                "order": 11
            },
            {
                "title": "Create Speaker Promotion Kit",
                "description": "Social posts, email templates for speakers",
                "category": "social",
                "priority": "medium",
                "estimated_hours": 3,
                "order": 12
            },
            {
                "title": "Launch Early Bird Campaign",
                "description": "Open registration with early bird pricing",
                "category": "campaign",
                "priority": "critical",
                "estimated_hours": 2,
                "order": 13
            },
            {
                "title": "Schedule Social Media Posts",
                "description": "Load all posts into scheduling tool",
                "category": "social",
                "priority": "high",
                "estimated_hours": 4,
                "order": 14
            }
        ]
    },
    "preparation": {
        "category_name": "Final Preparations",
        "subtasks": [
            {
                "title": "Final Speaker Communications",
                "description": "Send logistics, AV requirements, schedule",
                "category": "speakers",
                "priority": "critical",
                "estimated_hours": 4,
                "order": 1
            },
            {
                "title": "Collect Speaker Materials",
                "description": "Bios, photos, slide decks, videos",
                "category": "content",
                "priority": "high",
                "estimated_hours": 4,
                "order": 2
            },
            {
                "title": "Review & Test AV Equipment",
                "description": "Full rehearsal with all technical setup",
                "category": "technical",
                "priority": "critical",
                "estimated_hours": 4,
                "order": 3
            },
            {
                "title": "Create Event Schedule",
                "description": "Detailed timeline with buffer times",
                "category": "logistics",
                "priority": "critical",
                "estimated_hours": 4,
                "order": 4
            },
            {
                "title": "Prepare Speaker Briefings",
                "description": "Timelines, logistics, Q&A expectations",
                "category": "speakers",
                "priority": "high",
                "estimated_hours": 4,
                "order": 5
            },
            {
                "title": "Create Attendee Guide",
                "description": "Venue info, schedule, tips, WiFi passwords",
                "category": "content",
                "priority": "high",
                "estimated_hours": 4,
                "order": 6
            },
            {
                "title": "Print Signage & Materials",
                "description": "Direction signs, name tags, agendas",
                "category": "materials",
                "priority": "medium",
                "estimated_hours": 3,
                "order": 7
            },
            {
                "title": "Confirm Catering Order",
                "description": "Final headcount, delivery time, setup",
                "category": "catering",
                "priority": "high",
                "estimated_hours": 2,
                "order": 8
            },
            {
                "title": "Train Registration Volunteers",
                "description": "Process walkthrough, troubleshooting",
                "category": "volunteers",
                "priority": "high",
                "estimated_hours": 3,
                "order": 9
            },
            {
                "title": "Prepare Emergency Contacts List",
                "description": "Venue staff, tech support, medical",
                "category": "safety",
                "priority": "high",
                "estimated_hours": 1,
                "order": 10
            },
            {
                "title": "Set Up Event Check-in System",
                "description": "QR codes, badge printing, check-in app",
                "category": "registration",
                "priority": "critical",
                "estimated_hours": 3,
                "order": 11
            },
            {
                "title": "Final Marketing Push",
                "description": "Last social posts, reminder emails",
                "category": "marketing",
                "priority": "high",
                "estimated_hours": 4,
                "order": 12
            },
            {
                "title": "Print Final Attendee List",
                "description": "Backup registration list",
                "category": "registration",
                "priority": "medium",
                "estimated_hours": 1,
                "order": 13
            },
            {
                "title": "Pack Event Kit",
                "description": "Laptop, dongles, backup cables, swag",
                "category": "materials",
                "priority": "high",
                "estimated_hours": 2,
                "order": 14
            }
        ]
    },
    "execution": {
        "category_name": "Event Day Execution",
        "subtasks": [
            {
                "title": "Arrive Early & Set Up",
                "description": "Venue access, unpack, equipment setup",
                "category": "setup",
                "priority": "critical",
                "estimated_hours": 3,
                "order": 1
            },
            {
                "title": "Test All AV Systems",
                "description": "Projector, microphone, livestream, recordings",
                "category": "technical",
                "priority": "critical",
                "estimated_hours": 1,
                "order": 2
            },
            {
                "title": "Set Up Registration Desk",
                "description": "Check-in stations, badge printing, signs",
                "category": "registration",
                "priority": "critical",
                "estimated_hours": 1,
                "order": 3
            },
            {
                "title": "Brief All Staff & Volunteers",
                "description": "Roles, schedule, communication plan",
                "category": "team",
                "priority": "critical",
                "estimated_hours": 0.5,
                "order": 4
            },
            {
                "title": "Manage Check-in Process",
                "description": "Greet attendees, troubleshoot issues",
                "category": "registration",
                "priority": "high",
                "estimated_hours": 4,
                "order": 5
            },
            {
                "title": "Facilitate Opening",
                "description": "Welcome remarks, housekeeping, WiFi info",
                "category": "program",
                "priority": "high",
                "estimated_hours": 0.5,
                "order": 6
            },
            {
                "title": "Monitor Session Flow",
                "description": "Track time, handle issues, assist speakers",
                "category": "program",
                "priority": "critical",
                "estimated_hours": 6,
                "order": 7
            },
            {
                "title": "Manage Break Logistics",
                "description": "Coffee, food, room reset",
                "category": "logistics",
                "priority": "high",
                "estimated_hours": 2,
                "order": 8
            },
            {
                "title": "Capture Photos & Video",
                "description": "Document key moments, speaker sessions",
                "category": "media",
                "priority": "high",
                "estimated_hours": 6,
                "order": 9
            },
            {
                "title": "Moderate Q&A Sessions",
                "description": "Collect questions, facilitate discussion",
                "category": "program",
                "priority": "medium",
                "estimated_hours": 3,
                "order": 10
            },
            {
                "title": "Handle Real-time Issues",
                "description": "Technical problems, attendee concerns",
                "category": "troubleshooting",
                "priority": "high",
                "estimated_hours": 4,
                "order": 11
            },
            {
                "title": "Manage Networking Session",
                "description": "Facilitate connections, timekeeper",
                "category": "program",
                "priority": "medium",
                "estimated_hours": 2,
                "order": 12
            },
            {
                "title": "Collect Feedback Cards",
                "description": "Physical feedback forms",
                "category": "feedback",
                "priority": "high",
                "estimated_hours": 1,
                "order": 13
            },
            {
                "title": "Close & Thank Attendees",
                "description": "Closing remarks, next event announcement",
                "category": "program",
                "priority": "high",
                "estimated_hours": 0.5,
                "order": 14
            },
            {
                "title": "Clean Up & Pack Out",
                "description": "Collect materials, equipment, trash",
                "category": "setup",
                "priority": "high",
                "estimated_hours": 2,
                "order": 15
            }
        ]
    },
    "review": {
        "category_name": "Post-Event Review",
        "subtasks": [
            {
                "title": "Send Thank You Emails",
                "description": "Attendees, speakers, sponsors, volunteers",
                "category": "communication",
                "priority": "high",
                "estimated_hours": 2,
                "order": 1
            },
            {
                "title": "Upload Session Recordings",
                "description": "Edit and publish video content",
                "category": "content",
                "priority": "high",
                "estimated_hours": 8,
                "order": 2
            },
            {
                "title": "Process Survey Responses",
                "description": "Analyze feedback forms and ratings",
                "category": "feedback",
                "priority": "high",
                "estimated_hours": 4,
                "order": 3
            },
            {
                "title": "Calculate Success Metrics",
                "description": "Attendance rate, NPS, engagement scores",
                "category": "metrics",
                "priority": "critical",
                "estimated_hours": 3,
                "order": 4
            },
            {
                "title": "Compare to Baseline Goals",
                "description": "Did we meet our KPIs? Analysis",
                "category": "metrics",
                "priority": "high",
                "estimated_hours": 2,
                "order": 5
            },
            {
                "title": "Conduct Team Retrospective",
                "description": "What went well, what to improve",
                "category": "review",
                "priority": "high",
                "estimated_hours": 3,
                "order": 6
            },
            {
                "title": "Document Lessons Learned",
                "description": "Create report for future events",
                "category": "documentation",
                "priority": "high",
                "estimated_hours": 4,
                "order": 7
            },
            {
                "title": "Process Expense Reimbursements",
                "description": "Collect and approve receipts",
                "category": "budget",
                "priority": "medium",
                "estimated_hours": 2,
                "order": 8
            },
            {
                "title": "Final Budget Reconciliation",
                "description": "Compare actual vs budgeted costs",
                "category": "budget",
                "priority": "high",
                "estimated_hours": 2,
                "order": 9
            },
            {
                "title": "Share Highlights Content",
                "description": "Photos, key moments on social media",
                "category": "marketing",
                "priority": "high",
                "estimated_hours": 4,
                "order": 10
            },
            {
                "title": "Update Speaker Database",
                "description": "Ratings, notes for future outreach",
                "category": "speakers",
                "priority": "medium",
                "estimated_hours": 2,
                "order": 11
            },
            {
                "title": "Archive Event Materials",
                "description": "Presentations, photos, assets for future use",
                "category": "documentation",
                "priority": "medium",
                "estimated_hours": 3,
                "order": 12
            },
            {
                "title": "Plan Follow-up Content",
                "description": "Blog posts, newsletters about event",
                "category": "content",
                "priority": "medium",
                "estimated_hours": 4,
                "order": 13
            },
            {
                "title": "Begin Planning Next Event",
                "description": "Initial ideas based on feedback",
                "category": "planning",
                "priority": "low",
                "estimated_hours": 2,
                "order": 14
            }
        ]
    }
}

# Milestone templates for different event types
MILESTONE_TEMPLATES = {
    "meetup": [
        {"title": "Event Concept Finalized", "milestone_type": "deliverable", "days_before_event": 60, "is_critical": True},
        {"title": "Venue Booked", "milestone_type": "deadline", "days_before_event": 45, "is_critical": True},
        {"title": "First Speaker Confirmed", "milestone_type": "deliverable", "days_before_event": 35, "is_critical": False},
        {"title": "Registration Opens", "milestone_type": "deadline", "days_before_event": 30, "is_critical": True},
        {"title": "Website Live", "milestone_type": "deliverable", "days_before_event": 28, "is_critical": True},
        {"title": "Speaker Deck Due", "milestone_type": "deadline", "days_before_event": 14, "is_critical": False},
        {"title": "Marketing Campaign Launch", "milestone_type": "deliverable", "days_before_event": 21, "is_critical": False},
        {"title": "Registration Deadline", "milestone_type": "deadline", "days_before_event": 7, "is_critical": True},
        {"title": "Final Run-through", "milestone_type": "deliverable", "days_before_event": 3, "is_critical": False},
        {"title": "Event Day", "milestone_type": "event", "days_before_event": 0, "is_critical": True},
        {"title": "Feedback Survey Sent", "milestone_type": "deadline", "days_before_event": -1, "is_critical": False},
        {"title": "Event Report Complete", "milestone_type": "deliverable", "days_before_event": -7, "is_critical": False},
    ],
    "workshop": [
        {"title": "Curriculum Finalized", "milestone_type": "deliverable", "days_before_event": 45, "is_critical": True},
        {"title": "Venue & Date Confirmed", "milestone_type": "deadline", "days_before_event": 40, "is_critical": True},
        {"title": "Instructor Contracts Signed", "milestone_type": "deliverable", "days_before_event": 35, "is_critical": True},
        {"title": "Registration Opens", "milestone_type": "deadline", "days_before_event": 30, "is_critical": True},
        {"title": "Course Materials Draft", "milestone_type": "deliverable", "days_before_event": 21, "is_critical": False},
        {"title": "Registration Deadline", "milestone_type": "deadline", "days_before_event": 7, "is_critical": True},
        {"title": "Final Materials Ready", "milestone_type": "deliverable", "days_before_event": 5, "is_critical": True},
        {"title": "Event Day", "milestone_type": "event", "days_before_event": 0, "is_critical": True},
        {"title": "Certificates Issued", "milestone_type": "deliverable", "days_before_event": -3, "is_critical": False},
    ],
    "conference": [
        {"title": "Conference Theme & Scope Defined", "milestone_type": "deliverable", "days_before_event": 120, "is_critical": True},
        {"title": "Keynote Speakers Secured", "milestone_type": "deliverable", "days_before_event": 90, "is_critical": True},
        {"title": "Venue Contract Signed", "milestone_type": "deadline", "days_before_event": 90, "is_critical": True},
        {"title": "Call for Proposals Open", "milestone_type": "deadline", "days_before_event": 75, "is_critical": False},
        {"title": "Early Bird Registration", "milestone_type": "deadline", "days_before_event": 60, "is_critical": True},
        {"title": "CFP Deadline", "milestone_type": "deadline", "days_before_event": 45, "is_critical": True},
        {"title": "Speaker Schedule Published", "milestone_type": "deliverable", "days_before_event": 30, "is_critical": True},
        {"title": "Regular Registration Closes", "milestone_type": "deadline", "days_before_event": 14, "is_critical": True},
        {"title": "Final AV Checklist", "milestone_type": "deliverable", "days_before_event": 7, "is_critical": False},
        {"title": "Conference Day 1", "milestone_type": "event", "days_before_event": 0, "is_critical": True},
        {"title": "Post-Conference Report", "milestone_type": "deliverable", "days_before_event": -14, "is_critical": False},
    ]
}

# Phase configuration templates
PHASE_CONFIG = {
    "ideation": {
        "name": "Ideation & Planning",
        "description": "Define event concept, goals, and initial planning",
        "weight": 10,
        "color": "#8B5CF6",  # Purple
        "icon": "💡",
        "typical_duration_days": 14,
        "order": 1
    },
    "logistics": {
        "name": "Logistics & Speakers",
        "description": "Book venue, confirm speakers, arrange logistics",
        "weight": 25,
        "color": "#3B82F6",  # Blue
        "icon": "📅",
        "typical_duration_days": 30,
        "order": 2
    },
    "marketing": {
        "name": "Marketing & Promotion",
        "description": "Create brand, launch campaigns, drive registrations",
        "weight": 25,
        "color": "#F59E0B",  # Yellow
        "icon": "📢",
        "typical_duration_days": 35,
        "order": 3
    },
    "preparation": {
        "name": "Final Preparation",
        "description": "Finalize materials, rehearse, prepare for event",
        "weight": 20,
        "color": "#F97316",  # Orange
        "icon": "✅",
        "typical_duration_days": 14,
        "order": 4
    },
    "execution": {
        "name": "Event Execution",
        "description": "Run the event successfully",
        "weight": 15,
        "color": "#22C55E",  # Green
        "icon": "🎉",
        "typical_duration_days": 1,
        "order": 5
    },
    "review": {
        "name": "Post-Event Review",
        "description": "Gather feedback, analyze metrics, document learnings",
        "weight": 5,
        "color": "#6B7280",  # Gray
        "icon": "📊",
        "typical_duration_days": 7,
        "order": 6
    }
}


def get_workflow_template(event_type: str = "meetup") -> Dict[str, Any]:
    """Get complete workflow template for an event type."""
    return {
        "phases": PHASE_CONFIG,
        "subtasks": SUBTASK_TEMPLATES,
        "milestones": MILESTONE_TEMPLATES.get(event_type, MILESTONE_TEMPLATES["meetup"]),
        "event_type": event_type
    }


def generate_subtasks_for_phase(phase: str) -> List[Dict[str, Any]]:
    """Get all subtasks for a specific phase."""
    return SUBTASK_TEMPLATES.get(phase, {}).get("subtasks", [])


def generate_milestones_for_event(
    event_type: str,
    event_date: datetime,
    schedule_offset: int = 0
) -> List[Dict[str, Any]]:
    """Generate milestone list based on event type and date."""
    template = MILESTONE_TEMPLATES.get(event_type, MILESTONE_TEMPLATES["meetup"])
    milestones = []
    
    for i, milestone_template in enumerate(template):
        due_date = event_date - timedelta(days=milestone_template["days_before_event"])
        milestones.append({
            "title": milestone_template["title"],
            "description": f"Milestone: {milestone_template['title']}",
            "milestone_type": milestone_template["milestone_type"],
            "due_date": due_date,
            "is_completed": False,
            "is_critical": milestone_template["is_critical"],
            "order": i,
            "impact_description": f"Missing this milestone could impact {milestone_template['title'].lower()}"
        })
    
    return milestones


def get_phase_subtasks_by_category(phase: str) -> Dict[str, List[Dict[str, Any]]]:
    """Get subtasks organized by category for a phase."""
    subtasks = generate_subtasks_for_phase(phase)
    categorized = {}
    
    for subtask in subtasks:
        category = subtask.get("category", "general")
        if category not in categorized:
            categorized[category] = []
        categorized[category].append(subtask)
    
    return categorized

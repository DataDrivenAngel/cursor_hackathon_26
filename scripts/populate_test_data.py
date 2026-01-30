#!/usr/bin/env python3
"""
Populate database with synthetic test data for Data & AI events.
Run this script to set up test data for local development.
"""
import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.database.connection import engine, async_session_factory
from app.models.database_models import (
    User, Event, Organizer, Venue, Speaker, Task, Sponsor, 
    EventSponsor, MarketingMaterial, AgentWorkflow, Permission,
    AttendeeProfile, EventAttendee
)
from app.models.workflow_models import EventWorkflowProgress, WorkflowStage, EventMilestone
from app.auth.utils import get_password_hash as hash_password


async def get_session():
    """Get a database session."""
    async with async_session_factory() as session:
        yield session


# Sample Data & AI Topics
TOPICS = [
    "Machine Learning",
    "Deep Learning",
    "Natural Language Processing",
    "Computer Vision",
    "AI Ethics",
    "Data Engineering",
    "MLOps",
    "Reinforcement Learning",
    "Transformer Models",
    "Generative AI",
    "Large Language Models",
    "Neural Networks",
    "AutoML",
    "Edge AI",
    "AI in Healthcare"
]

# Sample Event Titles
EVENT_TITLES = [
    "Introduction to Machine Learning",
    "Deep Learning Workshop",
    "NLP with Python",
    "Computer Vision Fundamentals",
    "AI Ethics and Responsible AI",
    "Data Engineering at Scale",
    "MLOps Best Practices",
    "Reinforcement Learning Lab",
    "Building with Transformers",
    "Generative AI Hackathon",
    "LLM Fine-tuning Workshop",
    "Neural Networks from Scratch",
    "AutoML Deep Dive",
    "Edge AI Deployment",
    "AI in Healthcare Summit"
]

# Sample Speaker Data
SPEAKERS = [
    {
        "name": "Dr. Sarah Chen",
        "email": "sarah.chen@aiml.example.com",
        "bio": "Senior Research Scientist at AI Lab. PhD in Machine Learning from Stanford. Specializes in deep learning and neural networks.",
        "expertise": ["Machine Learning", "Deep Learning", "Neural Networks"],
        "company": "AI Lab",
        "role": "Research Scientist"
    },
    {
        "name": "Marcus Johnson",
        "email": "marcus.j@dataengine.example.com",
        "bio": "Data Engineering Lead with 10+ years experience. Former Google engineer. Passionate about scalable data pipelines.",
        "expertise": ["Data Engineering", "Apache Spark", "Data Pipelines"],
        "company": "DataEngine Inc",
        "role": "Data Engineering Lead"
    },
    {
        "name": "Dr. Emily Rodriguez",
        "email": "emily.r@nlp.example.com",
        "bio": "NLP Researcher and author of 'Practical NLP'. PhD from MIT. Expert in transformer models and language understanding.",
        "expertise": ["Natural Language Processing", "Transformers", "LLMs"],
        "company": "NLP Research Lab",
        "role": "Principal Researcher"
    },
    {
        "name": "David Kim",
        "email": "david.kim@cv.example.com",
        "bio": "Computer Vision Engineer at Vision AI. Previously at Tesla Autopilot. Focus on real-time object detection.",
        "expertise": ["Computer Vision", "Object Detection", "Autonomous Systems"],
        "company": "Vision AI",
        "role": "Senior Engineer"
    },
    {
        "name": "Dr. Amanda Foster",
        "email": "amanda.foster@ethics.example.com",
        "bio": "AI Ethics researcher and advocate. Professor at Berkeley. Author of 'The Ethical AI Handbook'.",
        "expertise": ["AI Ethics", "Responsible AI", "AI Policy"],
        "company": "UC Berkeley",
        "role": "Associate Professor"
    },
    {
        "name": "James Wilson",
        "email": "james.wilson@mlops.example.com",
        "bio": "MLOps Architect. Helps companies deploy ML models at scale. Maintainer of popular open-source ML tools.",
        "expertise": ["MLOps", "Kubernetes", "Model Deployment"],
        "company": "MLOps Solutions",
        "role": "Solutions Architect"
    },
    {
        "name": "Dr. Priya Sharma",
        "email": "priya.s@genai.example.com",
        "bio": "Generative AI specialist. Created viral AI art tools. Previously at OpenAI. Expert in diffusion models.",
        "expertise": ["Generative AI", "Diffusion Models", "Image Generation"],
        "company": "Creative AI Labs",
        "role": "CTO"
    },
    {
        "name": "Michael Torres",
        "email": "michael.t@healthcare.ai",
        "bio": "AI in Healthcare pioneer. Developed FDA-approved diagnostic tools. Medical doctor and AI researcher.",
        "expertise": ["AI in Healthcare", "Medical AI", "Diagnostic Systems"],
        "company": "HealthAI Medical",
        "role": "Chief Medical Officer"
    }
]

# Sample Venues
VENUES = [
    {
        "name": "TechHub Conference Center",
        "address": "123 Innovation Drive",
        "city": "San Francisco",
        "state": "CA",
        "country": "USA",
        "capacity": 200,
        "amenities": ["WiFi", "Projector", "Whiteboard", "Coffee", "Parking"],
        "contact_email": "events@techhub.example.com",
        "contact_phone": "+1-415-555-0100",
        "website": "https://techhub.example.com"
    },
    {
        "name": "AI Research Lab Auditorium",
        "address": "456 Neural Network Lane",
        "city": "Palo Alto",
        "state": "CA",
        "country": "USA",
        "capacity": 150,
        "amenities": ["WiFi", "Video Recording", "Livestream", "Whiteboard"],
        "contact_email": "talks@airesearch.example.com",
        "contact_phone": "+1-650-555-0200",
        "website": "https://airesearch.example.com"
    },
    {
        "name": "The Data Center",
        "address": "789 Pipeline Blvd",
        "city": "San Jose",
        "state": "CA",
        "country": "USA",
        "capacity": 100,
        "amenities": ["WiFi", "Projector", "Kitchen", "Parking"],
        "contact_email": "hello@thedatacenter.example.com",
        "contact_phone": "+1-408-555-0300",
        "website": "https://thedatacenter.example.com"
    },
    {
        "name": "Startup Campus",
        "address": "321 Venture Way",
        "city": "Mountain View",
        "state": "CA",
        "country": "USA",
        "capacity": 80,
        "amenities": ["WiFi", "Whiteboard", "Coffee", "Snacks"],
        "contact_email": "events@startupcampus.example.com",
        "contact_phone": "+1-650-555-0400",
        "website": "https://startupcampus.example.com"
    },
    {
        "name": "University Hall",
        "address": "100 Academic Way",
        "city": "Berkeley",
        "state": "CA",
        "country": "USA",
        "capacity": 300,
        "amenities": ["WiFi", "AV System", "Stage", "Wheelchair Access"],
        "contact_email": "conference@university.example.edu",
        "contact_phone": "+1-510-555-0500",
        "website": "https://university.example.edu"
    }
]

# Sample Sponsors
SPONSORS = [
    {
        "name": "TechCorp Industries",
        "contact_email": "sponsors@techcorp.example.com",
        "contact_phone": "+1-800-555-1000",
        "website": "https://techcorp.example.com",
        "description": "Leading technology company focused on AI and cloud solutions"
    },
    {
        "name": "DataFlow Systems",
        "contact_email": "events@dataflow.example.com",
        "contact_phone": "+1-800-555-2000",
        "website": "https://dataflow.example.com",
        "description": "Enterprise data pipeline and analytics platform"
    },
    {
        "name": "CloudScale",
        "contact_email": "community@cloudscale.example.com",
        "contact_phone": "+1-800-555-3000",
        "website": "https://cloudscale.example.com",
        "description": "Cloud infrastructure for AI workloads"
    },
    {
        "name": "AI Ventures",
        "contact_email": "hello@aiventures.example.com",
        "contact_phone": "+1-800-555-4000",
        "website": "https://aiventures.example.com",
        "description": "Venture capital firm investing in AI startups"
    },
    {
        "name": "DevTools Inc",
        "contact_email": "sponsors@devtools.example.com",
        "contact_phone": "+1-800-555-5000",
        "website": "https://devtools.example.com",
        "description": "Developer tools and productivity platforms"
    }
]


async def create_users(session):
    """Create test users."""
    print("Creating users...")
    
    users = [
        User(
            username="admin",
            email="admin@example.com",
            hashed_password=hash_password("admin123"),
            role="admin",
            is_active=True
        ),
        User(
            username="organizer1",
            email="organizer1@example.com",
            hashed_password=hash_password("organizer123"),
            role="organizer",
            is_active=True
        ),
        User(
            username="organizer2",
            email="organizer2@example.com",
            hashed_password=hash_password("organizer123"),
            role="organizer",
            is_active=True
        ),
        User(
            username="assistant",
            email="assistant@example.com",
            hashed_password=hash_password("assistant123"),
            role="assistant",
            is_active=True
        )
    ]
    
    for user in users:
        session.add(user)
    
    await session.commit()
    print(f"✓ Created {len(users)} users")
    return users


async def create_venues(session):
    """Create test venues."""
    print("Creating venues...")
    
    venues = []
    for i, venue_data in enumerate(VENUES):
        venue = Venue(
            name=venue_data["name"],
            address=venue_data["address"],
            city=venue_data["city"],
            state=venue_data["state"],
            country=venue_data["country"],
            capacity=venue_data["capacity"],
            amenities=",".join(venue_data["amenities"]),
            contact_email=venue_data["contact_email"],
            contact_phone=venue_data["contact_phone"],
            website=venue_data["website"],
            created_by=1  # admin user
        )
        session.add(venue)
        venues.append(venue)
    
    await session.commit()
    print(f"✓ Created {len(venues)} venues")
    return venues


async def create_speakers(session):
    """Create test speakers."""
    print("Creating speakers...")
    
    speakers = []
    for speaker_data in SPEAKERS:
        speaker = Speaker(
            name=speaker_data["name"],
            email=speaker_data["email"],
            bio=speaker_data["bio"],
            expertise=",".join(speaker_data["expertise"]),
            company=speaker_data["company"],
            role=speaker_data["role"],
            created_by=1
        )
        session.add(speaker)
        speakers.append(speaker)
    
    await session.commit()
    print(f"✓ Created {len(speakers)} speakers")
    return speakers


async def create_sponsors(session):
    """Create test sponsors."""
    print("Creating sponsors...")
    
    sponsors = []
    for sponsor_data in SPONSORS:
        sponsor = Sponsor(
            name=sponsor_data["name"],
            contact_email=sponsor_data["contact_email"],
            contact_phone=sponsor_data["contact_phone"],
            website=sponsor_data["website"],
            description=sponsor_data["description"],
            created_by=1
        )
        session.add(sponsor)
        sponsors.append(sponsor)
    
    await session.commit()
    print(f"✓ Created {len(sponsors)} sponsors")
    return sponsors


async def create_events(session, users, venues):
    """Create test events."""
    print("Creating events...")
    
    events = []
    now = datetime.utcnow()
    
    # Create events over the next 3 months
    for i, title in enumerate(EVENT_TITLES):
        # Mix of scheduled and planning events
        status = "scheduled" if i < 5 else "planning"
        
        # Schedule dates from now to 3 months in the future
        scheduled_date = now + timedelta(days=i*7 + 3)
        
        event = Event(
            title=title,
            description=f"Join us for an in-depth exploration of {TOPICS[i % len(TOPICS)]}. This event features talks from industry experts, hands-on workshops, and networking opportunities.",
            topic=TOPICS[i % len(TOPICS)],
            status=status,
            scheduled_date=scheduled_date,
            venue_id=venues[i % len(venues)].id if status == "scheduled" else None,
            created_by=users[i % len(users)].id
        )
        
        session.add(event)
        events.append(event)
    
    await session.commit()
    
    # Refresh to get IDs
    for event in events:
        await session.refresh(event)
    
    print(f"✓ Created {len(events)} events")
    return events


async def create_organizers(session, users, events):
    """Create event organizers."""
    print("Creating organizers...")
    
    organizers = []
    for i, event in enumerate(events):
        # First user is primary organizer for all events
        organizer = Organizer(
            user_id=1,  # admin user
            event_id=event.id,
            role="primary"
        )
        session.add(organizer)
        organizers.append(organizer)
        
        # Add second organizer for some events
        if i < len(events) // 2:
            organizer = Organizer(
                user_id=2,  # organizer1
                event_id=event.id,
                role="assistant"
            )
            session.add(organizer)
            organizers.append(organizer)
    
    await session.commit()
    print(f"✓ Created {len(organizers)} organizer relationships")
    return organizers


async def create_event_sponsors(session, events, sponsors):
    """Link sponsors to events."""
    print("Creating event sponsorships...")
    
    event_sponsors = []
    sponsorship_levels = ["gold", "silver", "bronze"]
    
    for i, event in enumerate(events):
        # Add 2-3 sponsors per event
        num_sponsors = min(2 + i % 2, len(sponsors))
        for j in range(num_sponsors):
            sponsor = sponsors[(i + j) % len(sponsors)]
            event_sponsor = EventSponsor(
                event_id=event.id,
                sponsor_id=sponsor.id,
                sponsorship_level=sponsorship_levels[j % len(sponsorship_levels)],
                notes=f"Sponsorship for {event.title}"
            )
            session.add(event_sponsor)
            event_sponsors.append(event_sponsor)
    
    await session.commit()
    print(f"✓ Created {len(event_sponsors)} event sponsorships")
    return event_sponsors


async def create_tasks(session, events, users):
    """Create sample tasks for events."""
    print("Creating tasks...")
    
    tasks = []
    task_templates = [
        ("Send reminders to attendees", "todo"),
        ("Prepare presentation slides", "in_progress"),
        ("Book catering", "done"),
        ("Set up registration desk", "todo"),
        ("Create social media posts", "review"),
        ("Send speaker confirmation emails", "done"),
        ("Prepare venue equipment", "todo"),
        ("Review budget estimates", "in_progress")
    ]
    
    for i, event in enumerate(events):
        # Create 3-5 tasks per event
        num_tasks = 3 + i % 3
        for j in range(num_tasks):
            template = task_templates[(i + j) % len(task_templates)]
            task = Task(
                event_id=event.id,
                title=template[0],
                description=f"Task for {event.title}",
                status=template[1],
                assignee_id=users[(i + j) % len(users)].id if j % 2 == 0 else None,
                created_by=1,
                due_date=event.scheduled_date - timedelta(days=1) if event.scheduled_date else None
            )
            session.add(task)
            tasks.append(task)
    
    await session.commit()
    print(f"✓ Created {len(tasks)} tasks")
    return tasks


async def create_marketing_materials(session, events, users):
    """Create sample marketing materials."""
    print("Creating marketing materials...")
    
    materials = []
    material_types = ["post", "email", "social"]
    titles = [
        "Announcement Post",
        "Event Reminder Email",
        "Social Media Blast",
        "Speaker Feature",
        "Last Chance Registration"
    ]
    
    for i, event in enumerate(events):
        # Create 2-3 materials per event
        num_materials = 2 + i % 2
        for j in range(num_materials):
            material = MarketingMaterial(
                event_id=event.id,
                material_type=material_types[j % len(material_types)],
                title=f"{event.title} - {titles[j % len(titles)]}",
                content=f"Join us for {event.title}! {event.description[:100]}...",
                created_by=1
            )
            session.add(material)
            materials.append(material)
    
    await session.commit()
    print(f"✓ Created {len(materials)} marketing materials")
    return materials


async def create_agent_workflows(session, events, users):
    """Create sample agent workflows."""
    print("Creating agent workflows...")
    
    workflows = []
    workflow_types = ["venue_research", "speaker_research", "content_generation"]
    
    for i, event in enumerate(events[:5]):  # Only create for first 5 events
        workflow_type = workflow_types[i % len(workflow_types)]
        workflow = AgentWorkflow(
            workflow_type=workflow_type,
            event_id=event.id,
            user_id=users[i % len(users)].id,
            input_data=f'{{"event_id": {event.id}, "topic": "{event.topic}"}}',
            status="completed" if i < 3 else "pending",
            output_data='{"status": "success", "results": []}',
            started_at=datetime.utcnow() - timedelta(hours=2),
            completed_at=datetime.utcnow() - timedelta(hours=1) if i < 3 else None
        )
        session.add(workflow)
        workflows.append(workflow)
    
    await session.commit()
    print(f"✓ Created {len(workflows)} agent workflows")
    return workflows


async def create_permissions(session, users):
    """Create sample permissions."""
    print("Creating permissions...")
    
    permissions = []
    permission_data = [
        (2, "event", None, "write", 1),  # organizer1 can write to all events
        (2, "event", 1, "admin", 1),     # organizer1 is admin for event 1
        (3, "event", None, "read", 1),   # assistant can read all events
        (3, "event", 2, "write", 1),     # assistant can write to event 2
    ]
    
    for user_id, resource_type, resource_id, permission_level, granted_by in permission_data:
        permission = Permission(
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            permission_level=permission_level,
            granted_by=granted_by
        )
        session.add(permission)
        permissions.append(permission)
    
    await session.commit()
    print(f"✓ Created {len(permissions)} permissions")
    return permissions


async def main():
    """Main function to populate database."""
    print("\n" + "="*60)
    print("POPULATING DATABASE WITH TEST DATA")
    print("="*60 + "\n")
    
    async with async_session_factory() as session:
        try:
            # Create all data
            users = await create_users(session)
            venues = await create_venues(session)
            speakers = await create_speakers(session)
            sponsors = await create_sponsors(session)
            events = await create_events(session, users, venues)
            await create_organizers(session, users, events)
            await create_event_sponsors(session, events, sponsors)
            await create_tasks(session, events, users)
            await create_marketing_materials(session, events, users)
            await create_agent_workflows(session, events, users)
            await create_permissions(session, users)
            
            print("\n" + "="*60)
            print("✅ DATABASE POPULATION COMPLETE!")
            print("="*60)
            print(f"""
Summary:
  - {len(users)} users
  - {len(venues)} venues
  - {len(speakers)} speakers
  - {len(sponsors)} sponsors
  - {len(events)} events
  - Tasks, organizers, sponsorships, marketing materials, and workflows created

Test Credentials:
  - Admin: admin / admin123
  - Organizer: organizer1 / organizer123
  - Assistant: assistant / assistant123
            """)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())

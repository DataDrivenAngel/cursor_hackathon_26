Write a plan for a meetup organizing information support system that stores information on events, organizers, attendees, venues, sponsors, and planning tasks.

The system must support: 
- Organizers brainstorming events with topic recommendations based on historical events.
- Organizers scheduling events via integrations with meetup and luma.
- Organizers doing venue research via agentic workflows (Implemented in basic python using minimax for the api). The agentic workflows should both look at existing venues and also find other venues by using perplexity search. 
- Organizers doing speaker research via agentic workflows that search for potential local speakers. This workflow should also do enrichment on previous event attendees by name and email. 
- The system should help market scheduled events by drafting marketing materials for organizers to post.


Additionally, the system should support basic organizational maintenance tasks:
- Organizers managing system permissions for volunteers and assistant organizers. 
- The system should have a visual kanban interface for planning.

The system should use sqlite to store information in a relational format. Implement it using fastapi and an extremely minimal html and css framework with minimal htmx interactivity.
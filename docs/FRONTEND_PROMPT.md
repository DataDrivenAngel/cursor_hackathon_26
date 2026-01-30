# Frontend Implementation Prompt

## Context and Role

You are a senior frontend developer specializing in modern web applications using Jinja2 templating, HTMX for reactive interfaces, and CSS animations. Your task is to implement the frontend for an Event Management System with a focus on creating an engaging, active workflow visualization experience. The application helps users plan and manage events through a structured workflow system with detailed progress tracking.

## Project Overview

The existing codebase is a FastAPI-based web application with:
- Jinja2 templates in `app/templates/`
- HTMX for AJAX interactions
- CSS stylesheets in `app/static/style.css`
- Workflow models defined in `app/models/workflow_models.py`
- Workflow service in `app/services/workflow_service.py`
- Existing templates for events, workflow, and base layout

Your goal is to enhance the frontend to create a highly interactive, animated experience that makes workflow progress feel alive and actively tracks detailed metrics.

## Core Requirements

### 1. Create Event Wizard (Priority: HIGH)

Implement a multi-step event creation wizard with the following specifications:

**Step Structure:**
- Step 1: Event Basics - title, description, topic
- Step 2: Scheduling - date/time, registration deadline, event format (in-person/virtual/hybrid)
- Step 3: Resources - venue preferences, speaker requirements, sponsor info
- Step 4: Review - summary of all entered information

**Functional Requirements:**
- Progress indicator showing current step with checkmarks for completed steps
- Form validation at each step preventing progression until valid
- Previous/Next navigation buttons with proper state management
- HTMX-based submission on final step
- Immediate workflow generation upon successful creation

**Implementation Files:**
- Update `app/templates/events.html` to include the wizard modal
- Create `app/templates/components/event-wizard.html` for wizard partial
- Add wizard styles to `app/static/style.css`
- Add wizard JavaScript to handle step navigation and validation

**Success Criteria:**
- Users can create events through a guided 4-step process
- Validation prevents invalid data submission at each step
- Upon creation, user is redirected to the workflow page with generated tasks
- The transition includes an animation showing workflow "building"

### 2. Active Workflow Visualization (Priority: HIGH)

Implement animated progress indicators that convey active, ongoing progress:

**Overall Progress Display:**
- Circular progress indicator with sweeping animation
- Gradient coloring (red → yellow → green) based on completion percentage
- Smooth animations when progress updates
- Subtle pulse animation during active planning periods

**Phase Progress Bar:**
- Six phases: Ideation, Logistics, Marketing, Preparation, Execution, Review
- Each phase represented as a colored segment proportional to weight
- Phase cards display: icon, name, progress bar, percentage, task count
- Active phases pulse gently to indicate current focus
- Completed phases show checkmark overlay with reduced opacity
- Phases with blocked tasks display warning indicator

**Task Completion Animation:**
When a task transitions to "done":
1. Task card expands and glows green momentarily
2. Task counts update in column headers
3. Progress percentages update with number transition animation
4. Phase progress bars advance proportionally

**Implementation Approach:**
- Add CSS animations for progress indicators in `style.css`
- Create JavaScript module for progress animation handling
- Use HTMX poll trigger for real-time updates (30-second interval)
- Coordinate animations across components for cohesive feedback

**Success Criteria:**
- Progress indicators animate smoothly on updates
- Users can see progress changes immediately after completing tasks
- Active phases draw attention without being distracting
- The interface feels alive and responsive to user actions

### 3. Animated Phase Transitions (Priority: MEDIUM)

Implement celebration animations for phase completion:

**Phase Completion Animation:**
1. Progress bar fills completely and turns green
2. Confetti effect radiates from phase card center
3. Phase icon animates through celebration sequence
4. "Phase Complete" message appears momentarily
5. Phase card transitions to completed state with checkmark overlay

**Phase Activation Animation:**
1. Next phase card pulses with increasing intensity
2. Phase icon transitions from dormant to active state
3. Progress bar initializes from zero with filling animation
4. Announcement message describes the new phase and its purpose

**Implementation Files:**
- Add keyframe animations to `style.css`
- Create animation JavaScript module for triggering sequences
- Add confetti library or custom confetti implementation

**Success Criteria:**
- Phase transitions feel celebratory and motivating
- Users understand when they've completed a phase
- The next phase is clearly activated and ready for work

### 4. Dynamic Task Board (Priority: HIGH)

Implement a Kanban-style task management interface:

**Columns:**
- To Do (gray background)
- In Progress (blue accent)
- Review (purple accent)
- Done (green accent)

**Task Card Design:**
- Priority badge: Critical (red), High (orange), Medium (yellow), Low (purple)
- Category badge: Speakers, Venue, Marketing, Sponsors, etc.
- Title with full text
- Description truncated to 2 lines when long
- Due date with overdue highlighting in red
- Action buttons appropriate to status

**Blocked Task Visual Treatment:**
- Thick red border with diagonal striped overlay
- "BLOCKED" badge at top of card
- Tooltip reveals blocking reason on hover
- Drag attempts trigger shaking animation (rejecting move)
- Unblocking removes barrier visual treatment

**Drag-and-Drop:**
- HTML5 Drag and Drop API with click-to-move fallback
- Card becomes semi-transparent with drop shadow when dragging
- Valid drop targets highlight green, invalid highlight red
- Smooth snap animation when dropped
- Backend receives updated position for progress recalculation

**Implementation Files:**
- Update `app/templates/event_workflow.html` task board section
- Add task board styles to `style.css`
- Create `static/js/taskboard.js` for drag-and-drop logic
- Add column-specific styles for visual distinction

**Success Criteria:**
- Users can move tasks between columns via drag-and-drop
- Blocked tasks are visually distinct and cannot be moved
- Task cards display all relevant information clearly
- The board feels responsive and interactive

### 5. Overly Detailed Progress Tracking (Priority: MEDIUM)

Implement comprehensive multi-dimensional progress metrics:

**Progress Dimensions:**
- Phase progress (weighted calculation across 6 phases)
- Category progress (Speakers, Venue, Marketing, Sponsors, etc.)
- Time-based progress (planned vs actual comparison)
- Milestone completion tracking

**Category Progress Radial Chart:**
- Segments for each category with completion percentage
- Color-coded category identification
- Hover reveals detailed task counts and remaining tasks

**Time-Based Progress Visualization:**
- Expected progress curve based on event date
- Actual progress plotted against expected
- Warning colors for behind-schedule periods
- Positive colors for ahead-of-schedule progress

**Milestone Timeline:**
- Horizontal timeline spanning full planning period
- Completed milestones: green with checkmarks
- Upcoming milestones: blue with date
- Overdue milestones: red with urgency indicators
- Critical path milestones: gold border and icon
- Connecting line traces critical path through milestones

**Implementation Files:**
- Create `app/templates/components/progress-metrics.html`
- Add radial chart and timeline styles to `style.css`
- Create JavaScript module for interactive visualizations
- Update workflow service to provide multi-dimensional progress data

**Success Criteria:**
- Users can view progress from multiple angles
- Category breakdown shows where effort is concentrated
- Time-based comparison helps identify scheduling issues
- Milestone timeline provides clear deadline visibility

### 6. Micro-Interactions and Feedback (Priority: MEDIUM)

Implement satisfying feedback for user actions:

**Button Interactions:**
- Hover: brighten background, subtle lift effect
- Active: depress button, brighten further
- Disabled: gray background, no pointer events
- Loading: spinner animation replaces content
- Success: brief checkmark animation

**Form Field Interactions:**
- Focus: highlight border, show help text
- Valid input: brief green border flash
- Invalid input: red border shake animation
- Success: field-flourish animation

**Card/List Interactions:**
- Hover: lift and add shadow depth
- Drag: semi-transparent clone follows cursor
- Drop: smooth snap animation into position
- Delete: crumbling animation

**Implementation Approach:**
- Add CSS classes for each interaction state
- Create JavaScript utilities for complex animations
- Centralize animation timing in shared module
- Ensure all interactions complete in under 200ms

**Success Criteria:**
- Every user action receives immediate visual feedback
- Interactions feel consistent across all components
- Animations enhance without distracting from content

### 7. Notification System (Priority: LOW)

Implement comprehensive notification delivery:

**Toast Notifications:**
- Success (green, checkmark, 3s auto-dismiss)
- Warning (yellow, exclamation, 5s auto-dismiss)
- Error (red, X, manual dismiss)
- Info (blue, info icon, 4s auto-dismiss)

**Alert Banners:**
- Persistent at top of content areas
- Warning, Error, and Success variants
- Dismiss button for each
- Can be dismissed permanently or temporarily

**Notification Center:**
- Bell icon with unread count badge
- Dropdown panel with recent notifications
- Mark as read/dismiss individual items
- History of dismissed notifications

**Implementation Files:**
- Create `app/templates/components/notifications.html`
- Add notification styles to `style.css`
- Create `static/js/notifications.js` for management logic

**Success Criteria:**
- Users receive appropriate feedback for all operations
- Notifications can be dismissed easily
- Important alerts persist until addressed

### 8. Accessibility Implementation (Priority: REQUIRED)

Ensure WCAG 2.1 AA compliance:

**Keyboard Navigation:**
- All elements reachable via Tab
- Logical tab order matching visual layout
- Visible focus indicators
- Keyboard alternatives for drag-and-drop
- Focus trapping in modals

**Screen Reader Support:**
- Descriptive alt text for all images
- ARIA labels for interactive elements
- ARIA live regions for dynamic content
- aria-describedby for form validation errors
- Detailed descriptions for complex components

**Color Independence:**
- Iconography supplements color for status
- Patterns/labels for chart data series
- High-contrast focus indicators
- Respect `prefers-reduced-motion` setting

**Implementation Approach:**
- Audit all components for accessibility
- Add ARIA attributes throughout templates
- Implement keyboard navigation JavaScript
- Test with screen readers

**Success Criteria:**
- Complete keyboard accessibility
- Screen reader compatibility for all content
- Color-independent information delivery
- Reduced motion support

## Technical Specifications

### CSS Architecture

**Naming Convention (BEM):**
- Blocks: `event-wizard`, `workflow-progress-bar`, `task-column`
- Elements: `task-card__header`, `phase-progress__fill`
- Modifiers: `task-card--completed`, `btn--primary`

**CSS Custom Properties:**
```css
:root {
  /* Colors */
  --color-primary: #3b82f6;
  --color-success: #22c55e;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  
  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  
  /* Animation */
  --transition-fast: 150ms;
  --transition-normal: 300ms;
  --transition-slow: 500ms;
}
```

**Responsive Design:**
- Mobile-first approach
- Min-width media queries for breakpoints
- 768px for tablet
- 1024px for desktop
- 1400px for wide desktop

### JavaScript Module Structure

**Module Pattern:**
```javascript
// static/js/components/component-name.js
import { animate, durations } from '../utils/animation.js';

export function init() {
  // Locate component elements
  // Set up event listeners
  // Initialize state
  return { destroy };
}

function handleEvent() {
  // Event handling logic
}

function destroy() {
  // Cleanup
}
```

**Event Handling:**
- Delegation pattern for container-level listeners
- Cleanup on component removal
- Consistent naming for custom events

### HTMX Integration Patterns

**Request Handling:**
```html
<button hx-post="/events"
        hx-target="#events-grid"
        hx-swap="outerHTML"
        hx-indicator="#loading">
  Create Event
</button>
```

**Real-Time Updates:**
```html
<div hx-get="/events/{id}/workflow/progress"
     hx-trigger="load, every 30s">
  <!-- Progress content -->
</div>
```

**Form Submission:**
```html
<form hx-post="/events"
      hx-target="#events-grid"
      hx-swap="outerHTML">
```

## File Structure to Create/Modify

### New Files:
- `app/templates/components/event-wizard.html`
- `app/templates/components/progress-metrics.html`
- `app/templates/components/notifications.html`
- `app/templates/components/task-card.html`
- `app/templates/components/milestone-timeline.html`
- `static/js/event-wizard.js`
- `static/js/taskboard.js`
- `static/js/progress-animations.js`
- `static/js/notifications.js`
- `static/js/accessibility.js`
- `static/js/utils/animation.js`

### Files to Modify:
- `app/templates/base.html` - Add notification container, accessibility enhancements
- `app/templates/events.html` - Add wizard modal, update event list
- `app/templates/event_workflow.html` - Enhance workflow visualization
- `app/static/style.css` - Add all component styles and animations

## Implementation Order

1. **Phase 1: Foundation**
   - Update base template with notification container
   - Add core CSS variables and utilities
   - Implement accessibility base styles

2. **Phase 2: Event Creation**
   - Create event wizard HTML structure
   - Add wizard CSS and basic JavaScript
   - Implement form validation

3. **Phase 3: Workflow Visualization**
   - Add progress indicator styles and animations
   - Implement phase progress bar
   - Add task board styles and drag-and-drop

4. **Phase 4: Polish**
   - Implement micro-interactions
   - Add notification system
   - Complete accessibility implementation

5. **Phase 5: Advanced Features**
   - Add multi-dimensional progress metrics
   - Implement milestone timeline
   - Add celebration animations

## Quality Standards

- All animations under 200ms for micro-interactions
- Mobile-responsive at all breakpoints
- WCAG 2.1 AA compliant
- Browser testing: Chrome, Firefox, Safari, Edge
- Progressive enhancement: core functionality without JavaScript

## Additional Considerations

- HTMX should handle all data loading and form submissions
- JavaScript only for interactions not possible with HTMX
- Server-side rendering for initial page loads
- Polling for real-time updates (no WebSockets required)
- Clean separation between template and JavaScript logic

## Reference Files

- Current templates: `app/templates/*.html`
- Workflow models: `app/models/workflow_models.py`
- Workflow service: `app/services/workflow_service.py`
- Existing styles: `app/static/style.css`

---

## Instructions for AI Assistant

When implementing based on this prompt:

1. **Start with the foundation** - Set up CSS variables, base styles, and accessibility groundwork
2. **Implement incrementally** - Complete one component before moving to the next
3. **Follow the specifications** - Use exact class names, file locations, and patterns specified
4. **Test interactively** - Verify animations and interactions work as expected
5. **Maintain consistency** - Use existing code patterns and style conventions
6. **Prioritize accessibility** - Ensure all new components meet accessibility standards

Ask clarifying questions if any requirements are ambiguous, and suggest improvements if you identify better approaches that still meet the core goals.

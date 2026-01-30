"""
AI Workflow Service - Intelligent task analysis and recommendations.
"""
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict


class TaskPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"


class WorkflowPhase(Enum):
    IDEATION = "ideation"
    LOGISTICS = "logistics"
    MARKETING = "marketing"
    PREPARATION = "preparation"
    EXECUTION = "execution"
    REVIEW = "review"


@dataclass
class AITask:
    """Represents a task for AI analysis."""
    id: str
    title: str
    description: str
    status: str
    priority: str
    category: str
    phase: str
    due_date: Optional[datetime]
    is_blocked: bool
    blocking_reason: Optional[str]
    assignee: Optional[str]
    created_at: datetime
    updated_at: datetime


@dataclass
class AIWorkflowInsight:
    """Represents an AI-generated insight."""
    type: str  # suggestion, warning, tip, prediction
    category: str  # priority, timeline, resources, dependencies, quality
    title: str
    description: str
    confidence: float  # 0.0 to 1.0
    actionable: bool
    related_task_ids: List[str]
    recommendation: Optional[str]
    impact: str  # high, medium, low


@dataclass
class AIPriorityRecommendation:
    """Represents AI-suggested task priority."""
    task_id: str
    suggested_priority: str
    reason: str
    factors: List[str]
    score: float


@dataclass
class AITimelinePrediction:
    """Represents AI timeline analysis."""
    predicted_completion: Optional[datetime]
    risk_level: str  # low, medium, high
    factors: List[str]
    recommendations: List[str]
    confidence: float


class AIWorkflowAnalyzer:
    """
    AI-powered workflow analyzer that provides intelligent insights
    and recommendations for event planning tasks.
    """
    
    def __init__(self):
        self.priority_weights = {
            TaskPriority.CRITICAL: 4.0,
            TaskPriority.HIGH: 3.0,
            TaskPriority.MEDIUM: 2.0,
            TaskPriority.LOW: 1.0,
        }
        
        self.status_urgency = {
            TaskStatus.BLOCKED: 4.0,
            TaskStatus.IN_PROGRESS: 3.0,
            TaskStatus.TODO: 2.0,
            TaskStatus.REVIEW: 1.5,
            TaskStatus.DONE: 0.0,
        }
    
    async def analyze_workflow(
        self,
        tasks: List[AITask],
        event_date: Optional[datetime],
        current_phase: str
    ) -> Dict[str, Any]:
        """Perform comprehensive workflow analysis."""
        
        insights = []
        priority_recommendations = []
        
        # Analyze different aspects
        insights.extend(await self._analyze_blocked_tasks(tasks))
        insights.extend(await self._analyze_overdue_tasks(tasks))
        insights.extend(await self._analyze_prioritization(tasks, event_date))
        insights.extend(await self._analyze_workload_distribution(tasks))
        insights.extend(await self._analyze_phase_progress(tasks, current_phase))
        insights.extend(await self._analyze_timeline_risks(tasks, event_date))
        insights.extend(await self._analyze_resource_gaps(tasks))
        insights.extend(await self._analyze_dependencies(tasks))
        
        # Generate priority recommendations
        priority_recommendations = await self._generate_priority_recommendations(tasks, event_date)
        
        # Calculate overall health score
        health_score = self._calculate_workflow_health(tasks, event_date)
        
        # Generate timeline prediction
        timeline_prediction = await self._predict_completion(tasks, event_date)
        
        return {
            "insights": [i.__dict__ for i in insights],
            "priority_recommendations": [r.__dict__ for r in priority_recommendations],
            "health_score": health_score,
            "timeline_prediction": timeline_prediction.__dict__ if timeline_prediction else None,
            "summary": self._generate_summary(insights, health_score),
        }
    
    async def _analyze_blocked_tasks(self, tasks: List[AITask]) -> List[AIWorkflowInsight]:
        """Analyze blocked tasks and provide recommendations."""
        insights = []
        
        blocked_tasks = [t for t in tasks if t.is_blocked]
        
        if not blocked_tasks:
            return insights
        
        # Group blocked tasks by reason
        reasons = defaultdict(list)
        for task in blocked_tasks:
            reason = task.blocking_reason or "Unknown reason"
            reasons[reason].append(task)
        
        for reason, task_list in reasons.items():
            insight = AIWorkflowInsight(
                type="warning",
                category="dependencies",
                title=f"Blocked Tasks: {len(task_list)} task(s) waiting on dependencies",
                description=f"Tasks blocked due to: '{reason}'. This is preventing progress on critical path items.",
                confidence=0.95,
                actionable=True,
                related_task_ids=[t.id for t in task_list],
                recommendation=f"Address the blocking issue: {reason}",
                impact="high"
            )
            insights.append(insight)
        
        # Check for critical blocked tasks
        critical_blocked = [t for t in blocked_tasks if t.priority == "critical"]
        if critical_blocked:
            insight = AIWorkflowInsight(
                type="warning",
                category="priority",
                title="Critical tasks are blocked!",
                description=f"{len(critical_blocked)} critical task(s) are currently blocked. This poses significant risk to the event.",
                confidence=0.98,
                actionable=True,
                related_task_ids=[t.id for t in critical_blocked],
                recommendation="Immediately resolve blockers on critical tasks or escalate to leadership.",
                impact="critical"
            )
            insights.insert(0, insight)
        
        return insights
    
    async def _analyze_overdue_tasks(self, tasks: List[AITask]) -> List[AIWorkflowInsight]:
        """Analyze overdue tasks."""
        insights = []
        now = datetime.utcnow()
        
        overdue_tasks = [
            t for t in tasks
            if t.due_date and t.due_date < now
            and t.status not in [TaskStatus.DONE.value, TaskStatus.BLOCKED.value]
        ]
        
        if not overdue_tasks:
            return insights
        
        # Categorize by days overdue
        very_overdue = [t for t in overdue_tasks if (now - t.due_date).days > 7]
        moderately_overdue = [t for t in overdue_tasks if 3 < (now - t.due_date).days <= 7]
        slightly_overdue = [t for t in overdue_tasks if (now - t.due_date).days <= 3]
        
        if very_overdue:
            insights.append(AIWorkflowInsight(
                type="warning",
                category="timeline",
                title=f"Critical: {len(very_overdue)} task(s) severely overdue",
                description="These tasks are more than 7 days past their due date and require immediate attention.",
                confidence=0.95,
                actionable=True,
                related_task_ids=[t.id for t in very_overdue],
                recommendation="Consider reassigning these tasks or extending scope to fit realistic timeline.",
                impact="critical"
            ))
        
        if moderately_overdue:
            insights.append(AIWorkflowInsight(
                type="warning",
                category="timeline",
                title=f"Alert: {len(moderately_overdue)} task(s) moderately overdue",
                description="These tasks are 4-7 days past due and need prioritization.",
                confidence=0.90,
                actionable=True,
                related_task_ids=[t.id for t in moderately_overdue],
                recommendation="Schedule these tasks for completion within the next 48 hours.",
                impact="high"
            ))
        
        if slightly_overdue:
            insights.append(AIWorkflowInsight(
                type="suggestion",
                category="timeline",
                title=f"Notice: {len(slightly_overdue)} task(s) slightly overdue",
                description="These tasks are just a few days past due.",
                confidence=0.85,
                actionable=True,
                related_task_ids=[t.id for t in slightly_overdue],
                recommendation="Complete these tasks to maintain schedule integrity.",
                impact="medium"
            ))
        
        return insights
    
    async def _analyze_prioritization(
        self,
        tasks: List[AITask],
        event_date: Optional[datetime]
    ) -> List[AIWorkflowInsight]:
        """Analyze and suggest optimal task prioritization."""
        insights = []
        now = datetime.utcnow()
        
        # Identify tasks that should be prioritized
        incomplete_tasks = [
            t for t in tasks
            if t.status in [TaskStatus.TODO.value, TaskStatus.IN_PROGRESS.value]
            and not t.is_blocked
        ]
        
        # Calculate priority scores
        scored_tasks = []
        for task in incomplete_tasks:
            score = self._calculate_priority_score(task, event_date, now)
            scored_tasks.append((task, score))
        
        # Sort by score
        scored_tasks.sort(key=lambda x: x[1], reverse=True)
        
        # Get top 3 tasks that might be overlooked
        todo_tasks = [t for t, s in scored_tasks if t.status == TaskStatus.TODO.value]
        in_progress_tasks = [t for t, s in scored_tasks if t.status == TaskStatus.IN_PROGRESS.value]
        
        # Find high-value todo tasks
        if len(todo_tasks) > 3:
            high_value_todos = [
                t for t, s in scored_tasks[:5]
                if t.status == TaskStatus.TODO.value
            ]
            
            if high_value_todos:
                task_titles = ", ".join([t.title for t in high_value_todos[:2]])
                insight = AIWorkflowInsight(
                    type="suggestion",
                    category="priority",
                    title="High-priority tasks need attention",
                    description=f"Consider starting: {task_titles}. These tasks have high urgency based on deadlines and event timeline.",
                    confidence=0.82,
                    actionable=True,
                    related_task_ids=[t.id for t in high_value_todos],
                    recommendation="Prioritize these tasks in your next work session.",
                    impact="high"
                )
                insights.append(insight)
        
        # Check for task imbalance (too many low priority tasks in progress)
        in_progress = [t for t in incomplete_tasks if t.status == TaskStatus.IN_PROGRESS.value]
        low_priority_in_progress = [
            t for t in in_progress
            if t.priority in [TaskPriority.LOW.value, TaskPriority.MEDIUM.value]
            and t.due_date
            and (t.due_date - now).days > 14
        ]
        
        if len(low_priority_in_progress) > 2:
            insight = AIWorkflowInsight(
                type="tip",
                category="resources",
                title="Consider pausing low-priority work",
                description=f"{len(low_priority_in_progress)} lower-priority tasks are in progress while higher-priority items await.",
                confidence=0.75,
                actionable=True,
                related_task_ids=[t.id for t in low_priority_in_progress],
                recommendation="Consider moving these tasks back to todo to focus on higher-priority work.",
                impact="medium"
            )
            insights.append(insight)
        
        return insights
    
    async def _analyze_workload_distribution(self, tasks: List[AITask]) -> List[AIWorkflowInsight]:
        """Analyze workload distribution across team members."""
        insights = []
        
        # Group tasks by assignee
        assignee_tasks = defaultdict(list)
        for task in tasks:
            if task.assignee:
                assignee_tasks[task.assignee].append(task)
        
        # Find workload imbalances
        workloads = []
        for assignee, task_list in assignee_tasks.items():
            incomplete = [
                t for t in task_list
                if t.status not in [TaskStatus.DONE.value]
            ]
            workloads.append((assignee, len(incomplete)))
        
        if len(workloads) < 2:
            return insights
        
        workloads.sort(key=lambda x: x[1], reverse=True)
        
        max_workload = workloads[0][1]
        min_workload = workloads[-1][1]
        
        # Check for significant imbalance
        if max_workload > min_workload * 2 and max_workload > 3:
            overloaded = workloads[0][0]
            underutilized = [a for a, _ in workloads[-2:] if _ > 0]
            
            insight = AIWorkflowInsight(
                type="suggestion",
                category="resources",
                title="Workload imbalance detected",
                description=f"{overloaded} has {max_workload} pending tasks while team members have fewer items.",
                confidence=0.85,
                actionable=True,
                related_task_ids=[],
                recommendation=f"Consider reassigning some tasks from {overloaded} to team members with capacity.",
                impact="medium"
            )
            insights.append(insight)
        
        # Check for unassigned tasks
        unassigned = [
            t for t in tasks
            if not t.assignee
            and t.status not in [TaskStatus.DONE.value]
        ]
        
        if len(unassigned) > 2:
            insight = AIWorkflowInsight(
                type="tip",
                category="resources",
                title=f"{len(unassigned)} tasks are unassigned",
                description="These tasks need team members to take ownership.",
                confidence=0.90,
                actionable=True,
                related_task_ids=[t.id for t in unassigned[:5]],
                recommendation="Assign these tasks to team members based on their skills and current workload.",
                impact="high"
            )
            insights.append(insight)
        
        return insights
    
    async def _analyze_phase_progress(
        self,
        tasks: List[AITask],
        current_phase: str
    ) -> List[AIWorkflowInsight]:
        """Analyze progress within each workflow phase."""
        insights = []
        
        phase_tasks = defaultdict(list)
        for task in tasks:
            phase_tasks[task.phase].append(task)
        
        # Check for lagging phases
        phase_order = [
            WorkflowPhase.IDEATION.value,
            WorkflowPhase.LOGISTICS.value,
            WorkflowPhase.MARKETING.value,
            WorkflowPhase.PREPARATION.value,
            WorkflowPhase.EXECUTION.value,
            WorkflowPhase.REVIEW.value,
        ]
        
        current_phase_idx = phase_order.index(current_phase) if current_phase in phase_order else 0
        
        for i, phase in enumerate(phase_order):
            phase_task_list = phase_tasks.get(phase, [])
            
            if not phase_task_list:
                continue
            
            completed = len([t for t in phase_task_list if t.status == TaskStatus.DONE.value])
            total = len(phase_task_list)
            progress = completed / total if total > 0 else 0
            
            # Check if we're behind schedule for this phase
            if i < current_phase_idx and progress < 0.8:
                insight = AIWorkflowInsight(
                    type="warning",
                    category="quality",
                    title=f"{phase.title()} phase is behind",
                    description=f"Only {completed}/{total} tasks completed in {phase.title()}. This may impact subsequent phases.",
                    confidence=0.88,
                    actionable=True,
                    related_task_ids=[t.id for t in phase_task_list if t.status != TaskStatus.DONE.value],
                    recommendation=f"Complete remaining {phase} tasks before advancing to next phase.",
                    impact="high"
                )
                insights.append(insight)
            
            # Check if current phase is ready to advance
            if i == current_phase_idx and progress >= 0.9:
                insight = AIWorkflowInsight(
                    type="suggestion",
                    category="quality",
                    title=f"Ready to advance from {phase.title()}",
                    description=f"90%+ of {phase} tasks are complete. Consider advancing to next phase.",
                    confidence=0.92,
                    actionable=False,
                    related_task_ids=[],
                    recommendation="Update workflow phase when ready to proceed.",
                    impact="medium"
                )
                insights.append(insight)
        
        return insights
    
    async def _analyze_timeline_risks(
        self,
        tasks: List[AITask],
        event_date: Optional[datetime]
    ) -> List[AIWorkflowInsight]:
        """Analyze timeline risks and provide predictions."""
        insights = []
        
        if not event_date:
            return insights
        
        now = datetime.utcnow()
        days_until = (event_date - now).days
        
        if days_until <= 0:
            return insights
        
        # Identify tasks at risk of not being completed
        at_risk_tasks = []
        for task in tasks:
            if task.status == TaskStatus.DONE.value or task.is_blocked:
                continue
            
            if not task.due_date:
                continue
            
            days_until_due = (task.due_date - now).days
            effort_days = self._estimate_effort(task)
            
            if days_until_due < effort_days:
                at_risk_tasks.append((task, days_until_due, effort_days))
        
        if at_risk_tasks:
            critical_at_risk = [
                (t, d, e) for t, d, e in at_risk_tasks
                if d < e * 0.5
            ]
            
            if critical_at_risk:
                task_titles = ", ".join([t.title for t, _, _ in critical_at_risk[:3]])
                insight = AIWorkflowInsight(
                    type="warning",
                    category="timeline",
                    title="Tasks at critical risk of missing deadlines",
                    description=f"Some tasks have insufficient time for completion: {task_titles}",
                    confidence=0.90,
                    actionable=True,
                    related_task_ids=[t.id for t, _, _ in critical_at_risk],
                    recommendation="Either extend deadlines, increase resources, or reduce task scope.",
                    impact="critical"
                )
                insights.append(insight)
        
        # General timeline health check
        incomplete = [
            t for t in tasks
            if t.status != TaskStatus.DONE.value and not t.is_blocked
        ]
        
        if incomplete and days_until > 0:
            avg_days_per_task = days_until / len(incomplete)
            
            if avg_days_per_task < 1:
                insight = AIWorkflowInsight(
                    type="warning",
                    category="timeline",
                    title="Timeline under severe pressure",
                    description="Less than 1 day remaining per incomplete task on average.",
                    confidence=0.95,
                    actionable=True,
                    related_task_ids=[],
                    recommendation="Consider extending event date, reducing scope, or adding resources.",
                    impact="critical"
                )
                insights.append(insight)
            elif avg_days_per_task < 2:
                insight = AIWorkflowInsight(
                    type="warning",
                    category="timeline",
                    title="Timeline is tight",
                    description="Less than 2 days per task on average. Focus on high-priority items.",
                    confidence=0.80,
                    actionable=True,
                    related_task_ids=[],
                    recommendation="Prioritize critical and high-priority tasks only.",
                    impact="high"
                )
                insights.append(insight)
        
        return insights
    
    async def _analyze_resource_gaps(self, tasks: List[AITask]) -> List[AIWorkflowInsight]:
        """Analyze potential resource gaps."""
        insights = []
        
        # Check for skill-related tasks without appropriate categories
        category_counts = defaultdict(int)
        for task in tasks:
            if task.status != TaskStatus.DONE.value:
                category_counts[task.category] += 1
        
        # Check for common resource needs
        if category_counts.get("speakers", 0) > 5:
            insight = AIWorkflowInsight(
                type="tip",
                category="resources",
                title="High speaker coordination workload",
                description="Managing multiple speaker-related tasks. Consider dedicated speaker coordinator.",
                confidence=0.75,
                actionable=False,
                related_task_ids=[],
                recommendation="Assign a point person for speaker communications.",
                impact="medium"
            )
            insights.append(insight)
        
        if category_counts.get("marketing", 0) > 5:
            insight = AIWorkflowInsight(
                type="suggestion",
                category="resources",
                title="Marketing tasks piling up",
                description="Multiple marketing tasks pending. Marketing efforts may be lagging.",
                confidence=0.80,
                actionable=True,
                related_task_ids=[],
                recommendation="Increase marketing focus or hire external support.",
                impact="high"
            )
            insights.append(insight)
        
        return insights
    
    async def _analyze_dependencies(self, tasks: List[AITask]) -> List[AIWorkflowInsight]:
        """Analyze task dependencies and potential bottlenecks."""
        insights = []
        
        # Find tasks that might be dependencies for many other tasks
        potential_blockers = [t for t in tasks if t.is_blocked]
        
        if len(potential_blockers) > 3:
            insight = AIWorkflowInsight(
                type="warning",
                category="dependencies",
                title="Multiple blocking dependencies",
                description=f"{len(potential_blockers)} tasks are currently blocked. This creates significant project risk.",
                confidence=0.92,
                actionable=True,
                related_task_ids=[t.id for t in potential_blockers],
                recommendation="Conduct dependency review meeting to unblock critical path items.",
                impact="high"
            )
            insights.append(insight)
        
        # Check for concentration of tasks in single phase
        phase_counts = defaultdict(int)
        for task in tasks:
            if task.status != TaskStatus.DONE.value:
                phase_counts[task.phase] += 1
        
        max_phase = max(phase_counts, key=phase_counts.get) if phase_counts else None
        if max_phase and phase_counts[max_phase] > 8:
            insight = AIWorkflowInsight(
                type="tip",
                category="resources",
                title=f"Heavy workload in {max_phase.title()} phase",
                description=f"{phase_counts[max_phase]} tasks pending in {max_phase}. Consider breaking into smaller phases.",
                confidence=0.78,
                actionable=True,
                related_task_ids=[],
                recommendation="Decompose complex tasks into smaller, manageable subtasks.",
                impact="medium"
            )
            insights.append(insight)
        
        return insights
    
    async def _generate_priority_recommendations(
        self,
        tasks: List[AITask],
        event_date: Optional[datetime]
    ) -> List[AIPriorityRecommendation]:
        """Generate AI-powered priority recommendations."""
        recommendations = []
        now = datetime.utcnow()
        
        incomplete_tasks = [
            t for t in tasks
            if t.status in [TaskStatus.TODO.value, TaskStatus.IN_PROGRESS.value]
            and not t.is_blocked
        ]
        
        for task in incomplete_tasks:
            score = self._calculate_priority_score(task, event_date, now)
            current_priority = task.priority
            
            # Determine if priority should change
            if score >= 3.5 and current_priority not in ["critical", "high"]:
                recommendations.append(AIPriorityRecommendation(
                    task_id=task.id,
                    suggested_priority="high",
                    reason="AI analysis indicates this task is more urgent than current priority suggests",
                    factors=self._get_priority_factors(task, event_date, now),
                    score=score
                ))
            elif score <= 1.5 and current_priority in ["critical", "high"]:
                recommendations.append(AIPriorityRecommendation(
                    task_id=task.id,
                    suggested_priority="medium",
                    reason="AI analysis indicates this task can be deprioritized based on timeline and dependencies",
                    factors=self._get_priority_factors(task, event_date, now),
                    score=score
                ))
        
        return recommendations
    
    async def _predict_completion(
        self,
        tasks: List[AITask],
        event_date: Optional[datetime]
    ) -> Optional[AITimelinePrediction]:
        """Predict timeline completion and risks."""
        
        incomplete = [
            t for t in tasks
            if t.status != TaskStatus.DONE.value and not t.is_blocked
        ]
        
        if not incomplete:
            return None
        
        now = datetime.utcnow()
        
        # Calculate estimated effort
        total_effort = sum(self._estimate_effort(t) for t in incomplete)
        
        # Assume 1 person can complete ~3 tasks per day
        tasks_per_day_per_person = 3
        people_count = len(set(t.assignee for t in incomplete if t.assignee)) or 1
        daily_capacity = tasks_per_day_per_person * people_count
        
        days_needed = total_effort / daily_capacity
        
        if event_date:
            days_until = (event_date - now).days
            
            if days_needed > days_until:
                return AITimelinePrediction(
                    predicted_completion=now + timedelta(days=days_needed),
                    risk_level="high",
                    factors=[
                        f"Estimated effort ({days_needed:.1f} days) exceeds available time ({days_until} days)",
                        f"{len(incomplete)} tasks remaining",
                    ],
                    recommendations=[
                        "Reduce task scope",
                        "Add more resources",
                        "Extend event date if possible",
                    ],
                    confidence=0.70
                )
            elif days_needed > days_until * 0.7:
                return AITimelinePrediction(
                    predicted_completion=now + timedelta(days=days_needed),
                    risk_level="medium",
                    factors=[
                        f"Timeline is tight with {days_needed:.1f} days needed vs {days_until} available",
                    ],
                    recommendations=[
                        "Focus on critical path items",
                        "Minimize scope creep",
                        "Monitor progress daily",
                    ],
                    confidence=0.80
                )
            else:
                return AITimelinePrediction(
                    predicted_completion=now + timedelta(days=days_needed),
                    risk_level="low",
                    factors=[
                        f"Healthy timeline with {days_until - days_needed:.1f} days buffer",
                    ],
                    recommendations=[
                        "Maintain current pace",
                        "Address blockers quickly",
                    ],
                    confidence=0.85
                )
        
        return AITimelinePrediction(
            predicted_completion=now + timedelta(days=days_needed),
            risk_level="medium",
            factors=[f"{len(incomplete)} tasks remaining, ~{total_effort:.1f} days of effort"],
            recommendations=["Continue monitoring progress"],
            confidence=0.65
        )
    
    def _calculate_priority_score(
        self,
        task: AITask,
        event_date: Optional[datetime],
        now: datetime
    ) -> float:
        """Calculate dynamic priority score for a task."""
        score = 0.0
        
        # Base priority weight
        score += self.priority_weights.get(
            TaskPriority(task.priority),
            TaskPriority.MEDIUM.value
        )
        
        # Status urgency
        status_value = self.status_urgency.get(TaskStatus(task.status), 1.0)
        score += status_value * 0.3
        
        # Time sensitivity
        if task.due_date:
            days_until_due = (task.due_date - now).days
            
            if days_until_due < 0:
                score += 2.0  # Already overdue
            elif days_until_due <= 3:
                score += 1.5  # Due very soon
            elif days_until_due <= 7:
                score += 1.0  # Due this week
            elif days_until_due <= 14:
                score += 0.5  # Due in two weeks
        
        # Event proximity
        if event_date:
            days_until_event = (event_date - now).days
            task_importance = self._get_event_importance(task)
            score += (30 - days_until_event) * task_importance * 0.02
        
        return score
    
    def _get_priority_factors(
        self,
        task: AITask,
        event_date: Optional[datetime],
        now: datetime
    ) -> List[str]:
        """Get factors that influenced priority calculation."""
        factors = []
        
        if task.priority == "critical":
            factors.append("Marked as critical priority")
        elif task.priority == "high":
            factors.append("Marked as high priority")
        
        if task.due_date:
            days_until_due = (task.due_date - now).days
            if days_until_due < 0:
                factors.append("Task is overdue")
            elif days_until_due <= 7:
                factors.append(f"Due in {days_until_due} days")
        
        if task.status == "in_progress":
            factors.append("Already in progress")
        elif task.status == "todo":
            factors.append("Not yet started")
        
        if task.is_blocked:
            factors.append("Task is blocked")
        
        if task.assignee:
            factors.append(f"Assigned to {task.assignee}")
        else:
            factors.append("Unassigned")
        
        return factors
    
    def _estimate_effort(self, task: AITask) -> float:
        """Estimate effort in days for a task."""
        # Base effort by priority
        effort_map = {
            TaskPriority.CRITICAL: 2.0,
            TaskPriority.HIGH: 1.5,
            TaskPriority.MEDIUM: 1.0,
            TaskPriority.LOW: 0.5,
        }
        
        base_effort = effort_map.get(TaskPriority(task.priority), 1.0)
        
        # Adjust based on description length (rough estimate)
        desc_length = len(task.description or "")
        if desc_length > 200:
            base_effort *= 1.5
        elif desc_length > 100:
            base_effort *= 1.25
        
        return base_effort
    
    def _get_event_importance(self, task: AITask) -> float:
        """Get importance weight based on task category and phase."""
        # Critical categories
        if task.category in ["venue", "speakers"]:
            return 1.0
        # Important categories
        if task.category in ["logistics", "registration"]:
            return 0.8
        # Standard categories
        return 0.5
    
    def _calculate_workflow_health(
        self,
        tasks: List[AITask],
        event_date: Optional[datetime]
    ) -> float:
        """Calculate overall workflow health score (0-100)."""
        if not tasks:
            return 100.0
        
        now = datetime.utcnow()
        score = 100.0
        
        # Penalty for blocked tasks
        blocked = [t for t in tasks if t.is_blocked]
        score -= len(blocked) * 5
        
        # Penalty for overdue tasks
        overdue = [
            t for t in tasks
            if t.due_date and t.due_date < now
            and t.status not in [TaskStatus.DONE.value, TaskStatus.BLOCKED.value]
        ]
        score -= len(overdue) * 3
        
        # Penalty for tasks without assignees
        unassigned = [
            t for t in tasks
            if not t.assignee and t.status != TaskStatus.DONE.value
        ]
        score -= len(unassigned) * 2
        
        # Bonus for good progress
        completed = len([t for t in tasks if t.status == TaskStatus.DONE.value])
        total = len(tasks)
        progress_ratio = completed / total if total > 0 else 0
        
        if progress_ratio > 0.5:
            score += 5
        if progress_ratio > 0.75:
            score += 5
        
        return max(0, min(100, score))
    
    def _generate_summary(
        self,
        insights: List[AIWorkflowInsight],
        health_score: float
    ) -> str:
        """Generate human-readable summary of analysis."""
        
        warnings = [i for i in insights if i.type == "warning"]
        suggestions = [i for i in insights if i.type == "suggestion"]
        tips = [i for i in insights if i.type == "tip"]
        
        if health_score >= 90:
            return "Workflow is healthy and on track. Great progress!"
        elif health_score >= 70:
            if warnings:
                return f"Workflow is stable with {len(warnings)} warning(s) to address."
            return "Workflow is progressing well."
        elif health_score >= 50:
            if warnings:
                return f"Attention needed: {len(warnings)} warning(s) require action."
            return "Workflow has some issues that should be addressed."
        else:
            return f"Critical attention required: {len(warnings)} issue(s) need immediate action."

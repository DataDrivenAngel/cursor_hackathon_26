"""
Kanban router - Task management for event planning.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.connection import get_db
from app.database.schemas import TaskCreate, TaskUpdate, TaskResponse
from app.auth.dependencies import get_current_user, require_admin_or_organizer
from app.models.database_models import User, Task, Event


router = APIRouter()


@router.get("/{event_id}", response_model=List[TaskResponse])
async def get_tasks(
    event_id: int,
    status_filter: str = Query(None, description="Filter by status: todo, in_progress, review, done"),
    db: AsyncSession = Depends(get_db)
):
    """Get all tasks for an event, optionally filtered by status."""
    # Verify event exists
    event_result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    if event_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    query = select(Task).where(Task.event_id == event_id)
    
    if status_filter:
        query = query.where(Task.status == status_filter)
    
    query = query.order_by(Task.created_at)
    result = await db.execute(query)
    tasks = result.scalars().all()
    return tasks


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(require_admin_or_organizer),
    db: AsyncSession = Depends(get_db)
):
    """Create a new task."""
    # Verify event exists
    event_result = await db.execute(
        select(Event).where(Event.id == task_data.event_id)
    )
    if event_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    task = Task(
        event_id=task_data.event_id,
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        assignee_id=task_data.assignee_id,
        due_date=task_data.due_date,
        created_by=current_user.id
    )
    
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    return task


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task_status(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(require_admin_or_organizer),
    db: AsyncSession = Depends(get_db)
):
    """Update a task's status or other fields."""
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    await db.commit()
    await db.refresh(task)
    
    return task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def edit_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(require_admin_or_organizer),
    db: AsyncSession = Depends(get_db)
):
    """Edit a task (full update)."""
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    await db.commit()
    await db.refresh(task)
    
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(require_admin_or_organizer),
    db: AsyncSession = Depends(get_db)
):
    """Delete a task."""
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    await db.delete(task)
    await db.commit()

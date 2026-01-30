"use client";

import { useDroppable } from "@dnd-kit/core";
import { TaskCard } from "./task-card";
import { cn } from "@/lib/utils";
import type { Task, TaskStatus } from "@/lib/types";

interface TaskColumnProps {
  status: TaskStatus;
  tasks: Task[];
  onStatusChange?: (taskId: string, newStatus: TaskStatus) => void;
}

const columnConfig: Record<
  TaskStatus,
  { title: string; color: string; bgClass: string }
> = {
  todo: {
    title: "To Do",
    color: "bg-muted-foreground",
    bgClass: "task-column-todo",
  },
  "in-progress": {
    title: "In Progress",
    color: "bg-info",
    bgClass: "task-column-in-progress",
  },
  review: {
    title: "Review",
    color: "bg-phase-marketing",
    bgClass: "task-column-review",
  },
  done: {
    title: "Done",
    color: "bg-success",
    bgClass: "task-column-done",
  },
};

export function TaskColumn({ status, tasks, onStatusChange }: TaskColumnProps) {
  const { setNodeRef, isOver } = useDroppable({
    id: status,
  });

  const config = columnConfig[status];

  return (
    <div className="flex flex-col h-full min-w-[280px] max-w-[320px]">
      {/* Column Header */}
      <div className="flex items-center justify-between mb-3 px-1">
        <div className="flex items-center gap-2">
          <div className={cn("h-3 w-3 rounded-full", config.color)} />
          <h3 className="font-semibold text-foreground">{config.title}</h3>
          <span className="text-sm text-muted-foreground">({tasks.length})</span>
        </div>
      </div>

      {/* Column Content */}
      <div
        ref={setNodeRef}
        className={cn(
          "flex-1 rounded-lg p-2 transition-colors duration-200 overflow-y-auto",
          config.bgClass,
          isOver && "ring-2 ring-primary ring-offset-2 ring-offset-background"
        )}
      >
        <div className="space-y-2">
          {tasks.map((task, index) => (
            <div
              key={task.id}
              className="animate-slide-up"
              style={{ animationDelay: `${index * 30}ms` }}
            >
              <TaskCard task={task} onStatusChange={onStatusChange} />
            </div>
          ))}

          {tasks.length === 0 && (
            <div className="flex items-center justify-center h-24 text-sm text-muted-foreground">
              No tasks
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

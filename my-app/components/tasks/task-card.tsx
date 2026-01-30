"use client";

import { useDraggable } from "@dnd-kit/core";
import { CSS } from "@dnd-kit/utilities";
import {
  Calendar,
  AlertTriangle,
  User,
  MoreHorizontal,
  Lock,
} from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import type { Task, TaskPriority, TaskCategory } from "@/lib/types";

interface TaskCardProps {
  task: Task;
  onStatusChange?: (taskId: string, newStatus: Task["status"]) => void;
}

const priorityColors: Record<TaskPriority, string> = {
  critical: "bg-priority-critical text-white",
  high: "bg-priority-high text-white",
  medium: "bg-priority-medium text-black",
  low: "bg-priority-low text-white",
};

const categoryColors: Record<TaskCategory, string> = {
  speakers: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  venue: "bg-green-500/20 text-green-400 border-green-500/30",
  marketing: "bg-pink-500/20 text-pink-400 border-pink-500/30",
  sponsors: "bg-amber-500/20 text-amber-400 border-amber-500/30",
  catering: "bg-orange-500/20 text-orange-400 border-orange-500/30",
  logistics: "bg-cyan-500/20 text-cyan-400 border-cyan-500/30",
  registration: "bg-violet-500/20 text-violet-400 border-violet-500/30",
  content: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
};

export function TaskCard({ task, onStatusChange }: TaskCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    isDragging,
  } = useDraggable({
    id: task.id,
    disabled: task.isBlocked,
    data: task,
  });

  const style = transform
    ? {
        transform: CSS.Translate.toString(transform),
      }
    : undefined;

  const dueDate = new Date(task.dueDate);
  const isOverdue = dueDate < new Date() && task.status !== "done";
  const daysUntilDue = Math.ceil(
    (dueDate.getTime() - Date.now()) / (1000 * 60 * 60 * 24)
  );

  return (
    <TooltipProvider>
      <Card
        ref={setNodeRef}
        style={style}
        {...attributes}
        {...listeners}
        className={cn(
          "cursor-grab active:cursor-grabbing border-border bg-card transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg",
          isDragging && "opacity-50 shadow-xl z-50 rotate-2",
          task.isBlocked && "task-blocked cursor-not-allowed"
        )}
      >
        <CardHeader className="p-3 pb-2">
          <div className="flex items-start justify-between gap-2">
            <div className="flex flex-wrap gap-1.5">
              <Badge className={cn("text-xs capitalize", priorityColors[task.priority])}>
                {task.priority}
              </Badge>
              <Badge
                variant="outline"
                className={cn("text-xs capitalize", categoryColors[task.category])}
              >
                {task.category}
              </Badge>
            </div>

            {task.isBlocked ? (
              <Tooltip>
                <TooltipTrigger asChild>
                  <div className="flex items-center gap-1 text-destructive">
                    <Lock className="h-4 w-4" />
                  </div>
                </TooltipTrigger>
                <TooltipContent className="max-w-xs bg-popover border-border text-popover-foreground">
                  <p className="font-medium">Blocked</p>
                  <p className="text-sm text-muted-foreground">
                    {task.blockingReason}
                  </p>
                </TooltipContent>
              </Tooltip>
            ) : (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 text-muted-foreground hover:bg-secondary"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <MoreHorizontal className="h-4 w-4" />
                    <span className="sr-only">Task options</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="bg-popover border-border">
                  <DropdownMenuItem
                    className="text-popover-foreground hover:bg-secondary cursor-pointer"
                    onClick={() => onStatusChange?.(task.id, "todo")}
                  >
                    Move to To Do
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    className="text-popover-foreground hover:bg-secondary cursor-pointer"
                    onClick={() => onStatusChange?.(task.id, "in-progress")}
                  >
                    Move to In Progress
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    className="text-popover-foreground hover:bg-secondary cursor-pointer"
                    onClick={() => onStatusChange?.(task.id, "review")}
                  >
                    Move to Review
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    className="text-popover-foreground hover:bg-secondary cursor-pointer"
                    onClick={() => onStatusChange?.(task.id, "done")}
                  >
                    Move to Done
                  </DropdownMenuItem>
                  <DropdownMenuSeparator className="bg-border" />
                  <DropdownMenuItem className="text-popover-foreground hover:bg-secondary cursor-pointer">
                    Edit Task
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </div>
        </CardHeader>

        <CardContent className="p-3 pt-0 space-y-2">
          <div>
            <h4 className="font-medium text-card-foreground line-clamp-2">
              {task.title}
            </h4>
            {task.description && (
              <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
                {task.description}
              </p>
            )}
          </div>

          {/* Task meta */}
          <div className="flex items-center justify-between text-xs">
            <div
              className={cn(
                "flex items-center gap-1",
                isOverdue ? "text-destructive" : "text-muted-foreground"
              )}
            >
              {isOverdue && <AlertTriangle className="h-3 w-3" />}
              <Calendar className="h-3 w-3" />
              <span>
                {isOverdue
                  ? "Overdue"
                  : daysUntilDue === 0
                    ? "Due today"
                    : daysUntilDue === 1
                      ? "Due tomorrow"
                      : `${daysUntilDue} days`}
              </span>
            </div>

            {task.assignee && (
              <div className="flex items-center gap-1 text-muted-foreground">
                <User className="h-3 w-3" />
                <span className="truncate max-w-[80px]">{task.assignee}</span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </TooltipProvider>
  );
}

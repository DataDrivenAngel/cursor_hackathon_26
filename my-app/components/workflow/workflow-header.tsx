"use client";

import { ArrowLeft, MoreHorizontal, ExternalLink } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ProgressCircle } from "./progress-circle";
import type { Event, WorkflowProgress } from "@/lib/types";
import { cn } from "@/lib/utils";

interface WorkflowHeaderProps {
  event: Event;
  progress: WorkflowProgress;
}

const statusColors = {
  planning: "bg-info/20 text-info border-info/30",
  active: "bg-success/20 text-success border-success/30",
  completed: "bg-muted text-muted-foreground border-muted",
  cancelled: "bg-destructive/20 text-destructive border-destructive/30",
};

export function WorkflowHeader({ event, progress }: WorkflowHeaderProps) {
  const eventDate = new Date(event.date);

  return (
    <div className="border-b border-border bg-card">
      <div className="px-6 py-4">
        {/* Back link */}
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors mb-4"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Dashboard
        </Link>

        <div className="flex items-start justify-between gap-6">
          {/* Event Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold text-card-foreground truncate">
                {event.title}
              </h1>
              <Badge
                variant="outline"
                className={cn("shrink-0 capitalize", statusColors[event.status])}
              >
                {event.status}
              </Badge>
            </div>
            <p className="text-muted-foreground mb-4 line-clamp-2">
              {event.description}
            </p>

            {/* Event meta */}
            <div className="flex flex-wrap items-center gap-4 text-sm">
              <div className="flex items-center gap-1.5">
                <span className="text-muted-foreground">Date:</span>
                <span className="text-card-foreground font-medium">
                  {eventDate.toLocaleDateString("en-US", {
                    weekday: "long",
                    month: "long",
                    day: "numeric",
                    year: "numeric",
                  })}
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="text-muted-foreground">Format:</span>
                <span className="text-card-foreground font-medium capitalize">
                  {event.format}
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="text-muted-foreground">Topic:</span>
                <span className="text-card-foreground font-medium">
                  {event.topic}
                </span>
              </div>
            </div>
          </div>

          {/* Progress & Actions */}
          <div className="flex items-center gap-6">
            {/* Progress Circle */}
            <div className="text-center">
              <ProgressCircle progress={progress.overallProgress} size={100} />
            </div>

            {/* Quick Stats */}
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between gap-4">
                <span className="text-muted-foreground">Total Tasks</span>
                <span className="font-medium text-card-foreground">
                  {progress.totalTasks}
                </span>
              </div>
              <div className="flex items-center justify-between gap-4">
                <span className="text-muted-foreground">Completed</span>
                <span className="font-medium text-success">
                  {progress.completedTasks}
                </span>
              </div>
              <div className="flex items-center justify-between gap-4">
                <span className="text-muted-foreground">In Progress</span>
                <span className="font-medium text-info">
                  {progress.inProgressTasks}
                </span>
              </div>
              {progress.blockedTasks > 0 && (
                <div className="flex items-center justify-between gap-4">
                  <span className="text-muted-foreground">Blocked</span>
                  <span className="font-medium text-destructive">
                    {progress.blockedTasks}
                  </span>
                </div>
              )}
            </div>

            {/* Actions Menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="text-muted-foreground hover:bg-secondary"
                >
                  <MoreHorizontal className="h-5 w-5" />
                  <span className="sr-only">Event actions</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="bg-popover border-border">
                <DropdownMenuItem className="text-popover-foreground hover:bg-secondary cursor-pointer">
                  <ExternalLink className="h-4 w-4 mr-2" />
                  View Event Page
                </DropdownMenuItem>
                <DropdownMenuItem className="text-popover-foreground hover:bg-secondary cursor-pointer">
                  Export Tasks
                </DropdownMenuItem>
                <DropdownMenuSeparator className="bg-border" />
                <DropdownMenuItem className="text-destructive hover:bg-destructive/10 cursor-pointer">
                  Cancel Event
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>
    </div>
  );
}

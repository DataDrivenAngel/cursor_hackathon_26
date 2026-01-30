"use client";

import { Check, Clock, AlertTriangle, Star } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Milestone } from "@/lib/types";

interface MilestoneTimelineProps {
  milestones: Milestone[];
  eventDate: string;
}

export function MilestoneTimeline({
  milestones,
  eventDate,
}: MilestoneTimelineProps) {
  const sortedMilestones = [...milestones].sort(
    (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
  );

  const today = new Date();
  const event = new Date(eventDate);
  const start = new Date(
    Math.min(
      ...milestones.map((m) => new Date(m.date).getTime()),
      today.getTime()
    )
  );

  const totalDays = Math.ceil(
    (event.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)
  );

  const getPosition = (date: string) => {
    const d = new Date(date);
    const daysSinceStart = Math.ceil(
      (d.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)
    );
    return Math.min(Math.max((daysSinceStart / totalDays) * 100, 0), 100);
  };

  const todayPosition = getPosition(today.toISOString());

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-foreground">
          Milestone Timeline
        </h2>
        <span className="text-sm text-muted-foreground">
          {milestones.filter((m) => m.isCompleted).length}/{milestones.length}{" "}
          milestones completed
        </span>
      </div>

      {/* Timeline Container */}
      <div className="relative">
        {/* Timeline Bar */}
        <div className="relative h-2 bg-secondary rounded-full overflow-hidden">
          {/* Progress */}
          <div
            className="absolute h-full bg-primary transition-all duration-500"
            style={{ width: `${todayPosition}%` }}
          />
          {/* Critical Path Line */}
          <div className="absolute top-1/2 left-0 right-0 h-0.5 -translate-y-1/2">
            {sortedMilestones
              .filter((m) => m.isCriticalPath)
              .map((milestone, index, arr) => {
                if (index === 0) return null;
                const prevMilestone = arr[index - 1];
                const startPos = getPosition(prevMilestone.date);
                const endPos = getPosition(milestone.date);
                return (
                  <div
                    key={`line-${milestone.id}`}
                    className="absolute h-full bg-warning/50"
                    style={{
                      left: `${startPos}%`,
                      width: `${endPos - startPos}%`,
                    }}
                  />
                );
              })}
          </div>
        </div>

        {/* Today Marker */}
        <div
          className="absolute top-0 -translate-x-1/2 flex flex-col items-center"
          style={{ left: `${todayPosition}%` }}
        >
          <div className="h-6 w-0.5 bg-primary" />
          <span className="text-xs text-primary font-medium mt-1">Today</span>
        </div>

        {/* Milestones */}
        <div className="relative mt-8 pt-2">
          {sortedMilestones.map((milestone, index) => {
            const position = getPosition(milestone.date);
            const isLeft = position < 50;
            const milestoneDate = new Date(milestone.date);

            return (
              <div
                key={milestone.id}
                className="absolute -translate-x-1/2"
                style={{
                  left: `${position}%`,
                  top: `${(index % 2) * 80}px`,
                }}
              >
                {/* Connector Line */}
                <div
                  className={cn(
                    "absolute left-1/2 -translate-x-1/2 w-0.5 -top-2",
                    milestone.isCompleted
                      ? "bg-success"
                      : milestone.isOverdue
                        ? "bg-destructive"
                        : "bg-border",
                    index % 2 === 0 ? "h-2" : "h-[82px]"
                  )}
                />

                {/* Milestone Node */}
                <div
                  className={cn(
                    "relative flex items-center justify-center h-8 w-8 rounded-full border-2 transition-all",
                    milestone.isCompleted
                      ? "bg-success/20 border-success text-success"
                      : milestone.isOverdue
                        ? "bg-destructive/20 border-destructive text-destructive animate-pulse"
                        : "bg-card border-border text-muted-foreground",
                    milestone.isCriticalPath && !milestone.isCompleted && "ring-2 ring-warning ring-offset-2 ring-offset-background"
                  )}
                >
                  {milestone.isCompleted ? (
                    <Check className="h-4 w-4" />
                  ) : milestone.isOverdue ? (
                    <AlertTriangle className="h-4 w-4" />
                  ) : milestone.isCriticalPath ? (
                    <Star className="h-4 w-4 text-warning" />
                  ) : (
                    <Clock className="h-4 w-4" />
                  )}
                </div>

                {/* Milestone Label */}
                <div
                  className={cn(
                    "absolute whitespace-nowrap text-center",
                    index % 2 === 0 ? "top-10" : "-top-16",
                    "left-1/2 -translate-x-1/2"
                  )}
                >
                  <p
                    className={cn(
                      "text-sm font-medium",
                      milestone.isCompleted
                        ? "text-success"
                        : milestone.isOverdue
                          ? "text-destructive"
                          : "text-foreground"
                    )}
                  >
                    {milestone.title}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {milestoneDate.toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                    })}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Spacer for milestone labels */}
        <div className="h-40" />
      </div>

      {/* Legend */}
      <div className="flex flex-wrap items-center gap-6 text-sm text-muted-foreground pt-4 border-t border-border">
        <div className="flex items-center gap-2">
          <div className="h-4 w-4 rounded-full bg-success/20 border-2 border-success flex items-center justify-center">
            <Check className="h-2.5 w-2.5 text-success" />
          </div>
          <span>Completed</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-4 w-4 rounded-full bg-card border-2 border-border flex items-center justify-center">
            <Clock className="h-2.5 w-2.5 text-muted-foreground" />
          </div>
          <span>Upcoming</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-4 w-4 rounded-full bg-destructive/20 border-2 border-destructive flex items-center justify-center">
            <AlertTriangle className="h-2.5 w-2.5 text-destructive" />
          </div>
          <span>Overdue</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-4 w-4 rounded-full bg-card border-2 border-border ring-2 ring-warning ring-offset-1 ring-offset-background flex items-center justify-center">
            <Star className="h-2.5 w-2.5 text-warning" />
          </div>
          <span>Critical Path</span>
        </div>
      </div>
    </div>
  );
}

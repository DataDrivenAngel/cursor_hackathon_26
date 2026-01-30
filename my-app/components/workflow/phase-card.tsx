"use client";

import {
  Lightbulb,
  Truck,
  Megaphone,
  ClipboardList,
  Play,
  CheckCircle,
  AlertTriangle,
  Check,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { PhaseProgress, WorkflowPhase } from "@/lib/types";

interface PhaseCardProps {
  phase: PhaseProgress;
  isCompact?: boolean;
}

const phaseIcons: Record<WorkflowPhase, typeof Lightbulb> = {
  ideation: Lightbulb,
  logistics: Truck,
  marketing: Megaphone,
  preparation: ClipboardList,
  execution: Play,
  review: CheckCircle,
};

const phaseColors: Record<WorkflowPhase, string> = {
  ideation: "bg-phase-ideation",
  logistics: "bg-phase-logistics",
  marketing: "bg-phase-marketing",
  preparation: "bg-phase-preparation",
  execution: "bg-phase-execution",
  review: "bg-phase-review",
};

const phaseTextColors: Record<WorkflowPhase, string> = {
  ideation: "text-phase-ideation",
  logistics: "text-phase-logistics",
  marketing: "text-phase-marketing",
  preparation: "text-phase-preparation",
  execution: "text-phase-execution",
  review: "text-phase-review",
};

export function PhaseCard({ phase, isCompact = false }: PhaseCardProps) {
  const Icon = phaseIcons[phase.phase];

  return (
    <Card
      className={cn(
        "relative border-border bg-card transition-all duration-300",
        phase.isActive && "ring-2 ring-primary/50 animate-pulse-glow",
        phase.isCompleted && "opacity-75"
      )}
    >
      {/* Completed overlay */}
      {phase.isCompleted && (
        <div className="absolute inset-0 flex items-center justify-center bg-card/80 rounded-lg z-10">
          <div className="flex items-center gap-2 text-success">
            <Check className="h-5 w-5" />
            <span className="font-medium">Completed</span>
          </div>
        </div>
      )}

      <CardContent className={cn("p-4", isCompact && "p-3")}>
        <div className="flex items-start gap-3">
          {/* Icon */}
          <div
            className={cn(
              "flex items-center justify-center rounded-lg p-2",
              phaseColors[phase.phase],
              "bg-opacity-20"
            )}
          >
            <Icon
              className={cn(
                "h-5 w-5",
                phaseTextColors[phase.phase],
                phase.isActive && "animate-pulse"
              )}
            />
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2 mb-2">
              <h4 className="font-medium text-card-foreground truncate">
                {phase.name}
              </h4>
              {phase.hasBlockedTasks && (
                <Badge
                  variant="outline"
                  className="shrink-0 border-destructive/50 text-destructive bg-destructive/10"
                >
                  <AlertTriangle className="h-3 w-3 mr-1" />
                  Blocked
                </Badge>
              )}
            </div>

            {/* Progress bar */}
            <div className="space-y-1">
              <Progress
                value={phase.progress}
                className={cn(
                  "h-2 bg-secondary",
                  phase.isCompleted && "opacity-50"
                )}
              />
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>{phase.progress}%</span>
                <span>
                  {phase.completedTasks}/{phase.totalTasks} tasks
                </span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

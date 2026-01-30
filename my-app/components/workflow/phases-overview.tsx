"use client";

import { PhaseCard } from "./phase-card";
import type { PhaseProgress } from "@/lib/types";

interface PhasesOverviewProps {
  phases: PhaseProgress[];
}

export function PhasesOverview({ phases }: PhasesOverviewProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-foreground">
          Workflow Phases
        </h2>
        <span className="text-sm text-muted-foreground">
          {phases.filter((p) => p.isCompleted).length}/{phases.length} phases
          completed
        </span>
      </div>

      {/* Phase Progress Bar */}
      <div className="flex h-3 rounded-full overflow-hidden bg-secondary">
        {phases.map((phase, index) => (
          <div
            key={phase.phase}
            className="relative h-full transition-all duration-500"
            style={{
              width: `${phase.weight}%`,
              backgroundColor:
                phase.progress > 0
                  ? `var(--color-phase-${phase.phase})`
                  : undefined,
              opacity: phase.progress / 100,
            }}
          >
            {/* Phase separator */}
            {index < phases.length - 1 && (
              <div className="absolute right-0 top-0 h-full w-0.5 bg-background" />
            )}
          </div>
        ))}
      </div>

      {/* Phase Labels */}
      <div className="flex">
        {phases.map((phase) => (
          <div
            key={phase.phase}
            className="text-center"
            style={{ width: `${phase.weight}%` }}
          >
            <span className="text-xs text-muted-foreground">{phase.name}</span>
          </div>
        ))}
      </div>

      {/* Phase Cards Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {phases.map((phase, index) => (
          <div
            key={phase.phase}
            className="animate-slide-up"
            style={{ animationDelay: `${index * 50}ms` }}
          >
            <PhaseCard phase={phase} />
          </div>
        ))}
      </div>
    </div>
  );
}

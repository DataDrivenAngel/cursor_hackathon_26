"use client";

import {
  CalendarDays,
  CheckCircle2,
  Clock,
  AlertTriangle,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface StatsData {
  totalEvents: number;
  activeEvents: number;
  completedTasks: number;
  pendingTasks: number;
}

interface StatsCardsProps {
  stats: StatsData;
}

const statsConfig = [
  {
    key: "totalEvents" as const,
    label: "Total Events",
    icon: CalendarDays,
    color: "text-info",
    bgColor: "bg-info/10",
  },
  {
    key: "activeEvents" as const,
    label: "Active Events",
    icon: Clock,
    color: "text-primary",
    bgColor: "bg-primary/10",
  },
  {
    key: "completedTasks" as const,
    label: "Completed Tasks",
    icon: CheckCircle2,
    color: "text-success",
    bgColor: "bg-success/10",
  },
  {
    key: "pendingTasks" as const,
    label: "Pending Tasks",
    icon: AlertTriangle,
    color: "text-warning",
    bgColor: "bg-warning/10",
  },
];

export function StatsCards({ stats }: StatsCardsProps) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {statsConfig.map((stat, index) => (
        <Card
          key={stat.key}
          className="card-hover border-border bg-card animate-slide-up"
          style={{ animationDelay: `${index * 50}ms` }}
        >
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">{stat.label}</p>
                <p className="text-3xl font-bold text-card-foreground">
                  {stats[stat.key]}
                </p>
              </div>
              <div className={cn("rounded-lg p-3", stat.bgColor)}>
                <stat.icon className={cn("h-6 w-6", stat.color)} />
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

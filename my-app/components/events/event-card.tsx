"use client";

import { Calendar, MapPin, Users, Monitor, ArrowRight } from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import type { Event } from "@/lib/types";
import Link from "next/link";

interface EventCardProps {
  event: Event;
}

const formatIcons = {
  "in-person": MapPin,
  virtual: Monitor,
  hybrid: Users,
};

const statusColors = {
  planning: "bg-info/20 text-info border-info/30",
  active: "bg-success/20 text-success border-success/30",
  completed: "bg-muted text-muted-foreground border-muted",
  cancelled: "bg-destructive/20 text-destructive border-destructive/30",
};

export function EventCard({ event }: EventCardProps) {
  const FormatIcon = formatIcons[event.format];
  const eventDate = new Date(event.date);
  const daysUntil = Math.ceil(
    (eventDate.getTime() - Date.now()) / (1000 * 60 * 60 * 24)
  );

  return (
    <Link href={`/events/${event.id}`}>
      <Card className="card-hover group cursor-pointer border-border bg-card overflow-hidden">
        {/* Progress indicator at top */}
        <div className="h-1 w-full bg-secondary">
          <div
            className="h-full bg-primary transition-all duration-500"
            style={{ width: `${event.progress}%` }}
          />
        </div>

        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-2">
            <div className="space-y-1 flex-1 min-w-0">
              <h3 className="font-semibold text-card-foreground group-hover:text-primary transition-colors line-clamp-1">
                {event.title}
              </h3>
              <p className="text-sm text-muted-foreground line-clamp-2">
                {event.description}
              </p>
            </div>
            <Badge
              variant="outline"
              className={cn("shrink-0 capitalize", statusColors[event.status])}
            >
              {event.status}
            </Badge>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Event details */}
          <div className="flex flex-wrap gap-3 text-sm text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <Calendar className="h-4 w-4" />
              <span>
                {eventDate.toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                  year: "numeric",
                })}
              </span>
            </div>
            <div className="flex items-center gap-1.5">
              <FormatIcon className="h-4 w-4" />
              <span className="capitalize">{event.format}</span>
            </div>
          </div>

          {/* Progress section */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Progress</span>
              <span className="font-medium text-card-foreground">
                {event.progress}%
              </span>
            </div>
            <Progress value={event.progress} className="h-2 bg-secondary" />
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between pt-2 border-t border-border">
            <div className="text-sm">
              {daysUntil > 0 ? (
                <span className="text-muted-foreground">
                  <span className="font-medium text-card-foreground">
                    {daysUntil}
                  </span>{" "}
                  days until event
                </span>
              ) : daysUntil === 0 ? (
                <span className="font-medium text-primary">Today</span>
              ) : (
                <span className="text-muted-foreground">Event passed</span>
              )}
            </div>
            <div className="flex items-center gap-1 text-sm text-primary opacity-0 group-hover:opacity-100 transition-opacity">
              <span>View details</span>
              <ArrowRight className="h-4 w-4" />
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

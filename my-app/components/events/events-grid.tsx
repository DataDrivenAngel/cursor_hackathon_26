"use client";

import { EventCard } from "./event-card";
import type { Event } from "@/lib/types";

interface EventsGridProps {
  events: Event[];
  title?: string;
}

export function EventsGrid({ events, title }: EventsGridProps) {
  if (events.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border bg-card/50 p-12 text-center">
        <div className="rounded-full bg-secondary p-4">
          <svg
            className="h-8 w-8 text-muted-foreground"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
        </div>
        <h3 className="mt-4 text-lg font-medium text-card-foreground">
          No events yet
        </h3>
        <p className="mt-2 text-sm text-muted-foreground">
          Get started by creating your first event
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {title && (
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-foreground">{title}</h2>
          <span className="text-sm text-muted-foreground">
            {events.length} event{events.length !== 1 ? "s" : ""}
          </span>
        </div>
      )}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {events.map((event, index) => (
          <div
            key={event.id}
            className="animate-slide-up"
            style={{ animationDelay: `${index * 50}ms` }}
          >
            <EventCard event={event} />
          </div>
        ))}
      </div>
    </div>
  );
}

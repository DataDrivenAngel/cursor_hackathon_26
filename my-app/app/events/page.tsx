"use client";

import { useState, useEffect } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { EventsGrid } from "@/components/events/events-grid";
import { EventWizard } from "@/components/events/event-wizard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Search, Filter, SlidersHorizontal, Loader2, RefreshCw } from "lucide-react";
import { mockNotifications } from "@/lib/mock-data";
import { getEvents } from "@/lib/api";
import type { Event } from "@/lib/types";
import { toast } from "sonner";

export default function EventsPage() {
  const [isWizardOpen, setIsWizardOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [formatFilter, setFormatFilter] = useState<string>("all");
  const [events, setEvents] = useState<Event[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchEvents = async () => {
    setIsLoading(true);
    try {
      const eventsData = await getEvents().catch(() => []);
      setEvents(eventsData);
    } catch (error) {
      console.error("Error fetching events:", error);
      toast.error("Failed to load events from backend");
      setEvents([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  // Filter events based on search and filters
  const filteredEvents = events.filter((event) => {
    const matchesSearch =
      event.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      event.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (event.topic && event.topic.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesStatus =
      statusFilter === "all" || event.status === statusFilter;
    const matchesFormat =
      formatFilter === "all" || event.format === formatFilter;

    return matchesSearch && matchesStatus && matchesFormat;
  });

  return (
    <div className="flex h-screen bg-background">
      <Sidebar onCreateEvent={() => setIsWizardOpen(true)} />

      <div className="flex flex-1 flex-col overflow-hidden">
        <Header
          title="Events"
          subtitle="Manage and track all your events"
          notifications={mockNotifications}
        />

        <main className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Filters */}
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                type="search"
                placeholder="Search events..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 bg-input border-border text-foreground placeholder:text-muted-foreground"
              />
            </div>

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <Filter className="h-4 w-4 text-muted-foreground" />
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-[140px] bg-input border-border text-foreground">
                    <SelectValue placeholder="Status" />
                  </SelectTrigger>
                  <SelectContent className="bg-popover border-border">
                    <SelectItem
                      value="all"
                      className="text-popover-foreground hover:bg-secondary"
                    >
                      All Status
                    </SelectItem>
                    <SelectItem
                      value="planning"
                      className="text-popover-foreground hover:bg-secondary"
                    >
                      Planning
                    </SelectItem>
                    <SelectItem
                      value="active"
                      className="text-popover-foreground hover:bg-secondary"
                    >
                      Active
                    </SelectItem>
                    <SelectItem
                      value="completed"
                      className="text-popover-foreground hover:bg-secondary"
                    >
                      Completed
                    </SelectItem>
                    <SelectItem
                      value="cancelled"
                      className="text-popover-foreground hover:bg-secondary"
                    >
                      Cancelled
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center gap-2">
                <SlidersHorizontal className="h-4 w-4 text-muted-foreground" />
                <Select value={formatFilter} onValueChange={setFormatFilter}>
                  <SelectTrigger className="w-[140px] bg-input border-border text-foreground">
                    <SelectValue placeholder="Format" />
                  </SelectTrigger>
                  <SelectContent className="bg-popover border-border">
                    <SelectItem
                      value="all"
                      className="text-popover-foreground hover:bg-secondary"
                    >
                      All Formats
                    </SelectItem>
                    <SelectItem
                      value="in-person"
                      className="text-popover-foreground hover:bg-secondary"
                    >
                      In-Person
                    </SelectItem>
                    <SelectItem
                      value="virtual"
                      className="text-popover-foreground hover:bg-secondary"
                    >
                      Virtual
                    </SelectItem>
                    <SelectItem
                      value="hybrid"
                      className="text-popover-foreground hover:bg-secondary"
                    >
                      Hybrid
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button
                onClick={() => setIsWizardOpen(true)}
                className="bg-primary text-primary-foreground hover:bg-primary/90"
              >
                Create Event
              </Button>
            </div>
          </div>

          {/* Events Grid */}
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : filteredEvents.length > 0 ? (
            <EventsGrid
              events={filteredEvents}
              title={`${filteredEvents.length} Event${filteredEvents.length !== 1 ? "s" : ""}`}
            />
          ) : (
            <div className="text-center py-12 text-muted-foreground">
              <p>No events found matching your criteria.</p>
              <Button
                onClick={() => setIsWizardOpen(true)}
                className="mt-4"
              >
                Create New Event
              </Button>
            </div>
          )}
        </main>
      </div>

      <EventWizard
        isOpen={isWizardOpen}
        onClose={() => setIsWizardOpen(false)}
        onSubmit={async () => {
          await fetchEvents();
        }}
      />
    </div>
  );
}

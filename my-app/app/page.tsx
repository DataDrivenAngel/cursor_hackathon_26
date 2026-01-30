"use client";

import { useState, useEffect } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { StatsCards } from "@/components/dashboard/stats-cards";
import { EventsGrid } from "@/components/events/events-grid";
import { EventWizard } from "@/components/events/event-wizard";
import { mockNotifications, mockTasks } from "@/lib/mock-data";
import { getEvents, checkHealth } from "@/lib/api";
import type { Event } from "@/lib/types";
import { Loader2, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

export default function DashboardPage() {
  const [isWizardOpen, setIsWizardOpen] = useState(false);
  const [events, setEvents] = useState<Event[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isBackendHealthy, setIsBackendHealthy] = useState(false);

  // Calculate stats from real data
  const stats = {
    totalEvents: events.length,
    activeEvents: events.filter((e) => e.status === "active" || e.status === "planning").length,
    completedTasks: mockTasks.filter((t) => t.status === "done").length,
    pendingTasks: mockTasks.filter((t) => t.status !== "done").length,
  };

  // Sort events by date
  const upcomingEvents = [...events]
    .filter((e) => new Date(e.date) >= new Date())
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

  const fetchEvents = async () => {
    setIsLoading(true);
    try {
      const [eventsData, healthData] = await Promise.all([
        getEvents().catch(() => []),
        checkHealth().catch(() => ({ status: "unhealthy" })),
      ]);
      
      setEvents(eventsData);
      setIsBackendHealthy(healthData.status === "healthy");
      
      if (eventsData.length === 0) {
        toast.info("No events found. Create your first event to get started!");
      }
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

  return (
    <div className="flex h-screen bg-background">
      <Sidebar onCreateEvent={() => setIsWizardOpen(true)} />
      
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header
          title="Dashboard"
          subtitle="Welcome back! Here's an overview of your events."
          notifications={mockNotifications}
        />
        
        <main className="flex-1 overflow-y-auto p-6 space-y-8">
          {/* Backend Status & Refresh */}
          <div className="flex items-center justify-between">
            {!isBackendHealthy && (
              <div className="flex items-center gap-2 text-sm text-amber-600 dark:text-amber-400">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
                </span>
                Backend server is not responding
              </div>
            )}
            <div className="flex-1" />
            <Button
              variant="outline"
              size="sm"
              onClick={fetchEvents}
              disabled={isLoading}
              className="gap-2"
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
              Refresh
            </Button>
          </div>

          {/* Stats Overview */}
          <section>
            <h2 className="text-lg font-semibold text-foreground mb-4">
              Overview
            </h2>
            <StatsCards stats={stats} />
          </section>

          {/* Upcoming Events */}
          <section>
            <h2 className="text-lg font-semibold text-foreground mb-4">
              Upcoming Events
            </h2>
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              </div>
            ) : upcomingEvents.length > 0 ? (
              <EventsGrid events={upcomingEvents} title="Upcoming Events" />
            ) : (
              <div className="text-center py-12 text-muted-foreground">
                <p>No upcoming events. Create your first event!</p>
                <Button
                  onClick={() => setIsWizardOpen(true)}
                  className="mt-4"
                >
                  Create Event
                </Button>
              </div>
            )}
          </section>
        </main>
      </div>

      {/* Event Creation Wizard */}
      <EventWizard
        isOpen={isWizardOpen}
        onClose={() => setIsWizardOpen(false)}
        onSubmit={async (data) => {
          await getEvents();
          await fetchEvents();
        }}
      />
    </div>
  );
}

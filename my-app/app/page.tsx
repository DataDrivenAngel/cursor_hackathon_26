"use client";

import { useState } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { StatsCards } from "@/components/dashboard/stats-cards";
import { EventsGrid } from "@/components/events/events-grid";
import { EventWizard } from "@/components/events/event-wizard";
import { mockEvents, mockNotifications, mockTasks } from "@/lib/mock-data";

export default function DashboardPage() {
  const [isWizardOpen, setIsWizardOpen] = useState(false);

  // Calculate stats from mock data
  const stats = {
    totalEvents: mockEvents.length,
    activeEvents: mockEvents.filter((e) => e.status === "active" || e.status === "planning").length,
    completedTasks: mockTasks.filter((t) => t.status === "done").length,
    pendingTasks: mockTasks.filter((t) => t.status !== "done").length,
  };

  // Sort events by date
  const upcomingEvents = [...mockEvents]
    .filter((e) => new Date(e.date) >= new Date())
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

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
          {/* Stats Overview */}
          <section>
            <h2 className="text-lg font-semibold text-foreground mb-4">
              Overview
            </h2>
            <StatsCards stats={stats} />
          </section>

          {/* Upcoming Events */}
          <section>
            <EventsGrid events={upcomingEvents} title="Upcoming Events" />
          </section>
        </main>
      </div>

      {/* Event Creation Wizard */}
      <EventWizard
        isOpen={isWizardOpen}
        onClose={() => setIsWizardOpen(false)}
      />
    </div>
  );
}

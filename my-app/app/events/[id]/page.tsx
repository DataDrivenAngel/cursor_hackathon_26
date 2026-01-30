"use client";

import { use } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { WorkflowHeader } from "@/components/workflow/workflow-header";
import { PhasesOverview } from "@/components/workflow/phases-overview";
import { TaskBoard } from "@/components/tasks/task-board";
import { MilestoneTimeline } from "@/components/workflow/milestone-timeline";
import { EventWizard } from "@/components/events/event-wizard";
import {
  mockEvents,
  mockTasks,
  mockWorkflowProgress,
  mockMilestones,
} from "@/lib/mock-data";
import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function EventDetailPage({ params }: PageProps) {
  const { id } = use(params);
  const [isWizardOpen, setIsWizardOpen] = useState(false);

  // Find event from mock data
  const event = mockEvents.find((e) => e.id === id) || mockEvents[0];
  const tasks = mockTasks.filter((t) => t.eventId === event.id);
  const progress = { ...mockWorkflowProgress, eventId: event.id };
  const milestones = mockMilestones.filter((m) => m.eventId === event.id);

  return (
    <div className="flex h-screen bg-background">
      <Sidebar onCreateEvent={() => setIsWizardOpen(true)} />

      <div className="flex flex-1 flex-col overflow-hidden">
        <WorkflowHeader event={event} progress={progress} />

        <main className="flex-1 overflow-y-auto p-6 space-y-8">
          <Tabs defaultValue="board" className="space-y-6">
            <TabsList className="bg-secondary border border-border">
              <TabsTrigger
                value="board"
                className="data-[state=active]:bg-card data-[state=active]:text-foreground text-muted-foreground"
              >
                Task Board
              </TabsTrigger>
              <TabsTrigger
                value="phases"
                className="data-[state=active]:bg-card data-[state=active]:text-foreground text-muted-foreground"
              >
                Phases
              </TabsTrigger>
              <TabsTrigger
                value="timeline"
                className="data-[state=active]:bg-card data-[state=active]:text-foreground text-muted-foreground"
              >
                Timeline
              </TabsTrigger>
            </TabsList>

            <TabsContent value="board" className="mt-0">
              <TaskBoard initialTasks={tasks} />
            </TabsContent>

            <TabsContent value="phases" className="mt-0">
              <PhasesOverview phases={progress.phases} />
            </TabsContent>

            <TabsContent value="timeline" className="mt-0">
              <MilestoneTimeline milestones={milestones} eventDate={event.date} />
            </TabsContent>
          </Tabs>
        </main>
      </div>

      <EventWizard
        isOpen={isWizardOpen}
        onClose={() => setIsWizardOpen(false)}
      />
    </div>
  );
}

"use client";

import { use } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { WorkflowHeader } from "@/components/workflow/workflow-header";
import { PhasesOverview } from "@/components/workflow/phases-overview";
import { TaskBoard } from "@/components/tasks/task-board";
import { MilestoneTimeline } from "@/components/workflow/milestone-timeline";
import { AIWorkflowPanel } from "@/components/workflow/ai-workflow-panel";
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
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Content */}
            <div className="lg:col-span-2 space-y-6">
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
                  <TabsTrigger
                    value="ai"
                    className="data-[state=active]:bg-card data-[state=active]:text-foreground text-muted-foreground"
                  >
                    AI Insights
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

                <TabsContent value="ai" className="mt-0">
                  <div className="space-y-6">
                    <div className="bg-gradient-to-r from-primary/10 via-purple-500/5 to-primary/10 rounded-xl p-6 border border-primary/20">
                      <div className="flex items-center gap-3 mb-4">
                        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/20">
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            className="h-6 w-6 text-primary"
                          >
                            <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2z" />
                            <path d="M12 16v-4" />
                            <path d="M12 8h.01" />
                          </svg>
                        </div>
                        <div>
                          <h2 className="text-xl font-semibold text-foreground">
                            AI-Powered Workflow Assistant
                          </h2>
                          <p className="text-sm text-muted-foreground">
                            Get intelligent insights, priority recommendations, and timeline predictions for your event planning
                          </p>
                        </div>
                      </div>
                      <div className="grid gap-4 sm:grid-cols-3">
                        <div className="flex items-center gap-2 p-3 rounded-lg bg-card/50">
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            className="h-5 w-5 text-primary"
                          >
                            <path d="M12 2v4" />
                            <path d="M12 18v4" />
                            <path d="M4.93 4.93l2.83 2.83" />
                            <path d="M16.24 16.24l2.83 2.83" />
                            <path d="M2 12h4" />
                            <path d="M18 12h4" />
                            <path d="M4.93 19.07l2.83-2.83" />
                            <path d="M16.24 7.76l2.83-2.83" />
                          </svg>
                          <span className="text-sm font-medium">Smart Analysis</span>
                        </div>
                        <div className="flex items-center gap-2 p-3 rounded-lg bg-card/50">
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            className="h-5 w-5 text-primary"
                          >
                            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                          </svg>
                          <span className="text-sm font-medium">Priority Ranking</span>
                        </div>
                        <div className="flex items-center gap-2 p-3 rounded-lg bg-card/50">
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            className="h-5 w-5 text-primary"
                          >
                            <circle cx="12" cy="12" r="10" />
                            <polyline points="12 6 12 12 16 14" />
                          </svg>
                          <span className="text-sm font-medium">Timeline预测</span>
                        </div>
                      </div>
                    </div>
                    <AIWorkflowPanel eventId={event.id} />
                  </div>
                </TabsContent>
              </Tabs>
            </div>

            {/* Sidebar - AI Panel */}
            <div className="lg:col-span-1">
              <div className="sticky top-0 space-y-6">
                <AIWorkflowPanel eventId={event.id} />
              </div>
            </div>
          </div>
        </main>
      </div>

      <EventWizard
        isOpen={isWizardOpen}
        onClose={() => setIsWizardOpen(false)}
      />
    </div>
  );
}

"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";
import {
  Check,
  ChevronLeft,
  ChevronRight,
  FileText,
  Calendar,
  Settings,
  Eye,
  Loader2,
} from "lucide-react";
import { createEvent } from "@/lib/api";
import type { EventWizardData, EventFormat } from "@/lib/types";
import { toast } from "sonner";

interface EventWizardProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit?: (data: EventWizardData) => Promise<void>;
}

const steps = [
  { id: 1, name: "Basics", icon: FileText, description: "Event details" },
  { id: 2, name: "Schedule", icon: Calendar, description: "Date & time" },
  { id: 3, name: "Resources", icon: Settings, description: "Venue & speakers" },
  { id: 4, name: "Review", icon: Eye, description: "Confirm details" },
];

const initialFormData: EventWizardData = {
  title: "",
  description: "",
  topic: "",
  date: "",
  registrationDeadline: "",
  format: "in-person",
  venuePreferences: "",
  speakerRequirements: "",
  sponsorInfo: "",
};

export function EventWizard({ isOpen, onClose, onSubmit }: EventWizardProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<EventWizardData>(initialFormData);
  const [errors, setErrors] = useState<Partial<Record<keyof EventWizardData, string>>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const updateFormData = <K extends keyof EventWizardData>(
    field: K,
    value: EventWizardData[K]
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  };

  const validateStep = (step: number): boolean => {
    const newErrors: Partial<Record<keyof EventWizardData, string>> = {};

    if (step === 1) {
      if (!formData.title.trim()) newErrors.title = "Title is required";
      if (!formData.description.trim()) newErrors.description = "Description is required";
      if (!formData.topic.trim()) newErrors.topic = "Topic is required";
    }

    if (step === 2) {
      if (!formData.date) newErrors.date = "Event date is required";
      if (!formData.registrationDeadline) {
        newErrors.registrationDeadline = "Registration deadline is required";
      } else if (formData.date && new Date(formData.registrationDeadline) > new Date(formData.date)) {
        newErrors.registrationDeadline = "Deadline must be before event date";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep((prev) => Math.min(prev + 1, 4));
    }
  };

  const handleBack = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 1));
  };

  const handleSubmit = async () => {
    if (!validateStep(currentStep)) return;

    setIsSubmitting(true);
    try {
      if (onSubmit) {
        await onSubmit(formData);
      } else {
        // Submit to FastAPI backend
        await createEvent(formData);
        toast.success("Event created successfully!");
      }
      handleClose();
    } catch (error) {
      console.error("Error creating event:", error);
      toast.error(error instanceof Error ? error.message : "Failed to create event. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setCurrentStep(1);
    setFormData(initialFormData);
    setErrors({});
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl bg-card border-border p-0 gap-0 max-h-[calc(100vh-4rem)] overflow-hidden">
        {/* Progress Steps */}
        <div className="border-b border-border bg-secondary/30 px-6 py-4 shrink-0 w-full overflow-hidden">
          <div className="flex items-center justify-between w-full min-w-0">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div className="flex items-center gap-3">
                  <div
                    className={cn(
                      "flex h-10 w-10 items-center justify-center rounded-full border-2 transition-all duration-300",
                      currentStep > step.id
                        ? "border-primary bg-primary text-primary-foreground"
                        : currentStep === step.id
                          ? "border-primary bg-primary/10 text-primary"
                          : "border-border bg-secondary text-muted-foreground"
                    )}
                  >
                    {currentStep > step.id ? (
                      <Check className="h-5 w-5" />
                    ) : (
                      <step.icon className="h-5 w-5" />
                    )}
                  </div>
                  <div className="hidden sm:block">
                    <p
                      className={cn(
                        "text-sm font-medium transition-colors",
                        currentStep >= step.id
                          ? "text-card-foreground"
                          : "text-muted-foreground"
                      )}
                    >
                      {step.name}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {step.description}
                    </p>
                  </div>
                </div>
                {index < steps.length - 1 && (
                  <div
                    className={cn(
                      "mx-4 h-0.5 w-8 sm:w-12 lg:w-16 transition-colors duration-300",
                      currentStep > step.id ? "bg-primary" : "bg-border"
                    )}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        <DialogHeader className="px-6 pt-6 pb-2 shrink-0">
          <DialogTitle className="text-xl text-card-foreground">
            {currentStep === 1 && "Event Basics"}
            {currentStep === 2 && "Schedule & Format"}
            {currentStep === 3 && "Resources & Requirements"}
            {currentStep === 4 && "Review & Create"}
          </DialogTitle>
        </DialogHeader>

        {/* Step Content */}
        <div className="px-6 py-4 min-h-[320px] overflow-y-auto max-h-[calc(100vh-20rem)]">
          {/* Step 1: Basics */}
          {currentStep === 1 && (
            <div className="space-y-4 animate-fade-in">
              <div className="space-y-2">
                <Label htmlFor="title" className="text-card-foreground">
                  Event Title <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={(e) => updateFormData("title", e.target.value)}
                  placeholder="Enter event title"
                  className={cn(
                    "bg-input border-border text-foreground placeholder:text-muted-foreground",
                    errors.title && "border-destructive"
                  )}
                />
                {errors.title && (
                  <p className="text-sm text-destructive">{errors.title}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="description" className="text-card-foreground">
                  Description <span className="text-destructive">*</span>
                </Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => updateFormData("description", e.target.value)}
                  placeholder="Describe your event"
                  rows={3}
                  className={cn(
                    "bg-input border-border text-foreground placeholder:text-muted-foreground resize-none",
                    errors.description && "border-destructive"
                  )}
                />
                {errors.description && (
                  <p className="text-sm text-destructive">{errors.description}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="topic" className="text-card-foreground">
                  Topic <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="topic"
                  value={formData.topic}
                  onChange={(e) => updateFormData("topic", e.target.value)}
                  placeholder="e.g., Technology, Marketing, Team Building"
                  className={cn(
                    "bg-input border-border text-foreground placeholder:text-muted-foreground",
                    errors.topic && "border-destructive"
                  )}
                />
                {errors.topic && (
                  <p className="text-sm text-destructive">{errors.topic}</p>
                )}
              </div>
            </div>
          )}

          {/* Step 2: Schedule */}
          {currentStep === 2 && (
            <div className="space-y-4 animate-fade-in">
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="date" className="text-card-foreground">
                    Event Date <span className="text-destructive">*</span>
                  </Label>
                  <Input
                    id="date"
                    type="date"
                    value={formData.date}
                    onChange={(e) => updateFormData("date", e.target.value)}
                    className={cn(
                      "bg-input border-border text-foreground",
                      errors.date && "border-destructive"
                    )}
                  />
                  {errors.date && (
                    <p className="text-sm text-destructive">{errors.date}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="deadline" className="text-card-foreground">
                    Registration Deadline <span className="text-destructive">*</span>
                  </Label>
                  <Input
                    id="deadline"
                    type="date"
                    value={formData.registrationDeadline}
                    onChange={(e) =>
                      updateFormData("registrationDeadline", e.target.value)
                    }
                    className={cn(
                      "bg-input border-border text-foreground",
                      errors.registrationDeadline && "border-destructive"
                    )}
                  />
                  {errors.registrationDeadline && (
                    <p className="text-sm text-destructive">
                      {errors.registrationDeadline}
                    </p>
                  )}
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="format" className="text-card-foreground">
                  Event Format
                </Label>
                <Select
                  value={formData.format}
                  onValueChange={(value: EventFormat) =>
                    updateFormData("format", value)
                  }
                >
                  <SelectTrigger className="bg-input border-border text-foreground">
                    <SelectValue placeholder="Select format" />
                  </SelectTrigger>
                  <SelectContent className="bg-popover border-border">
                    <SelectItem value="in-person" className="text-popover-foreground hover:bg-secondary">
                      In-Person
                    </SelectItem>
                    <SelectItem value="virtual" className="text-popover-foreground hover:bg-secondary">
                      Virtual
                    </SelectItem>
                    <SelectItem value="hybrid" className="text-popover-foreground hover:bg-secondary">
                      Hybrid
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}

          {/* Step 3: Resources */}
          {currentStep === 3 && (
            <div className="space-y-4 animate-fade-in">
              <div className="space-y-2">
                <Label htmlFor="venue" className="text-card-foreground">
                  Venue Preferences
                </Label>
                <Textarea
                  id="venue"
                  value={formData.venuePreferences}
                  onChange={(e) =>
                    updateFormData("venuePreferences", e.target.value)
                  }
                  placeholder="Describe your ideal venue (location, capacity, amenities)"
                  rows={2}
                  className="bg-input border-border text-foreground placeholder:text-muted-foreground resize-none"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="speakers" className="text-card-foreground">
                  Speaker Requirements
                </Label>
                <Textarea
                  id="speakers"
                  value={formData.speakerRequirements}
                  onChange={(e) =>
                    updateFormData("speakerRequirements", e.target.value)
                  }
                  placeholder="Number and type of speakers needed"
                  rows={2}
                  className="bg-input border-border text-foreground placeholder:text-muted-foreground resize-none"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="sponsors" className="text-card-foreground">
                  Sponsor Information
                </Label>
                <Textarea
                  id="sponsors"
                  value={formData.sponsorInfo}
                  onChange={(e) => updateFormData("sponsorInfo", e.target.value)}
                  placeholder="Sponsorship tiers and packages"
                  rows={2}
                  className="bg-input border-border text-foreground placeholder:text-muted-foreground resize-none"
                />
              </div>
            </div>
          )}

          {/* Step 4: Review */}
          {currentStep === 4 && (
            <div className="space-y-4 animate-fade-in">
              <div className="rounded-lg border border-border bg-secondary/30 p-4 space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">
                    Event Title
                  </h4>
                  <p className="text-card-foreground">{formData.title}</p>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">
                    Description
                  </h4>
                  <p className="text-card-foreground">{formData.description}</p>
                </div>

                <div className="grid gap-4 sm:grid-cols-3">
                  <div>
                    <h4 className="text-sm font-medium text-muted-foreground">
                      Topic
                    </h4>
                    <p className="text-card-foreground">{formData.topic}</p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-muted-foreground">
                      Date
                    </h4>
                    <p className="text-card-foreground">
                      {formData.date
                        ? new Date(formData.date).toLocaleDateString("en-US", {
                            month: "long",
                            day: "numeric",
                            year: "numeric",
                          })
                        : "-"}
                    </p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-muted-foreground">
                      Format
                    </h4>
                    <p className="text-card-foreground capitalize">
                      {formData.format}
                    </p>
                  </div>
                </div>

                {(formData.venuePreferences ||
                  formData.speakerRequirements ||
                  formData.sponsorInfo) && (
                  <div className="border-t border-border pt-4 space-y-3">
                    {formData.venuePreferences && (
                      <div>
                        <h4 className="text-sm font-medium text-muted-foreground">
                          Venue Preferences
                        </h4>
                        <p className="text-card-foreground text-sm">
                          {formData.venuePreferences}
                        </p>
                      </div>
                    )}
                    {formData.speakerRequirements && (
                      <div>
                        <h4 className="text-sm font-medium text-muted-foreground">
                          Speaker Requirements
                        </h4>
                        <p className="text-card-foreground text-sm">
                          {formData.speakerRequirements}
                        </p>
                      </div>
                    )}
                    {formData.sponsorInfo && (
                      <div>
                        <h4 className="text-sm font-medium text-muted-foreground">
                          Sponsor Information
                        </h4>
                        <p className="text-card-foreground text-sm">
                          {formData.sponsorInfo}
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>

              <p className="text-sm text-muted-foreground">
                By creating this event, a workflow will be automatically
                generated with tasks for planning, logistics, marketing, and
                execution.
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-border bg-secondary/30 px-6 py-4 shrink-0">
          <Button
            variant="ghost"
            onClick={currentStep === 1 ? handleClose : handleBack}
            disabled={isSubmitting}
            className="text-card-foreground hover:bg-secondary"
          >
            <ChevronLeft className="mr-1 h-4 w-4" />
            {currentStep === 1 ? "Cancel" : "Back"}
          </Button>

          {currentStep < 4 ? (
            <Button onClick={handleNext} className="bg-primary text-primary-foreground hover:bg-primary/90">
              Next
              <ChevronRight className="ml-1 h-4 w-4" />
            </Button>
          ) : (
            <Button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="bg-primary text-primary-foreground hover:bg-primary/90"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating...
                </>
              ) : (
                "Create Event"
              )}
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

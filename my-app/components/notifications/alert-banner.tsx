"use client";

import { useState } from "react";
import { X, AlertTriangle, CheckCircle, XCircle, Info } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type AlertType = "success" | "warning" | "error" | "info";

interface AlertBannerProps {
  type: AlertType;
  title: string;
  message?: string;
  dismissible?: boolean;
  onDismiss?: () => void;
  className?: string;
}

const alertConfig: Record<
  AlertType,
  { icon: typeof AlertTriangle; bgClass: string; iconClass: string }
> = {
  success: {
    icon: CheckCircle,
    bgClass: "bg-success/10 border-success/30",
    iconClass: "text-success",
  },
  warning: {
    icon: AlertTriangle,
    bgClass: "bg-warning/10 border-warning/30",
    iconClass: "text-warning",
  },
  error: {
    icon: XCircle,
    bgClass: "bg-destructive/10 border-destructive/30",
    iconClass: "text-destructive",
  },
  info: {
    icon: Info,
    bgClass: "bg-info/10 border-info/30",
    iconClass: "text-info",
  },
};

export function AlertBanner({
  type,
  title,
  message,
  dismissible = true,
  onDismiss,
  className,
}: AlertBannerProps) {
  const [isDismissed, setIsDismissed] = useState(false);

  if (isDismissed) return null;

  const config = alertConfig[type];
  const Icon = config.icon;

  const handleDismiss = () => {
    setIsDismissed(true);
    onDismiss?.();
  };

  return (
    <div
      role="alert"
      className={cn(
        "flex items-start gap-3 rounded-lg border p-4 animate-slide-up",
        config.bgClass,
        className
      )}
    >
      <Icon className={cn("h-5 w-5 shrink-0 mt-0.5", config.iconClass)} />
      <div className="flex-1 min-w-0">
        <p className="font-medium text-foreground">{title}</p>
        {message && (
          <p className="text-sm text-muted-foreground mt-1">{message}</p>
        )}
      </div>
      {dismissible && (
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6 shrink-0 text-muted-foreground hover:text-foreground"
          onClick={handleDismiss}
          aria-label="Dismiss alert"
        >
          <X className="h-4 w-4" />
        </Button>
      )}
    </div>
  );
}

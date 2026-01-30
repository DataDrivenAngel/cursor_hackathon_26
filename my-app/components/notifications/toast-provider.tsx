"use client";

import { Toaster } from "sonner";

export function ToastProvider() {
  return (
    <Toaster
      position="top-right"
      toastOptions={{
        style: {
          background: "var(--color-card)",
          color: "var(--color-card-foreground)",
          border: "1px solid var(--color-border)",
        },
        classNames: {
          success: "border-success/50",
          error: "border-destructive/50",
          warning: "border-warning/50",
          info: "border-info/50",
        },
      }}
    />
  );
}

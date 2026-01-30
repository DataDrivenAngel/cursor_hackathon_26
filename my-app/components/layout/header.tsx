"use client";

import { useState } from "react";
import { Bell, Search, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { Notification } from "@/lib/types";

interface HeaderProps {
  title: string;
  subtitle?: string;
  notifications?: Notification[];
}

export function Header({ title, subtitle, notifications = [] }: HeaderProps) {
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const unreadCount = notifications.filter((n) => !n.isRead).length;

  return (
    <header className="flex h-16 items-center justify-between border-b border-border bg-card px-6">
      {/* Title Section */}
      <div>
        <h1 className="text-xl font-semibold text-card-foreground">{title}</h1>
        {subtitle && (
          <p className="text-sm text-muted-foreground">{subtitle}</p>
        )}
      </div>

      {/* Actions Section */}
      <div className="flex items-center gap-4">
        {/* Search */}
        <div
          className={cn(
            "relative transition-all duration-300",
            isSearchFocused ? "w-80" : "w-64"
          )}
        >
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search events, tasks..."
            className="pl-9 bg-secondary border-border text-foreground placeholder:text-muted-foreground"
            onFocus={() => setIsSearchFocused(true)}
            onBlur={() => setIsSearchFocused(false)}
          />
        </div>

        {/* Notifications */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="relative text-foreground hover:bg-secondary"
              aria-label={`Notifications ${unreadCount > 0 ? `(${unreadCount} unread)` : ""}`}
            >
              <Bell className="h-5 w-5" />
              {unreadCount > 0 && (
                <Badge className="absolute -right-1 -top-1 h-5 w-5 rounded-full p-0 text-xs flex items-center justify-center bg-destructive text-destructive-foreground">
                  {unreadCount}
                </Badge>
              )}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-80 bg-popover border-border">
            <DropdownMenuLabel className="text-popover-foreground">Notifications</DropdownMenuLabel>
            <DropdownMenuSeparator className="bg-border" />
            {notifications.length === 0 ? (
              <div className="p-4 text-center text-sm text-muted-foreground">
                No notifications
              </div>
            ) : (
              notifications.slice(0, 5).map((notification) => (
                <DropdownMenuItem
                  key={notification.id}
                  className={cn(
                    "flex flex-col items-start gap-1 p-3 cursor-pointer hover:bg-secondary",
                    !notification.isRead && "bg-secondary/50"
                  )}
                >
                  <div className="flex w-full items-center justify-between">
                    <span
                      className={cn(
                        "text-sm font-medium text-popover-foreground",
                        notification.type === "error" && "text-destructive",
                        notification.type === "warning" && "text-warning",
                        notification.type === "success" && "text-success"
                      )}
                    >
                      {notification.title}
                    </span>
                    {!notification.isRead && (
                      <span className="h-2 w-2 rounded-full bg-primary" />
                    )}
                  </div>
                  <span className="text-xs text-muted-foreground line-clamp-2">
                    {notification.message}
                  </span>
                </DropdownMenuItem>
              ))
            )}
            {notifications.length > 0 && (
              <>
                <DropdownMenuSeparator className="bg-border" />
                <DropdownMenuItem className="justify-center text-sm text-primary hover:bg-secondary cursor-pointer">
                  View all notifications
                </DropdownMenuItem>
              </>
            )}
          </DropdownMenuContent>
        </DropdownMenu>

        {/* User Menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="text-foreground hover:bg-secondary"
              aria-label="User menu"
            >
              <User className="h-5 w-5" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="bg-popover border-border">
            <DropdownMenuLabel className="text-popover-foreground">My Account</DropdownMenuLabel>
            <DropdownMenuSeparator className="bg-border" />
            <DropdownMenuItem className="text-popover-foreground hover:bg-secondary cursor-pointer">Profile</DropdownMenuItem>
            <DropdownMenuItem className="text-popover-foreground hover:bg-secondary cursor-pointer">Settings</DropdownMenuItem>
            <DropdownMenuSeparator className="bg-border" />
            <DropdownMenuItem className="text-popover-foreground hover:bg-secondary cursor-pointer">Sign out</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}

import React from "react";
import { cn } from "@/lib/utils";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "default" | "critical" | "high" | "medium" | "low" | "outline" | "info" | "purple" | "lime";
  size?: "sm" | "md";
  className?: string;
  dot?: boolean;
}

export function Badge({ children, variant = "default", dot, size = "sm", className }: BadgeProps) {
  const variants: Record<string, string> = {
    default:  "bg-[rgba(255,255,255,0.05)] text-fog",
    critical: "bg-[rgba(235,87,87,0.10)] text-coral-red",
    high:     "bg-[rgba(228,242,34,0.08)] text-acid-lime",
    medium:   "bg-[rgba(139,92,246,0.10)] text-lavender",
    low:      "bg-[rgba(39,166,68,0.10)] text-pulse-green",
    info:     "bg-[rgba(2,184,204,0.10)] text-signal-teal",
    purple:   "bg-[rgba(99,102,241,0.10)] text-iris-violet",
    lime:     "bg-[rgba(228,242,34,0.12)] text-acid-lime",
    outline:  "bg-transparent text-fog border border-graphite",
  };

  const dotColors: Record<string, string> = {
    default:  "bg-fog",
    critical: "bg-coral-red",
    high:     "bg-acid-lime",
    medium:   "bg-lavender",
    low:      "bg-pulse-green",
    info:     "bg-signal-teal",
    purple:   "bg-iris-violet",
    lime:     "bg-acid-lime",
    outline:  "bg-fog",
  };

  const sizes: Record<string, string> = {
    sm: "px-1.5 py-0 text-label",
    md: "px-2.5 py-0.5 text-caption",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-[4px] font-normal transition-colors",
        variants[variant],
        sizes[size],
        className
      )}
    >
      {dot && (
        <span className={cn("w-1.5 h-1.5 rounded-full animate-pulse-dot flex-shrink-0", dotColors[variant])} />
      )}
      {children}
    </span>
  );
}

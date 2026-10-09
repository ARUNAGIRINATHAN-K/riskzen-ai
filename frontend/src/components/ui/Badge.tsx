import React from "react";
import { cn } from "@/lib/utils";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "default" | "critical" | "high" | "medium" | "low" | "outline" | "info" | "purple";
  size?: "sm" | "md";
  className?: string;
}

export function Badge({ children, variant = "default", size = "sm", className }: BadgeProps) {
  const variants = {
    default: "bg-zinc-800 text-zinc-300 border-zinc-700/50",
    critical: "bg-rose-500/10 text-rose-400 border-rose-500/20 shadow-sm shadow-rose-950/20",
    high: "bg-amber-500/10 text-amber-400 border-amber-500/20 shadow-sm shadow-amber-950/20",
    medium: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
    low: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    info: "bg-sky-500/10 text-sky-400 border-sky-500/20",
    purple: "bg-purple-500/10 text-purple-400 border-purple-500/20",
    outline: "bg-transparent text-zinc-400 border-zinc-700/60",
  };

  const sizes = {
    sm: "px-2.5 py-0.5 text-xs",
    md: "px-3 py-1 text-sm font-medium",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full font-medium border transition-colors",
        variants[variant],
        sizes[size],
        className
      )}
    >
      {children}
    </span>
  );
}

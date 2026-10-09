import React from "react";
import { cn } from "@/lib/utils";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  hoverEffect?: boolean;
  glow?: "indigo" | "rose" | "amber" | "emerald" | "none";
}

export function Card({
  children,
  hoverEffect = false,
  glow = "none",
  className,
  ...props
}: CardProps) {
  const glowStyles = {
    none: "",
    indigo: "hover:border-indigo-500/40 hover:shadow-lg hover:shadow-indigo-500/10",
    rose: "hover:border-rose-500/40 hover:shadow-lg hover:shadow-rose-500/10",
    amber: "hover:border-amber-500/40 hover:shadow-lg hover:shadow-amber-500/10",
    emerald: "hover:border-emerald-500/40 hover:shadow-lg hover:shadow-emerald-500/10",
  };

  return (
    <div
      className={cn(
        "rounded-xl border border-zinc-800 bg-zinc-900/70 backdrop-blur-md p-5 text-zinc-100 transition-all duration-200",
        hoverEffect && "hover:-translate-y-0.5 hover:bg-zinc-900/90",
        glowStyles[glow],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({
  title,
  subtitle,
  action,
  className,
}: {
  title: React.ReactNode;
  subtitle?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("flex items-start justify-between gap-4 mb-4", className)}>
      <div>
        <h3 className="text-base font-semibold text-zinc-100 tracking-tight">{title}</h3>
        {subtitle && <p className="text-xs text-zinc-400 mt-0.5">{subtitle}</p>}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  );
}

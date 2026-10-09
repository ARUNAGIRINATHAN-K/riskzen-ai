import React from "react";
import { cn } from "@/lib/utils";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  hoverEffect?: boolean;
  variant?: "default" | "subtle" | "elevated";
}

export function Card({
  children,
  hoverEffect = false,
  variant = "default",
  className,
  ...props
}: CardProps) {
  const variantStyles = {
    default: "bg-carbon border border-graphite rounded-[12px] p-6 shadow-sm",
    subtle: "bg-[rgba(255,255,255,0.02)] border border-graphite/50 rounded-[6px] p-3.5",
    elevated: "bg-obsidian border border-smoke/60 rounded-[12px] p-6 shadow-md",
  };

  return (
    <div
      className={cn(
        "text-mist transition-colors duration-150",
        variantStyles[variant],
        hoverEffect && "hover:border-smoke hover:bg-carbon/90",
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
        <h3 className="text-body-sm font-[510] text-paper tracking-[-0.011em]">{title}</h3>
        {subtitle && <p className="text-label text-fog mt-0.5">{subtitle}</p>}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  );
}

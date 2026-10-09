import { RiskCategory, RiskSeverity, ProjectHealth } from "@/types";

export function cn(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(" ");
}

export function formatDate(dateString?: string | null): string {
  if (!dateString) return "—";
  try {
    const d = new Date(dateString);
    return d.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  } catch {
    return dateString;
  }
}

export function formatDateTime(dateString?: string | null): string {
  if (!dateString) return "—";
  try {
    const d = new Date(dateString);
    return d.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return dateString;
  }
}

export function getSeverityBadge(severity: RiskSeverity): {
  label: string;
  bg: string;
  text: string;
  border: string;
  dot: string;
} {
  switch (severity) {
    case "critical":
      return {
        label: "Critical",
        bg: "bg-[rgba(235,87,87,0.10)]",
        text: "text-coral-red",
        border: "border-[rgba(235,87,87,0.25)]",
        dot: "bg-coral-red",
      };
    case "high":
      return {
        label: "High",
        bg: "bg-[rgba(228,242,34,0.08)]",
        text: "text-acid-lime",
        border: "border-[rgba(228,242,34,0.25)]",
        dot: "bg-acid-lime",
      };
    case "medium":
      return {
        label: "Medium",
        bg: "bg-[rgba(139,92,246,0.10)]",
        text: "text-lavender",
        border: "border-[rgba(139,92,246,0.25)]",
        dot: "bg-lavender",
      };
    case "low":
    default:
      return {
        label: "Low",
        bg: "bg-[rgba(39,166,68,0.10)]",
        text: "text-pulse-green",
        border: "border-[rgba(39,166,68,0.25)]",
        dot: "bg-pulse-green",
      };
  }
}

export function getHealthBadge(health: ProjectHealth): {
  label: string;
  bg: string;
  text: string;
  dot: string;
  border: string;
} {
  switch (health) {
    case "green":
      return {
        label: "Healthy",
        bg: "bg-[rgba(39,166,68,0.10)]",
        text: "text-pulse-green",
        dot: "bg-pulse-green",
        border: "border-[rgba(39,166,68,0.25)]",
      };
    case "yellow":
      return {
        label: "Caution",
        bg: "bg-[rgba(139,92,246,0.10)]",
        text: "text-lavender",
        dot: "bg-lavender",
        border: "border-[rgba(139,92,246,0.25)]",
      };
    case "orange":
      return {
        label: "At Risk",
        bg: "bg-[rgba(228,242,34,0.08)]",
        text: "text-acid-lime",
        dot: "bg-acid-lime",
        border: "border-[rgba(228,242,34,0.25)]",
      };
    case "red":
      return {
        label: "Critical",
        bg: "bg-[rgba(235,87,87,0.10)]",
        text: "text-coral-red",
        dot: "bg-coral-red",
        border: "border-[rgba(235,87,87,0.25)]",
      };
    default:
      return {
        label: "Unknown",
        bg: "bg-[rgba(255,255,255,0.05)]",
        text: "text-fog",
        dot: "bg-fog",
        border: "border-graphite",
      };
  }
}

export function getCategoryLabel(category: RiskCategory | string): string {
  const map: Record<string, string> = {
    schedule: "Schedule & Delay",
    dependency: "Dependency Blocker",
    scope: "Scope Creep",
    capacity: "Capacity Bottleneck",
    quality: "Quality & Defects",
    budget: "Budget & Burn",
    decision: "Decision Latency",
  };
  return map[category] || category.toUpperCase();
}

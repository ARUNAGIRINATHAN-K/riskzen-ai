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
} {
  switch (severity) {
    case "critical":
      return {
        label: "Critical",
        bg: "bg-red-500/10",
        text: "text-red-500",
        border: "border-red-500/30",
      };
    case "high":
      return {
        label: "High",
        bg: "bg-amber-500/10",
        text: "text-amber-500",
        border: "border-amber-500/30",
      };
    case "medium":
      return {
        label: "Medium",
        bg: "bg-yellow-500/10",
        text: "text-yellow-500",
        border: "border-yellow-500/30",
      };
    case "low":
    default:
      return {
        label: "Low",
        bg: "bg-emerald-500/10",
        text: "text-emerald-500",
        border: "border-emerald-500/30",
      };
  }
}

export function getHealthBadge(health: ProjectHealth): {
  label: string;
  bg: string;
  text: string;
  dot: string;
} {
  switch (health) {
    case "green":
      return { label: "Healthy", bg: "bg-emerald-500/10", text: "text-emerald-400", dot: "bg-emerald-400" };
    case "yellow":
      return { label: "Caution", bg: "bg-yellow-500/10", text: "text-yellow-400", dot: "bg-yellow-400" };
    case "orange":
      return { label: "At Risk", bg: "bg-amber-500/10", text: "text-amber-400", dot: "bg-amber-400" };
    case "red":
      return { label: "Critical", bg: "bg-red-500/10", text: "text-red-400", dot: "bg-red-400" };
    default:
      return { label: "Unknown", bg: "bg-zinc-500/10", text: "text-zinc-400", dot: "bg-zinc-400" };
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

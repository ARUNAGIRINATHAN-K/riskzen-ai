import React from "react";
import { Shield } from "@/components/icons";

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  action?: React.ReactNode;
}

export function EmptyState({
  icon = <Shield className="w-10 h-10 text-zinc-500" />,
  title,
  description,
  action,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center rounded-2xl border border-dashed border-zinc-800 bg-zinc-900/30">
      <div className="p-3 bg-zinc-800/50 rounded-2xl mb-4 border border-zinc-700/40">
        {icon}
      </div>
      <h3 className="text-base font-semibold text-zinc-200 tracking-tight">{title}</h3>
      <p className="text-xs text-zinc-400 max-w-sm mt-1.5 mb-6">{description}</p>
      {action && <div>{action}</div>}
    </div>
  );
}

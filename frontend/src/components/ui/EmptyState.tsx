import React from "react";
import { Shield } from "@/components/icons";

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  action?: React.ReactNode;
}

export function EmptyState({
  icon = <Shield className="w-8 h-8 text-fog" />,
  title,
  description,
  action,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center rounded-[12px] border border-graphite bg-carbon/50">
      <div className="p-3 bg-[rgba(255,255,255,0.03)] rounded-[8px] mb-3.5 border border-graphite">
        {icon}
      </div>
      <h3 className="text-body-sm font-[510] text-paper tracking-[-0.011em]">{title}</h3>
      <p className="text-caption text-fog max-w-sm mt-1 mb-5">{description}</p>
      {action && <div>{action}</div>}
    </div>
  );
}

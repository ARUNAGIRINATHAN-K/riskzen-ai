import React from "react";
import { cn } from "@/lib/utils";

export function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-[4px] bg-graphite/60", className)}
      {...props}
    />
  );
}

export function CardSkeleton() {
  return (
    <div className="rounded-[12px] border border-graphite bg-carbon p-6 space-y-3">
      <div className="flex justify-between items-center">
        <Skeleton className="h-3.5 w-1/3" />
        <Skeleton className="h-3.5 w-16" />
      </div>
      <Skeleton className="h-5 w-3/4" />
      <Skeleton className="h-10 w-full" />
      <div className="flex gap-2 pt-2">
        <Skeleton className="h-3.5 w-20" />
        <Skeleton className="h-3.5 w-24" />
      </div>
    </div>
  );
}

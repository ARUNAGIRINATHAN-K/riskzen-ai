import React from "react";
import { cn } from "@/lib/utils";

export function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-lg bg-zinc-800/60", className)}
      {...props}
    />
  );
}

export function CardSkeleton() {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-5 space-y-3">
      <div className="flex justify-between items-center">
        <Skeleton className="h-4 w-1/3" />
        <Skeleton className="h-4 w-16" />
      </div>
      <Skeleton className="h-6 w-3/4" />
      <Skeleton className="h-12 w-full" />
      <div className="flex gap-2 pt-2">
        <Skeleton className="h-4 w-20" />
        <Skeleton className="h-4 w-24" />
      </div>
    </div>
  );
}

import React from "react";
import { Filter, Search } from "@/components/icons";

interface RiskFiltersProps {
  category: string;
  setCategory: (c: string) => void;
  severity: string;
  setSeverity: (s: string) => void;
  status: string;
  setStatus: (s: string) => void;
  search: string;
  setSearch: (q: string) => void;
}

export function RiskFilters({
  category,
  setCategory,
  severity,
  setSeverity,
  status,
  setStatus,
  search,
  setSearch,
}: RiskFiltersProps) {
  return (
    <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-900/60 flex flex-col md:flex-row items-center gap-3">
      {/* Search Input */}
      <div className="relative flex-1 w-full">
        <Search className="w-4 h-4 text-zinc-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search risks by title, keyword, or signal..."
          className="w-full pl-9 pr-4 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-indigo-500"
        />
      </div>

      {/* Category Dropdown */}
      <select
        value={category}
        onChange={(e) => setCategory(e.target.value)}
        className="w-full md:w-44 px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-xs text-zinc-200 focus:outline-none focus:border-indigo-500"
      >
        <option value="">All Categories</option>
        <option value="schedule">Schedule</option>
        <option value="dependency">Dependency</option>
        <option value="capacity">Capacity</option>
        <option value="scope">Scope</option>
        <option value="quality">Quality</option>
        <option value="budget">Budget</option>
        <option value="decision">Decision</option>
      </select>

      {/* Severity Dropdown */}
      <select
        value={severity}
        onChange={(e) => setSeverity(e.target.value)}
        className="w-full md:w-36 px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-xs text-zinc-200 focus:outline-none focus:border-indigo-500"
      >
        <option value="">All Severities</option>
        <option value="critical">Critical</option>
        <option value="high">High</option>
        <option value="medium">Medium</option>
        <option value="low">Low</option>
      </select>

      {/* Status Dropdown */}
      <select
        value={status}
        onChange={(e) => setStatus(e.target.value)}
        className="w-full md:w-36 px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-xs text-zinc-200 focus:outline-none focus:border-indigo-500"
      >
        <option value="">All Statuses</option>
        <option value="active">Active</option>
        <option value="new">New</option>
        <option value="mitigated">Mitigated</option>
        <option value="resolved">Resolved</option>
        <option value="dismissed">Dismissed</option>
      </select>
    </div>
  );
}

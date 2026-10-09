import React from "react";
import { Search } from "@/components/icons";

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
    <div className="p-3 rounded-[12px] border border-graphite bg-carbon flex flex-col md:flex-row items-center gap-2.5">
      {/* Search Input */}
      <div className="relative flex-1 w-full">
        <Search className="w-3.5 h-3.5 text-fog absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search risks by title, keyword, or signal..."
          className="w-full pl-8 pr-3 py-1.5 rounded-[6px] bg-void border border-graphite text-caption text-mist placeholder-fog focus:outline-none focus:border-mist transition-colors"
        />
      </div>

      {/* Category Dropdown */}
      <select
        value={category}
        onChange={(e) => setCategory(e.target.value)}
        className="w-full md:w-44 px-3 py-1.5 rounded-[6px] bg-void border border-graphite text-caption text-mist focus:outline-none focus:border-mist transition-colors"
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
        className="w-full md:w-36 px-3 py-1.5 rounded-[6px] bg-void border border-graphite text-caption text-mist focus:outline-none focus:border-mist transition-colors"
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
        className="w-full md:w-36 px-3 py-1.5 rounded-[6px] bg-void border border-graphite text-caption text-mist focus:outline-none focus:border-mist transition-colors"
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

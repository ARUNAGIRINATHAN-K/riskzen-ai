"use client";

import React, { useState } from "react";
import { Folder, GitBranch, RefreshCw, Sparkles } from "@/components/icons";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader } from "@/components/ui/Card";
import { api } from "@/lib/api";
import { formatDateTime } from "@/lib/utils";
import { DataSource } from "@/types";

interface DataSourcesManagerProps {
  projectId: string;
  dataSources: DataSource[];
  onRefresh?: () => void;
}

export function DataSourcesManager({ projectId, dataSources, onRefresh }: DataSourcesManagerProps) {
  const [syncingId, setSyncingId] = useState<string | null>(null);
  const [uploadingBudget, setUploadingBudget] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleSyncSource = async (sourceId: string) => {
    try {
      setSyncingId(sourceId);
      await api.triggerSync(projectId, sourceId);
      setMessage("Data source synchronization completed.");
      setTimeout(() => setMessage(null), 3000);
      if (onRefresh) onRefresh();
    } catch (err: any) {
      setMessage(`Sync failed: ${err.message}`);
    } finally {
      setSyncingId(null);
    }
  };

  const handleBudgetUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setUploadingBudget(true);
      const res = await api.uploadBudgetCSV(projectId, file);
      setMessage(`Budget CSV imported successfully (${res.records_imported} rows).`);
      setTimeout(() => setMessage(null), 3000);
      if (onRefresh) onRefresh();
    } catch (err: any) {
      setMessage(`Upload failed: ${err.message}`);
    } finally {
      setUploadingBudget(false);
    }
  };

  return (
    <Card>
      <CardHeader
        title="Connected Ingestion Sources"
        subtitle="Telemetry integrations synchronizing project deliverables, PRs, and financial budgets"
      />

      {message && (
        <div className="mb-4 p-3 rounded-lg bg-indigo-500/10 border border-indigo-500/30 text-xs text-indigo-300 font-medium">
          {message}
        </div>
      )}

      {dataSources.length === 0 ? (
        <p className="text-xs text-zinc-400 py-4 text-center">
          No external data sources connected yet.
        </p>
      ) : (
        <div className="space-y-3 mb-6">
          {dataSources.map((ds) => {
            const isGitHub = ds.source_type === "github";
            const isSyncing = syncingId === ds.id;

            return (
              <div
                key={ds.id}
                className="p-4 rounded-xl border border-zinc-800 bg-zinc-950/60 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-xl bg-zinc-800/80 shrink-0">
                    {isGitHub ? (
                      <GitBranch className="w-5 h-5 text-indigo-400" />
                    ) : (
                      <Folder className="w-5 h-5 text-emerald-400" />
                    )}
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="text-sm font-semibold text-zinc-100 uppercase">
                        {ds.source_type.replace("_", " ")}
                      </h4>
                      <Badge
                        variant={ds.status === "connected" ? "low" : "high"}
                        size="sm"
                      >
                        {ds.status}
                      </Badge>
                    </div>

                    <span className="text-xs text-zinc-400 block mt-0.5">
                      Last Synchronized: {formatDateTime(ds.last_synced_at)}
                    </span>
                  </div>
                </div>

                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => handleSyncSource(ds.id)}
                  isLoading={isSyncing}
                  className="text-xs self-end sm:self-center"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  Sync Now
                </Button>
              </div>
            );
          })}
        </div>
      )}

      {/* CSV Budget Upload Section */}
      <div className="p-4 rounded-xl border border-dashed border-zinc-800 bg-zinc-950/30 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h4 className="text-xs font-semibold text-zinc-200">
            Upload / Refresh Financial Budget CSV
          </h4>
          <p className="text-[11px] text-zinc-400 mt-0.5">
            Expected columns: <code className="font-mono text-zinc-300">month, category, planned, actual</code>
          </p>
        </div>

        <label className="cursor-pointer">
          <input
            type="file"
            accept=".csv"
            onChange={handleBudgetUpload}
            className="hidden"
            disabled={uploadingBudget}
          />
          <span className="inline-flex items-center justify-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold bg-zinc-800 hover:bg-zinc-700 text-zinc-100 border border-zinc-700 transition-colors">
            {uploadingBudget ? "Importing..." : "Select CSV File"}
          </span>
        </label>
      </div>
    </Card>
  );
}

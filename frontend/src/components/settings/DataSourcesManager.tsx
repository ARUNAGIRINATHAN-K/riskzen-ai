"use client";

import React, { useState } from "react";
import { Folder, GitBranch, RefreshCw } from "@/components/icons";
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
        <div className="mb-4 p-3 rounded-[6px] bg-void border border-graphite text-caption text-acid-lime font-[510]">
          {message}
        </div>
      )}

      {dataSources.length === 0 ? (
        <p className="text-caption text-fog py-4 text-center">
          No external data sources connected yet.
        </p>
      ) : (
        <div className="space-y-2.5 mb-6">
          {dataSources.map((ds) => {
            const isGitHub = ds.source_type === "github";
            const isSyncing = syncingId === ds.id;

            return (
              <div
                key={ds.id}
                className="p-3.5 rounded-[6px] border border-graphite bg-void flex flex-col sm:flex-row sm:items-center justify-between gap-4"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-[6px] bg-carbon border border-graphite shrink-0">
                    {isGitHub ? (
                      <GitBranch className="w-4 h-4 text-paper" />
                    ) : (
                      <Folder className="w-4 h-4 text-pulse-green" />
                    )}
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="text-caption font-[510] text-paper uppercase">
                        {ds.source_type.replace("_", " ")}
                      </h4>
                      <Badge
                        variant={ds.status === "connected" ? "low" : "high"}
                        size="sm"
                      >
                        {ds.status}
                      </Badge>
                    </div>

                    <span className="text-micro text-fog block mt-0.5 font-mono">
                      Last Synced: {formatDateTime(ds.last_synced_at)}
                    </span>
                  </div>
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleSyncSource(ds.id)}
                  isLoading={isSyncing}
                  className="self-end sm:self-center"
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
      <div className="p-4 rounded-[6px] border border-graphite bg-void flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h4 className="text-caption font-[510] text-paper">
            Upload / Refresh Financial Budget CSV
          </h4>
          <p className="text-micro text-fog mt-0.5">
            Expected columns: <code className="font-mono text-mist">month, category, planned, actual</code>
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
          <span className="inline-flex items-center justify-center gap-2 px-3 py-1.5 rounded-[6px] text-caption font-[510] bg-carbon hover:bg-obsidian text-paper border border-graphite transition-colors">
            {uploadingBudget ? "Importing..." : "Select CSV File"}
          </span>
        </label>
      </div>
    </Card>
  );
}

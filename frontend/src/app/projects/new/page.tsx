"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  ArrowRight,
  CheckCircle,
  Folder,
  GitBranch,
  Shield,
  Sparkles,
} from "@/components/icons";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { api } from "@/lib/api";

export default function NewProjectPage() {
  const router = useRouter();
  const [step, setStep] = useState<1 | 2>(1);

  // Form State
  const [name, setName] = useState("");
  const [key, setKey] = useState("");
  const [description, setDescription] = useState("");
  const [projectType, setProjectType] = useState("software");

  // Source Connection State
  const [sourceType, setSourceType] = useState<"github" | "csv_budget">("github");
  const [repoOwner, setRepoOwner] = useState("");
  const [repoName, setRepoName] = useState("");
  const [githubToken, setGithubToken] = useState("");
  const [budgetFile, setBudgetFile] = useState<File | null>(null);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [createdProject, setCreatedProject] = useState<{ id: string; name: string } | null>(null);

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    try {
      setIsLoading(true);
      setError(null);

      // Create project
      const proj = await api.createProject({
        name,
        key: key || name.substring(0, 4).toUpperCase(),
        description,
        project_type: projectType,
      });

      setCreatedProject({ id: proj.id, name: proj.name });
      setStep(2);
    } catch (err: any) {
      setError(err.message || "Failed to create project");
    } finally {
      setIsLoading(false);
    }
  };

  const handleConnectSource = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!createdProject) return;

    try {
      setIsLoading(true);
      setError(null);

      if (sourceType === "github") {
        await api.createDataSource(createdProject.id, {
          source_type: "github",
          config: {
            owner: repoOwner,
            repo: repoName,
            token: githubToken || undefined,
          },
        });
        // Trigger initial sync
        await api.triggerSync(createdProject.id);
      } else if (sourceType === "csv_budget" && budgetFile) {
        await api.uploadBudgetCSV(createdProject.id, budgetFile);
      }

      // Trigger initial risk evaluation
      try {
        await api.evaluateRisks(createdProject.id);
      } catch {
        // Safe fallback
      }

      // Navigate to project dashboard
      router.push(`/projects/${createdProject.id}`);
    } catch (err: any) {
      setError(err.message || "Failed to configure data source");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AppShell>
      <PageHeader
        title="Connect & Onboard New Project"
        subtitle="Set up your delivery tracking pipeline and configure automated risk evaluation"
        breadcrumbs={[
          { label: "Projects", href: "/projects" },
          { label: "New Project" },
        ]}
      />

      <div className="max-w-2xl mx-auto py-4">
        {/* Step Indicator */}
        <div className="flex items-center justify-between mb-8 px-4">
          <div className="flex items-center gap-3">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs ${
                step >= 1 ? "bg-indigo-600 text-white" : "bg-zinc-800 text-zinc-400"
              }`}
            >
              1
            </div>
            <span className="text-sm font-semibold text-zinc-200">Project Details</span>
          </div>

          <div className="flex-1 h-0.5 mx-4 bg-zinc-800" />

          <div className="flex items-center gap-3">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs ${
                step >= 2 ? "bg-indigo-600 text-white" : "bg-zinc-800 text-zinc-400"
              }`}
            >
              2
            </div>
            <span className={`text-sm font-semibold ${step >= 2 ? "text-zinc-200" : "text-zinc-500"}`}>
              Connect Telemetry
            </span>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-xs text-rose-300 font-medium">
            {error}
          </div>
        )}

        {/* Step 1: Project Metadata */}
        {step === 1 && (
          <Card className="p-6">
            <form onSubmit={handleCreateProject} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-zinc-200 mb-1.5">
                  Project Name *
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. NovaPay Mobile Checkout"
                  className="w-full px-3.5 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-indigo-500"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-zinc-200 mb-1.5">
                    Project Key / Prefix
                  </label>
                  <input
                    type="text"
                    value={key}
                    onChange={(e) => setKey(e.target.value)}
                    placeholder="e.g. NOVA"
                    className="w-full px-3.5 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-zinc-200 mb-1.5">
                    Project Type
                  </label>
                  <select
                    value={projectType}
                    onChange={(e) => setProjectType(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-sm text-zinc-100 focus:outline-none focus:border-indigo-500"
                  >
                    <option value="software">Software Engineering</option>
                    <option value="infrastructure">Cloud Infrastructure</option>
                    <option value="mobile">Mobile Application</option>
                    <option value="data_platform">Data & AI Platform</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-zinc-200 mb-1.5">
                  Description
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                  placeholder="Describe key delivery goals and business milestones..."
                  className="w-full px-3.5 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="pt-4 flex justify-end">
                <Button variant="primary" size="md" type="submit" isLoading={isLoading}>
                  Next: Connect Source
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </div>
            </form>
          </Card>
        )}

        {/* Step 2: Data Source Connection */}
        {step === 2 && (
          <Card className="p-6">
            <form onSubmit={handleConnectSource} className="space-y-6">
              <div>
                <label className="block text-xs font-semibold text-zinc-200 mb-2">
                  Select Primary Telemetry Source
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => setSourceType("github")}
                    className={`p-4 rounded-xl border flex items-center gap-3 transition-all ${
                      sourceType === "github"
                        ? "bg-indigo-600/15 border-indigo-500 text-white font-semibold"
                        : "bg-zinc-950 border-zinc-800 text-zinc-400 hover:border-zinc-700"
                    }`}
                  >
                    <GitBranch className="w-5 h-5 text-indigo-400 shrink-0" />
                    <div className="text-left">
                      <span className="text-xs block text-zinc-100">GitHub Connector</span>
                      <span className="text-[11px] text-zinc-400">Issues, PRs, Milestones</span>
                    </div>
                  </button>

                  <button
                    type="button"
                    onClick={() => setSourceType("csv_budget")}
                    className={`p-4 rounded-xl border flex items-center gap-3 transition-all ${
                      sourceType === "csv_budget"
                        ? "bg-indigo-600/15 border-indigo-500 text-white font-semibold"
                        : "bg-zinc-950 border-zinc-800 text-zinc-400 hover:border-zinc-700"
                    }`}
                  >
                    <Folder className="w-5 h-5 text-emerald-400 shrink-0" />
                    <div className="text-left">
                      <span className="text-xs block text-zinc-100">CSV Budget Importer</span>
                      <span className="text-[11px] text-zinc-400">Planned vs Actual Spend</span>
                    </div>
                  </button>
                </div>
              </div>

              {sourceType === "github" ? (
                <div className="space-y-4 pt-2">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-semibold text-zinc-300 mb-1">
                        Repository Owner / Org *
                      </label>
                      <input
                        type="text"
                        value={repoOwner}
                        onChange={(e) => setRepoOwner(e.target.value)}
                        placeholder="e.g. facebook"
                        className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-sm text-zinc-100 focus:outline-none focus:border-indigo-500"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-zinc-300 mb-1">
                        Repository Name *
                      </label>
                      <input
                        type="text"
                        value={repoName}
                        onChange={(e) => setRepoName(e.target.value)}
                        placeholder="e.g. react"
                        className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-sm text-zinc-100 focus:outline-none focus:border-indigo-500"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-zinc-300 mb-1">
                      GitHub Personal Access Token (Optional for public repos)
                    </label>
                    <input
                      type="password"
                      value={githubToken}
                      onChange={(e) => setGithubToken(e.target.value)}
                      placeholder="ghp_..."
                      className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-sm text-zinc-100 focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                </div>
              ) : (
                <div className="space-y-4 pt-2">
                  <div>
                    <label className="block text-xs font-semibold text-zinc-300 mb-1">
                      Budget CSV File *
                    </label>
                    <input
                      type="file"
                      accept=".csv"
                      onChange={(e) => setBudgetFile(e.target.files?.[0] || null)}
                      className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-xs text-zinc-200 focus:outline-none focus:border-indigo-500"
                      required
                    />
                    <p className="text-[11px] text-zinc-400 mt-1">
                      Expected headers: <code className="font-mono text-zinc-300">month, category, planned, actual</code>
                    </p>
                  </div>
                </div>
              )}

              <div className="pt-4 border-t border-zinc-800 flex items-center justify-between">
                <Button
                  variant="ghost"
                  size="sm"
                  type="button"
                  onClick={() => router.push(`/projects/${createdProject.id}`)}
                >
                  Skip for Now
                </Button>

                <Button variant="primary" size="md" type="submit" isLoading={isLoading}>
                  <Sparkles className="w-4 h-4" />
                  Complete Setup & Ingest Data
                </Button>
              </div>
            </form>
          </Card>
        )}
      </div>
    </AppShell>
  );
}

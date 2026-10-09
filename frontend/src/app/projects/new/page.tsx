"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  ArrowRight,
  Folder,
  GitBranch,
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
        await api.triggerSync(createdProject.id);
      } else if (sourceType === "csv_budget" && budgetFile) {
        await api.uploadBudgetCSV(createdProject.id, budgetFile);
      }

      try {
        await api.evaluateRisks(createdProject.id);
      } catch {
        // Safe fallback
      }

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
              className={`w-7 h-7 rounded-[6px] border flex items-center justify-center font-mono text-micro font-[510] ${
                step >= 1 ? "bg-acid-lime text-void border-acid-lime" : "bg-carbon text-fog border-graphite"
              }`}
            >
              1
            </div>
            <span className="text-caption font-[510] text-paper">Project Details</span>
          </div>

          <div className="flex-1 h-[1px] mx-4 bg-graphite" />

          <div className="flex items-center gap-3">
            <div
              className={`w-7 h-7 rounded-[6px] border flex items-center justify-center font-mono text-micro font-[510] ${
                step >= 2 ? "bg-acid-lime text-void border-acid-lime" : "bg-carbon text-fog border-graphite"
              }`}
            >
              2
            </div>
            <span className={`text-caption font-[510] ${step >= 2 ? "text-paper" : "text-fog"}`}>
              Connect Telemetry
            </span>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-3 rounded-[6px] bg-void border border-[rgba(235,87,87,0.3)] text-caption text-coral-red font-[510]">
            {error}
          </div>
        )}

        {/* Step 1: Project Metadata */}
        {step === 1 && (
          <Card className="p-6">
            <form onSubmit={handleCreateProject} className="space-y-4">
              <div>
                <label className="block text-caption font-[510] text-mist mb-1">
                  Project Name *
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. NovaPay Mobile Checkout"
                  className="w-full px-3 py-1.5 rounded-[6px] bg-void border border-graphite text-caption text-mist placeholder-fog focus:outline-none focus:border-mist transition-colors"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-caption font-[510] text-mist mb-1">
                    Project Key / Prefix
                  </label>
                  <input
                    type="text"
                    value={key}
                    onChange={(e) => setKey(e.target.value)}
                    placeholder="e.g. NOVA"
                    className="w-full px-3 py-1.5 rounded-[6px] bg-void border border-graphite text-caption text-mist placeholder-fog focus:outline-none focus:border-mist transition-colors font-mono"
                  />
                </div>

                <div>
                  <label className="block text-caption font-[510] text-mist mb-1">
                    Project Type
                  </label>
                  <select
                    value={projectType}
                    onChange={(e) => setProjectType(e.target.value)}
                    className="w-full px-3 py-1.5 rounded-[6px] bg-void border border-graphite text-caption text-mist focus:outline-none focus:border-mist transition-colors"
                  >
                    <option value="software">Software Engineering</option>
                    <option value="infrastructure">Cloud Infrastructure</option>
                    <option value="mobile">Mobile Application</option>
                    <option value="data_platform">Data & AI Platform</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-caption font-[510] text-mist mb-1">
                  Description
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                  placeholder="Describe key delivery goals and business milestones..."
                  className="w-full px-3 py-1.5 rounded-[6px] bg-void border border-graphite text-caption text-mist placeholder-fog focus:outline-none focus:border-mist transition-colors"
                />
              </div>

              <div className="pt-4 flex justify-end">
                <Button variant="primary" size="md" type="submit" isLoading={isLoading}>
                  Next: Connect Source
                  <ArrowRight className="w-3.5 h-3.5" />
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
                <label className="block text-caption font-[510] text-mist mb-2">
                  Select Primary Telemetry Source
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => setSourceType("github")}
                    className={`p-3.5 rounded-[6px] border flex items-center gap-3 transition-colors ${
                      sourceType === "github"
                        ? "bg-void border-acid-lime text-paper"
                        : "bg-void border-graphite text-fog hover:border-smoke"
                    }`}
                  >
                    <GitBranch className="w-4 h-4 text-paper shrink-0" />
                    <div className="text-left">
                      <span className="text-caption font-[510] block text-paper">GitHub Connector</span>
                      <span className="text-micro text-fog">Issues, PRs, Milestones</span>
                    </div>
                  </button>

                  <button
                    type="button"
                    onClick={() => setSourceType("csv_budget")}
                    className={`p-3.5 rounded-[6px] border flex items-center gap-3 transition-colors ${
                      sourceType === "csv_budget"
                        ? "bg-void border-acid-lime text-paper"
                        : "bg-void border-graphite text-fog hover:border-smoke"
                    }`}
                  >
                    <Folder className="w-4 h-4 text-pulse-green shrink-0" />
                    <div className="text-left">
                      <span className="text-caption font-[510] block text-paper">CSV Budget Importer</span>
                      <span className="text-micro text-fog">Planned vs Actual Spend</span>
                    </div>
                  </button>
                </div>
              </div>

              {sourceType === "github" ? (
                <div className="space-y-3 pt-2">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-caption font-[510] text-mist mb-1">
                        Repository Owner / Org *
                      </label>
                      <input
                        type="text"
                        value={repoOwner}
                        onChange={(e) => setRepoOwner(e.target.value)}
                        placeholder="e.g. facebook"
                        className="w-full px-3 py-1.5 rounded-[6px] bg-void border border-graphite text-caption text-mist focus:outline-none focus:border-mist transition-colors"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-caption font-[510] text-mist mb-1">
                        Repository Name *
                      </label>
                      <input
                        type="text"
                        value={repoName}
                        onChange={(e) => setRepoName(e.target.value)}
                        placeholder="e.g. react"
                        className="w-full px-3 py-1.5 rounded-[6px] bg-void border border-graphite text-caption text-mist focus:outline-none focus:border-mist transition-colors"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-caption font-[510] text-mist mb-1">
                      GitHub Personal Access Token (Optional for public repos)
                    </label>
                    <input
                      type="password"
                      value={githubToken}
                      onChange={(e) => setGithubToken(e.target.value)}
                      placeholder="ghp_..."
                      className="w-full px-3 py-1.5 rounded-[6px] bg-void border border-graphite text-caption text-mist focus:outline-none focus:border-mist transition-colors font-mono"
                    />
                  </div>
                </div>
              ) : (
                <div className="space-y-3 pt-2">
                  <div>
                    <label className="block text-caption font-[510] text-mist mb-1">
                      Budget CSV File *
                    </label>
                    <input
                      type="file"
                      accept=".csv"
                      onChange={(e) => setBudgetFile(e.target.files?.[0] || null)}
                      className="w-full px-3 py-1.5 rounded-[6px] bg-void border border-graphite text-caption text-mist focus:outline-none focus:border-mist transition-colors"
                      required
                    />
                    <p className="text-micro text-fog mt-1">
                      Expected headers: <code className="font-mono text-mist">month, category, planned, actual</code>
                    </p>
                  </div>
                </div>
              )}

              <div className="pt-4 border-t border-graphite flex items-center justify-between">
                <Button
                  variant="ghost"
                  size="sm"
                  type="button"
                  onClick={() => router.push(`/projects/${createdProject.id}`)}
                >
                  Skip for Now
                </Button>

                <Button variant="primary" size="md" type="submit" isLoading={isLoading}>
                  <Sparkles className="w-3.5 h-3.5" />
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

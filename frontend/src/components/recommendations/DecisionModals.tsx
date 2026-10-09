"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { Recommendation } from "@/types";

interface ApproveModalProps {
  isOpen: boolean;
  onClose: () => void;
  recommendation: Recommendation | null;
  onConfirm: (recId: string, owner?: string, dueDate?: string) => Promise<void>;
}

export function ApproveModal({ isOpen, onClose, recommendation, onConfirm }: ApproveModalProps) {
  const [owner, setOwner] = useState(recommendation?.suggested_owner || "Project Lead");
  const [dueDate, setDueDate] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!recommendation) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsSubmitting(true);
      await onConfirm(recommendation.id, owner, dueDate || undefined);
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Approve Mitigation Recommendation"
      description="Approving will convert this recommendation into a tracked project action item."
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="p-3 rounded-lg bg-zinc-950/70 border border-zinc-800 text-xs text-zinc-300">
          <span className="font-semibold text-zinc-100 block mb-1">Recommended Action:</span>
          {recommendation.action_description}
        </div>

        <div>
          <label className="block text-xs font-semibold text-zinc-300 mb-1">
            Assignee / Action Owner
          </label>
          <input
            type="text"
            value={owner}
            onChange={(e) => setOwner(e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-sm text-zinc-100 focus:outline-none focus:border-indigo-500"
            required
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-zinc-300 mb-1">
            Target Due Date (Optional)
          </label>
          <input
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-sm text-zinc-100 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="flex items-center justify-end gap-2 pt-4 border-t border-zinc-800">
          <Button variant="outline" size="sm" type="button" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="primary" size="sm" type="submit" isLoading={isSubmitting}>
            Confirm & Create Action
          </Button>
        </div>
      </form>
    </Modal>
  );
}

interface ModifyModalProps {
  isOpen: boolean;
  onClose: () => void;
  recommendation: Recommendation | null;
  onConfirm: (
    recId: string,
    actionDesc: string,
    owner: string,
    dueDate?: string,
    reason?: string
  ) => Promise<void>;
}

export function ModifyModal({ isOpen, onClose, recommendation, onConfirm }: ModifyModalProps) {
  const [actionDesc, setActionDesc] = useState(recommendation?.action_description || "");
  const [owner, setOwner] = useState(recommendation?.suggested_owner || "Project Lead");
  const [dueDate, setDueDate] = useState("");
  const [reason, setReason] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  React.useEffect(() => {
    if (recommendation) {
      setActionDesc(recommendation.action_description);
      setOwner(recommendation.suggested_owner || "Project Lead");
    }
  }, [recommendation]);

  if (!recommendation) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsSubmitting(true);
      await onConfirm(recommendation.id, actionDesc, owner, dueDate || undefined, reason);
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Modify & Approve Action"
      description="Adjust the mitigation scope or assignee to fit current team capacity."
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-zinc-300 mb-1">
            Action Description
          </label>
          <textarea
            value={actionDesc}
            onChange={(e) => setActionDesc(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-sm text-zinc-100 focus:outline-none focus:border-indigo-500"
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-semibold text-zinc-300 mb-1">Action Owner</label>
            <input
              type="text"
              value={owner}
              onChange={(e) => setOwner(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-sm text-zinc-100 focus:outline-none focus:border-indigo-500"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-zinc-300 mb-1">Due Date</label>
            <input
              type="date"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-sm text-zinc-100 focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-zinc-300 mb-1">
            Modification Reason (Audit Trail)
          </label>
          <input
            type="text"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="e.g. Scoped down requirements to maintain sprint velocity"
            className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-sm text-zinc-100 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="flex items-center justify-end gap-2 pt-4 border-t border-zinc-800">
          <Button variant="outline" size="sm" type="button" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="primary" size="sm" type="submit" isLoading={isSubmitting}>
            Save & Create Action
          </Button>
        </div>
      </form>
    </Modal>
  );
}

interface DismissModalProps {
  isOpen: boolean;
  onClose: () => void;
  recommendation: Recommendation | null;
  onConfirm: (recId: string, reason: string) => Promise<void>;
}

export function DismissModal({ isOpen, onClose, recommendation, onConfirm }: DismissModalProps) {
  const [reason, setReason] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!recommendation) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reason.trim()) return;
    try {
      setIsSubmitting(true);
      await onConfirm(recommendation.id, reason);
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Dismiss Recommendation"
      description="Dismissing helps RiskZen learn your team's decision criteria and improves future suggestions."
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-zinc-300 mb-1">
            Dismissal Justification (Required for Audit Trail)
          </label>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            rows={3}
            placeholder="e.g. Risk was already accepted by leadership during sprint planning"
            className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-sm text-zinc-100 focus:outline-none focus:border-indigo-500"
            required
          />
        </div>

        <div className="flex items-center justify-end gap-2 pt-4 border-t border-zinc-800">
          <Button variant="outline" size="sm" type="button" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="danger" size="sm" type="submit" isLoading={isSubmitting}>
            Confirm Dismissal
          </Button>
        </div>
      </form>
    </Modal>
  );
}

interface SnoozeModalProps {
  isOpen: boolean;
  onClose: () => void;
  recommendation: Recommendation | null;
  onConfirm: (recId: string, hours: number, reason?: string) => Promise<void>;
}

export function SnoozeModal({ isOpen, onClose, recommendation, onConfirm }: SnoozeModalProps) {
  const [hours, setHours] = useState(24);
  const [reason, setReason] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!recommendation) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsSubmitting(true);
      await onConfirm(recommendation.id, hours, reason || undefined);
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Snooze Recommendation Alert"
      description="Temporarily pause alert notifications while ongoing mitigation is in flight."
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-zinc-300 mb-1">Snooze Duration</label>
          <select
            value={hours}
            onChange={(e) => setHours(Number(e.target.value))}
            className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-sm text-zinc-100 focus:outline-none focus:border-indigo-500"
          >
            <option value={24}>24 Hours (1 Day)</option>
            <option value={48}>48 Hours (2 Days)</option>
            <option value={72}>72 Hours (3 Days)</option>
            <option value={168}>1 Week (7 Days)</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-zinc-300 mb-1">
            Reason / Context
          </label>
          <input
            type="text"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="e.g. Waiting on vendor API key resolution"
            className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-sm text-zinc-100 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="flex items-center justify-end gap-2 pt-4 border-t border-zinc-800">
          <Button variant="outline" size="sm" type="button" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="primary" size="sm" type="submit" isLoading={isSubmitting}>
            Confirm Snooze
          </Button>
        </div>
      </form>
    </Modal>
  );
}

interface OutcomeModalProps {
  isOpen: boolean;
  onClose: () => void;
  riskId: string;
  onConfirm: (
    riskId: string,
    result: "yes" | "partially" | "no" | "not_sure",
    comment?: string
  ) => Promise<void>;
}

export function OutcomeModal({ isOpen, onClose, riskId, onConfirm }: OutcomeModalProps) {
  const [result, setResult] = useState<"yes" | "partially" | "no" | "not_sure">("yes");
  const [comment, setComment] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsSubmitting(true);
      await onConfirm(riskId, result, comment || undefined);
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Record Risk Mitigation Outcome"
      description="Help RiskZen measure prediction precision: was the delivery risk successfully prevented?"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-zinc-300 mb-2">
            Was the delivery slip or threat successfully mitigated?
          </label>
          <div className="grid grid-cols-2 gap-2">
            {[
              { id: "yes", label: "Yes, fully mitigated" },
              { id: "partially", label: "Partially mitigated" },
              { id: "no", label: "No, delay occurred" },
              { id: "not_sure", label: "Not sure / Inconclusive" },
            ].map((opt) => (
              <button
                key={opt.id}
                type="button"
                onClick={() => setResult(opt.id as any)}
                className={`p-3 rounded-lg border text-xs font-medium text-left transition-all ${
                  result === opt.id
                    ? "bg-indigo-600/20 border-indigo-500 text-indigo-300 font-semibold"
                    : "bg-zinc-950 border-zinc-800 text-zinc-400 hover:border-zinc-700"
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-zinc-300 mb-1">
            Outcome Comment (Optional)
          </label>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            rows={2}
            placeholder="e.g. Action unblocked 3 tickets and sprint landed on time."
            className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-sm text-zinc-100 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="flex items-center justify-end gap-2 pt-4 border-t border-zinc-800">
          <Button variant="outline" size="sm" type="button" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="primary" size="sm" type="submit" isLoading={isSubmitting}>
            Record Outcome
          </Button>
        </div>
      </form>
    </Modal>
  );
}

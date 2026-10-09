import React, { useEffect } from "react";
import { X } from "@/components/icons";
import { cn } from "@/lib/utils";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  maxWidth?: "sm" | "md" | "lg" | "xl";
}

export function Modal({
  isOpen,
  onClose,
  title,
  description,
  children,
  footer,
  maxWidth = "md",
}: ModalProps) {
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    if (isOpen) {
      document.body.style.overflow = "hidden";
      window.addEventListener("keydown", handleKeyDown);
    }
    return () => {
      document.body.style.overflow = "unset";
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const widthClasses = {
    sm: "max-w-md",
    md: "max-w-lg",
    lg: "max-w-2xl",
    xl: "max-w-4xl",
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-void/85 backdrop-blur-[2px] transition-opacity"
        onClick={onClose}
      />

      {/* Modal Dialog */}
      <div
        className={cn(
          "relative w-full rounded-[12px] border border-graphite bg-carbon p-6 text-mist shadow-xl z-10 animate-fade-in",
          widthClasses[maxWidth]
        )}
      >
        <div className="flex items-start justify-between gap-4 mb-4">
          <div>
            <h2 className="text-body-lg font-[510] text-paper tracking-[-0.012em]">{title}</h2>
            {description && <p className="text-caption text-fog mt-0.5">{description}</p>}
          </div>
          <button
            onClick={onClose}
            className="rounded-[6px] p-1 text-fog hover:bg-graphite hover:text-paper transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="py-2 text-caption text-mist">{children}</div>

        {footer && (
          <div className="mt-6 flex items-center justify-end gap-2.5 pt-4 border-t border-graphite">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}

import React from "react";
import { cn } from "@/lib/utils";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "danger" | "ghost" | "pill" | "white";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
}

export function Button({
  children,
  variant = "primary",
  size = "md",
  isLoading = false,
  className,
  disabled,
  ...props
}: ButtonProps) {
  const variants = {
    // Acid Lime primary action - High emphasis flashlight CTA
    primary:
      "bg-acid-lime text-void font-[510] hover:brightness-105 active:brightness-95 shadow-[0px_1px_2px_rgba(0,0,0,0.4)]",
    // White high-contrast pill/button
    white:
      "bg-paper text-void font-[510] hover:bg-bone active:bg-mist shadow-sm",
    // Neutral Carbon surface
    secondary:
      "bg-obsidian hover:bg-graphite text-mist border border-graphite active:border-smoke",
    // Hairline outline
    outline:
      "bg-transparent hover:bg-[rgba(255,255,255,0.03)] text-mist border border-graphite hover:border-smoke",
    // Danger coral red
    danger:
      "bg-[rgba(235,87,87,0.12)] text-coral-red border border-[rgba(235,87,87,0.30)] hover:bg-[rgba(235,87,87,0.20)]",
    // Ghost
    ghost:
      "bg-transparent hover:bg-[rgba(255,255,255,0.04)] text-fog hover:text-mist",
    // Compact tag / pill button
    pill:
      "bg-[rgba(255,255,255,0.05)] text-mist hover:bg-[rgba(255,255,255,0.08)] rounded-full border border-transparent",
  };

  const sizes = {
    sm: "px-2.5 py-1 text-label rounded-[6px] gap-1.5",
    md: "px-3.5 py-1.5 text-caption rounded-[6px] gap-2",
    lg: "px-4 py-2.5 text-body-sm font-[510] rounded-[6px] gap-2.5",
  };

  const isPill = variant === "pill";

  return (
    <button
      className={cn(
        "inline-flex items-center justify-center transition-colors duration-150 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed select-none tracking-[-0.011em]",
        variants[variant],
        sizes[size],
        isPill && "rounded-full",
        className
      )}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin" />
      ) : null}
      {children}
    </button>
  );
}

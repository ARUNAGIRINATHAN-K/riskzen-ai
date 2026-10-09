import React from "react";
import { cn } from "@/lib/utils";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "danger" | "ghost" | "gradient";
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
    primary:
      "bg-indigo-600 hover:bg-indigo-500 text-white shadow-sm shadow-indigo-500/20 active:translate-y-px",
    gradient:
      "bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 hover:opacity-95 text-white shadow-md shadow-indigo-500/20 active:translate-y-px",
    secondary:
      "bg-zinc-800 hover:bg-zinc-700 text-zinc-100 border border-zinc-700/60 active:translate-y-px",
    outline:
      "bg-transparent hover:bg-zinc-800/60 text-zinc-300 border border-zinc-700 hover:border-zinc-500 active:translate-y-px",
    danger:
      "bg-rose-600/90 hover:bg-rose-500 text-white shadow-sm shadow-rose-900/30 active:translate-y-px",
    ghost: "bg-transparent hover:bg-zinc-800/60 text-zinc-400 hover:text-zinc-200",
  };

  const sizes = {
    sm: "px-2.5 py-1.5 text-xs rounded-lg gap-1.5",
    md: "px-3.5 py-2 text-sm rounded-lg gap-2",
    lg: "px-5 py-2.5 text-base rounded-xl gap-2.5 font-medium",
  };

  return (
    <button
      className={cn(
        "inline-flex items-center justify-center font-medium transition-all duration-150 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed select-none",
        variants[variant],
        sizes[size],
        className
      )}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
      ) : null}
      {children}
    </button>
  );
}

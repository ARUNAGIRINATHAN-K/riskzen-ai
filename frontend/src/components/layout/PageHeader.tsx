import React from "react";
import Link from "next/link";
import { ChevronRight } from "@/components/icons";

interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  breadcrumbs?: BreadcrumbItem[];
  actions?: React.ReactNode;
}

export function PageHeader({ title, subtitle, breadcrumbs, actions }: PageHeaderProps) {
  return (
    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-6 mb-6 border-b border-zinc-800/80">
      <div>
        {breadcrumbs && breadcrumbs.length > 0 && (
          <nav className="flex items-center gap-1.5 text-xs text-zinc-400 mb-2">
            {breadcrumbs.map((b, i) => (
              <React.Fragment key={i}>
                {i > 0 && <ChevronRight className="w-3.5 h-3.5 text-zinc-600" />}
                {b.href ? (
                  <Link href={b.href} className="hover:text-zinc-200 transition-colors">
                    {b.label}
                  </Link>
                ) : (
                  <span className="text-zinc-200 font-medium">{b.label}</span>
                )}
              </React.Fragment>
            ))}
          </nav>
        )}
        <h1 className="text-2xl font-bold tracking-tight text-white">{title}</h1>
        {subtitle && <p className="text-xs text-zinc-400 mt-1 max-w-2xl">{subtitle}</p>}
      </div>
      {actions && <div className="flex items-center gap-3 shrink-0">{actions}</div>}
    </div>
  );
}

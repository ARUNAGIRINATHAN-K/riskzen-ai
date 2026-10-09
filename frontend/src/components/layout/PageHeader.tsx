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
    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-5 mb-6 border-b border-graphite">
      <div>
        {breadcrumbs && breadcrumbs.length > 0 && (
          <nav className="flex items-center gap-1.5 text-caption text-ash mb-2 select-none">
            {breadcrumbs.map((b, i) => (
              <React.Fragment key={i}>
                {i > 0 && <ChevronRight className="w-3.5 h-3.5 text-ash/60" />}
                {b.href ? (
                  <Link href={b.href} className="hover:text-mist transition-colors">
                    {b.label}
                  </Link>
                ) : (
                  <span className="text-mist font-normal">{b.label}</span>
                )}
              </React.Fragment>
            ))}
          </nav>
        )}
        <h1 className="text-subheading font-[510] tracking-[-0.288px] text-paper">{title}</h1>
        {subtitle && <p className="text-caption text-fog mt-1 max-w-2xl">{subtitle}</p>}
      </div>
      {actions && <div className="flex items-center gap-2 shrink-0">{actions}</div>}
    </div>
  );
}

import type { ReactNode } from "react";
import { Card, SectionHeader } from "../ui";

interface DomainResultsPanelProps {
  title: string;
  subtitle: string;
  icon: ReactNode;
  action?: ReactNode;
  /** When true, render a bordered header with a separate scrollable body (microscope / infrared style). */
  headerBorder?: boolean;
  children: ReactNode;
}

/** Center results panel: header plus scrollable content area. */
export function DomainResultsPanel({
  title,
  subtitle,
  icon,
  action,
  headerBorder = false,
  children,
}: DomainResultsPanelProps) {
  if (headerBorder) {
    return (
      <Card padding="none" className="overflow-hidden h-full flex flex-col">
        <div className="p-4 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
          <SectionHeader title={title} subtitle={subtitle} icon={icon} />
          {action}
        </div>
        <div className="flex-1 overflow-y-auto p-3 space-y-3">
          {children}
        </div>
      </Card>
    );
  }

  return (
    <Card padding="none" className="overflow-hidden h-full flex flex-col">
      <div className="p-4 flex-1 flex flex-col">
        <SectionHeader title={title} subtitle={subtitle} icon={icon} action={action} />
        {children}
      </div>
    </Card>
  );
}

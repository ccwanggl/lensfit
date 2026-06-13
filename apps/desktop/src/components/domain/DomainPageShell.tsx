import type { ReactNode } from "react";

interface DomainPageShellProps {
  left: ReactNode;
  center: ReactNode;
  right: ReactNode;
}

/** Three-column layout shared by all domain pages (3 / 5 / 4). */
export function DomainPageShell({ left, center, right }: DomainPageShellProps) {
  return (
    <div className="grid grid-cols-12 gap-5">
      <div className="col-span-3">{left}</div>
      <div className="col-span-5">{center}</div>
      <div className="col-span-4">{right}</div>
    </div>
  );
}

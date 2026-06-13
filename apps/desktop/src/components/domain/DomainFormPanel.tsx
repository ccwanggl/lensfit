import type { ReactNode, FormEvent } from "react";
import { Card, Button, SectionHeader, ProgressBar } from "../ui";
import PresetSelector from "../PresetSelector";
import type { PresetConfigItem } from "../../utils/api";

export type Domain = "industrial" | "photography" | "microscope" | "infrared";

interface DomainFormPanelProps {
  title: string;
  subtitle: string;
  icon: ReactNode;
  domain: Domain;
  onPresetSelect: (preset: PresetConfigItem) => void;
  onSubmit: (e: FormEvent) => void;
  isLoading: boolean;
  submitText?: string;
  loadingText?: string;
  progress?: number;
  stage?: string;
  submitIcon?: ReactNode;
  children: ReactNode;
}

/** Left-hand parameter panel: header, preset selector, form fields, submit button and progress. */
export function DomainFormPanel({
  title,
  subtitle,
  icon,
  domain,
  onPresetSelect,
  onSubmit,
  isLoading,
  submitText = "自动匹配",
  loadingText = "计算中...",
  progress,
  stage,
  submitIcon,
  children,
}: DomainFormPanelProps) {
  return (
    <Card padding="none" className="overflow-hidden">
      <div className="p-6">
        <SectionHeader title={title} subtitle={subtitle} icon={icon} />
        <div className="mb-4">
          <PresetSelector domain={domain} onSelect={onPresetSelect} />
        </div>
        <form onSubmit={onSubmit} className="space-y-4">
          {children}
          <div className="pt-2">
            <Button
              type="submit"
              variant="primary"
              size="lg"
              loading={isLoading}
              leftIcon={submitIcon}
              className="w-full"
            >
              {isLoading ? loadingText : submitText}
            </Button>
          </div>
          {isLoading && progress !== undefined && (
            <div className="space-y-2 pt-1">
              <ProgressBar
                value={progress}
                color="indigo"
                label={stage || "准备中"}
                showValue
              />
            </div>
          )}
        </form>
      </div>
    </Card>
  );
}

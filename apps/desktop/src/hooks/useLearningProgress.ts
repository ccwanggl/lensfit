import { useState, useEffect, useCallback } from "react";

/**
 * 四领域工作台内部的章节/测验勾选状态（localStorage）。
 *
 * 边界决策见 docs/development/specifications/lab/learning-records.md §6：
 * 本 hook 的键空间与学习路径 item 命名空间不重叠，明确不迁移；
 * 学习路径相关进度一律走 /api/v1/learning/progress（见 lab/reportProgress.ts）。
 */

export type Domain = "photography" | "microscope" | "infrared" | "industrial";

export interface DomainProgress {
  sectionsViewed: string[];
  quizzesCompleted: string[];
  quizScores: Record<string, number>;
}

interface StoredProgress {
  version: number;
  domains: Record<Domain, DomainProgress>;
}

const STORAGE_KEY = "optibench-learning-progress";
const CURRENT_VERSION = 1;

function getInitialDomainProgress(): DomainProgress {
  return {
    sectionsViewed: [],
    quizzesCompleted: [],
    quizScores: {},
  };
}

function readStored(): StoredProgress {
  try {
    // Fallback to the legacy LensFit-era key so existing progress is kept.
    const raw =
      localStorage.getItem(STORAGE_KEY) ?? localStorage.getItem("lensfit-learning-progress");
    if (!raw) return { version: CURRENT_VERSION, domains: { photography: getInitialDomainProgress(), microscope: getInitialDomainProgress(), infrared: getInitialDomainProgress(), industrial: getInitialDomainProgress() } };
    const parsed = JSON.parse(raw) as StoredProgress;
    if (!parsed.domains) throw new Error("Invalid progress");
    // Ensure all domains exist
    const domains = { photography: getInitialDomainProgress(), microscope: getInitialDomainProgress(), infrared: getInitialDomainProgress(), industrial: getInitialDomainProgress() };
    for (const d of Object.keys(domains) as Domain[]) {
      if (parsed.domains[d]) {
        domains[d] = {
          ...getInitialDomainProgress(),
          ...parsed.domains[d],
          quizScores: parsed.domains[d].quizScores || {},
        };
      }
    }
    return { version: parsed.version || CURRENT_VERSION, domains };
  } catch {
    return { version: CURRENT_VERSION, domains: { photography: getInitialDomainProgress(), microscope: getInitialDomainProgress(), infrared: getInitialDomainProgress(), industrial: getInitialDomainProgress() } };
  }
}

function writeStored(progress: StoredProgress) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
  } catch {
    // ignore storage errors
  }
}

export function useLearningProgress() {
  const [progress, setProgress] = useState<StoredProgress>(() => readStored());

  useEffect(() => {
    writeStored(progress);
  }, [progress]);

  const getDomainProgress = useCallback((domain: Domain): DomainProgress => {
    return progress.domains[domain] ?? getInitialDomainProgress();
  }, [progress]);

  const markSectionViewed = useCallback((domain: Domain, sectionId: string) => {
    setProgress((prev) => {
      const current = prev.domains[domain] ?? getInitialDomainProgress();
      if (current.sectionsViewed.includes(sectionId)) return prev;
      return {
        ...prev,
        domains: {
          ...prev.domains,
          [domain]: {
            ...current,
            sectionsViewed: [...current.sectionsViewed, sectionId],
          },
        },
      };
    });
  }, []);

  const markQuizCompleted = useCallback((domain: Domain, quizId: string, score: number) => {
    setProgress((prev) => {
      const current = prev.domains[domain] ?? getInitialDomainProgress();
      return {
        ...prev,
        domains: {
          ...prev.domains,
          [domain]: {
            ...current,
            quizzesCompleted: current.quizzesCompleted.includes(quizId)
              ? current.quizzesCompleted
              : [...current.quizzesCompleted, quizId],
            quizScores: { ...current.quizScores, [quizId]: score },
          },
        },
      };
    });
  }, []);

  const resetDomainProgress = useCallback((domain: Domain) => {
    setProgress((prev) => ({
      ...prev,
      domains: {
        ...prev.domains,
        [domain]: getInitialDomainProgress(),
      },
    }));
  }, []);

  return {
    progress,
    getDomainProgress,
    markSectionViewed,
    markQuizCompleted,
    resetDomainProgress,
  };
}

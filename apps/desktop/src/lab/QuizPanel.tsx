import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, Loader2 } from "lucide-react";
import LearningQuiz, { type QuizQuestion } from "../components/LearningQuiz";
import { getContentQuiz } from "../utils/api";
import { useReportProgress } from "./reportProgress";

/**
 * Fetch a quiz by id and render the shared LearningQuiz component.
 * On completion the percentage score is reported as a scored
 * learning-record (item_kind="assessment"), which the curriculum graph
 * merges as "completed".
 */
export default function QuizPanel({ quizId }: { quizId: string }) {
  const reportProgress = useReportProgress();
  const { data, isLoading, error } = useQuery({
    queryKey: ["content-quiz", quizId],
    queryFn: () => getContentQuiz(quizId),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-6">
        <Loader2 className="animate-spin text-indigo-500" size={24} />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-400">
        <AlertTriangle size={14} />
        无法加载测验：{error?.message ?? "未找到测验"}
      </div>
    );
  }

  const questions: QuizQuestion[] = data.questions.map((q) => ({
    question: q.question,
    options: q.options,
    correctIndex: q.correct_index,
    explanation: q.explanation ?? "",
  }));

  return (
    <LearningQuiz
      title={data.title}
      questions={questions}
      quizId={data.id}
      onComplete={(score) => {
        const percentage = Math.round((score / questions.length) * 100);
        reportProgress("assessment", data.id, "scored", percentage);
      }}
    />
  );
}

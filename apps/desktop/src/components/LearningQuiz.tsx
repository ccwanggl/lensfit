import { useState, useCallback } from "react";
import { CheckCircle2, XCircle, HelpCircle, RotateCcw, Trophy } from "lucide-react";

export interface QuizQuestion {
  question: string;
  options: string[];
  correctIndex: number;
  explanation: string;
}

interface LearningQuizProps {
  title: string;
  questions: QuizQuestion[];
  quizId: string;
  onComplete?: (score: number) => void;
}

export default function LearningQuiz({ title, questions, onComplete }: LearningQuizProps) {
  const [current, setCurrent] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [showResult, setShowResult] = useState(false);
  const [score, setScore] = useState(0);
  const [completed, setCompleted] = useState(false);

  const handleAnswer = useCallback((index: number) => {
    if (showResult || completed) return;
    setSelected(index);
    setShowResult(true);
    if (index === questions[current].correctIndex) {
      setScore((s) => s + 1);
    }
  }, [current, questions, showResult, completed]);

  const handleNext = useCallback(() => {
    if (completed) return;
    if (current + 1 >= questions.length) {
      setCompleted(true);
      onComplete?.(score);
    } else {
      setCurrent((c) => c + 1);
      setSelected(null);
      setShowResult(false);
    }
  }, [current, questions, score, completed, onComplete]);

  const handleRetry = useCallback(() => {
    setCurrent(0);
    setSelected(null);
    setShowResult(false);
    setScore(0);
    setCompleted(false);
  }, []);

  if (completed) {
    const percentage = Math.round((score / questions.length) * 100);
    return (
      <div className="p-5 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-sm text-center space-y-4">
        <div className="w-14 h-14 rounded-full bg-amber-50 dark:bg-amber-900/20 border border-amber-100 dark:border-amber-800/30 flex items-center justify-center mx-auto text-amber-500">
          <Trophy size={28} />
        </div>
        <h4 className="text-sm font-bold text-slate-800 dark:text-slate-100">{title} 完成</h4>
        <p className="text-2xl font-extrabold text-indigo-600 dark:text-indigo-400">
          {score} / {questions.length}
        </p>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          {percentage >= 80 ? "太棒了！你对这些概念掌握得很好。" : percentage >= 50 ? "不错的开始，可以再复习一下相关章节。" : "建议重新浏览学习指南后再试一次。"}
        </p>
        <button
          onClick={handleRetry}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
        >
          <RotateCcw size={13} />
          重新测验
        </button>
      </div>
    );
  }

  const q = questions[current];
  const isCorrect = selected === q.correctIndex;

  return (
    <div className="p-4 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
          <HelpCircle size={14} className="text-indigo-500" />
          {title}
        </h4>
        <span className="text-xs font-semibold text-slate-400 dark:text-slate-500">
          {current + 1} / {questions.length}
        </span>
      </div>

      <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">{q.question}</p>

      <div className="space-y-2">
        {q.options.map((opt, i) => {
          const answered = showResult && selected === i;
          const isCorrectOption = showResult && i === q.correctIndex;
          const base = "w-full text-left px-3 py-2.5 rounded-lg text-xs font-medium border transition-colors focus-ring";
          const idle = "bg-slate-50 dark:bg-slate-800/60 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700";
          const correct = "bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800/30 text-emerald-700 dark:text-emerald-400";
          const wrong = "bg-rose-50 dark:bg-rose-900/20 border-rose-200 dark:border-rose-800/30 text-rose-700 dark:text-rose-400";
          const cls = showResult
            ? isCorrectOption
              ? correct
              : answered
              ? wrong
              : idle
            : idle;
          return (
            <button
              key={i}
              disabled={showResult}
              onClick={() => handleAnswer(i)}
              className={`${base} ${cls} flex items-center justify-between`}
            >
              <span>{opt}</span>
              {showResult && isCorrectOption && <CheckCircle2 size={14} />}
              {answered && !isCorrectOption && <XCircle size={14} />}
            </button>
          );
        })}
      </div>

      {showResult && (
        <div className={`p-3 rounded-lg text-xs leading-relaxed ${isCorrect ? "bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-100 dark:border-emerald-800/30 text-emerald-700 dark:text-emerald-400" : "bg-amber-50 dark:bg-amber-900/15 border border-amber-100 dark:border-amber-800/20 text-amber-800 dark:text-amber-300"}`}>
          <span className="font-semibold block mb-0.5">{isCorrect ? "回答正确" : "回答错误"}</span>
          {q.explanation}
        </div>
      )}

      {showResult && (
        <button
          onClick={handleNext}
          className="w-full py-2 rounded-lg text-xs font-semibold bg-indigo-600 text-white hover:bg-indigo-500 transition-colors"
        >
          {current + 1 >= questions.length ? "查看结果" : "下一题"}
        </button>
      )}
    </div>
  );
}

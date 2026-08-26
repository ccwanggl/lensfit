/** Sandbox side/content panels (moved verbatim from LearningHub, slice B). */
import { useMemo, useState } from "react";
import { ExternalLink, Loader2, Play } from "lucide-react";
import { ParameterControl } from "../ParameterControl";
import { getExperimentMedia } from "../experimentMedia";
import type { LabExperiment } from "../../utils/api";

export function ParameterPanel({
  experiment,
  params,
  onChange,
  onReset,
  isFetching,
  isPreset,
  sceneError,
}: {
  experiment: LabExperiment;
  params: Record<string, unknown>;
  onChange: (name: string, value: unknown) => void;
  onReset: () => void;
  isFetching: boolean;
  isPreset: boolean;
  sceneError: string | null;
}) {
  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
          参数控制
        </h3>
        {isFetching && (
          <Loader2 size={14} className="animate-spin text-indigo-500" />
        )}
      </div>
      <div className="min-h-0 flex-1 space-y-3 overflow-auto pr-1">
        {experiment.parameters.map((param) => (
          <ParameterControl
            key={param.name}
            param={param}
            value={params[param.name]}
            onChange={(value) => onChange(param.name, value)}
          />
        ))}
      </div>
      {sceneError && (
        <div className="mt-3 rounded-lg border border-red-200 bg-red-50 p-2 text-xs text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-400">
          {sceneError}
        </div>
      )}
      <button
        onClick={onReset}
        className="mt-3 w-full rounded-lg border border-slate-200 bg-white py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
      >
        {isPreset ? "重置默认布局" : "重置默认参数"}
      </button>
    </div>
  );
}

export function MediaPanel({ experimentId }: { experimentId: string }) {
  const media = useMemo(() => getExperimentMedia(experimentId), [experimentId]);
  const [open, setOpen] = useState(false);

  if (!media) return null;

  return (
    <div className="rounded-xl border border-slate-200/60 bg-slate-50/60 p-3 dark:border-slate-700/60 dark:bg-slate-800/60">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between"
      >
        <span className="flex items-center gap-2 text-xs font-semibold text-slate-700 dark:text-slate-300">
          <Play size={14} className="text-rose-500" />
          实验实操
          {media.caption && (
            <span className="font-normal text-slate-500 dark:text-slate-400">
              · {media.caption}
            </span>
          )}
        </span>
        <span className="text-xs text-indigo-600 dark:text-indigo-400">
          {open ? "收起" : "展开"}
        </span>
      </button>

      {open && (
        <div className="mt-3">
          {media.video?.provider === "youtube" && (
            <div className="relative aspect-video w-full max-h-56 overflow-hidden rounded-lg bg-black">
              <iframe
                className="h-full w-full"
                src={`https://www.youtube-nocookie.com/embed/${media.video.id}${
                  media.video.start ? `?start=${media.video.start}` : ""
                }`}
                title={media.video.title ?? "实验视频"}
                allow="accelerometer; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                loading="lazy"
              />
            </div>
          )}
          {media.image && (
            <div className="relative max-h-56 overflow-hidden rounded-lg">
              <img
                src={media.image.src}
                alt={media.image.alt}
                className="max-h-56 w-full object-contain"
                loading="lazy"
              />
              {media.image.credit && (
                <p className="mt-1 text-xs text-slate-400">
                  来源：{media.image.credit}
                </p>
              )}
            </div>
          )}
          {media.video?.provider === "youtube" && (
            <a
              href={`https://www.youtube.com/watch?v=${media.video.id}`}
              target="_blank"
              rel="noreferrer"
              className="mt-2 inline-flex items-center gap-1 text-xs text-indigo-600 hover:underline dark:text-indigo-400"
            >
              在 YouTube 打开 <ExternalLink size={10} />
            </a>
          )}
        </div>
      )}
    </div>
  );
}

export function DataPanel({ result }: { result?: { data: Record<string, unknown> } }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
      <h4 className="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-300">
        计算数据
      </h4>
      <pre className="max-h-[60vh] overflow-auto text-xs text-slate-600 dark:text-slate-400">
        {result ? JSON.stringify(result.data, null, 2) : "暂无数据"}
      </pre>
    </div>
  );
}

export function HintsPanel({
  result,
}: {
  result?: { warnings: string[]; learning_hints: string[] };
}) {
  return (
    <div className="space-y-3">
      {result?.warnings.length ? (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 dark:border-amber-900 dark:bg-amber-950/30">
          <div className="mb-1 text-sm font-semibold text-amber-800 dark:text-amber-400">
            注意
          </div>
          <ul className="list-inside list-disc text-sm text-amber-700 dark:text-amber-300">
            {result.warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      ) : null}
      {result?.learning_hints.length ? (
        <div className="rounded-lg border border-indigo-200 bg-indigo-50 p-3 dark:border-indigo-900 dark:bg-indigo-950/30">
          <div className="mb-1 text-sm font-semibold text-indigo-800 dark:text-indigo-400">
            学习提示
          </div>
          <ul className="list-inside list-disc text-sm text-indigo-700 dark:text-indigo-300">
            {result.learning_hints.map((h, i) => (
              <li key={i}>{h}</li>
            ))}
          </ul>
        </div>
      ) : (
        <p className="text-sm text-slate-500 dark:text-slate-400">暂无学习提示</p>
      )}
    </div>
  );
}

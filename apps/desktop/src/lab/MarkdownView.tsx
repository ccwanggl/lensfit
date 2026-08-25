import React from "react";

/**
 * Minimal markdown renderer for learning content (content contract v1 bodies).
 *
 * Deliberately small: headings, paragraphs, lists, fenced code, tables,
 * blockquotes, images, links, bold/italic/inline code. Renders to React
 * elements (no dangerouslySetInnerHTML). Math markup ($...$) is shown as
 * plain text — a proper math renderer is out of scope for phase 0.
 */

interface MarkdownViewProps {
  markdown: string;
}

/* ─── Inline parsing ─── */

const INLINE_RE =
  /(!\[[^\]]*\]\([^)]*\)|\[[^\]]*\]\([^)]*\)|\*\*[^*]+\*\*|\*[^*\n]+\*|`[^`]+`)/g;

function renderInline(text: string, keyPrefix: string): React.ReactNode[] {
  const parts = text.split(INLINE_RE);
  return parts.map((part, i) => {
    if (!part) return null;
    const key = `${keyPrefix}-${i}`;

    const image = part.match(/^!\[([^\]]*)\]\(([^)]*)\)$/);
    if (image) {
      return (
        <img
          key={key}
          src={image[2]}
          alt={image[1]}
          className="my-2 max-w-full rounded-lg"
          loading="lazy"
        />
      );
    }
    const link = part.match(/^\[([^\]]*)\]\(([^)]*)\)$/);
    if (link) {
      return (
        <a
          key={key}
          href={link[2]}
          target="_blank"
          rel="noreferrer"
          className="text-indigo-600 hover:underline dark:text-indigo-400"
        >
          {link[1]}
        </a>
      );
    }
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={key} className="font-semibold">
          {part.slice(2, -2)}
        </strong>
      );
    }
    if (part.startsWith("*") && part.endsWith("*") && part.length > 2) {
      return <em key={key}>{part.slice(1, -1)}</em>;
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code
          key={key}
          className="rounded bg-slate-100 px-1 py-0.5 font-mono text-[0.85em] text-slate-800 dark:bg-slate-700 dark:text-slate-200"
        >
          {part.slice(1, -1)}
        </code>
      );
    }
    return <React.Fragment key={key}>{part}</React.Fragment>;
  });
}

/* ─── Block parsing ─── */

function isTableSeparator(line: string): boolean {
  return /^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?\s*$/.test(line);
}

function splitTableRow(line: string): string[] {
  const trimmed = line.trim().replace(/^\|/, "").replace(/\|$/, "");
  return trimmed.split("|").map((c) => c.trim());
}

const HEADING_CLASSES: Record<number, string> = {
  1: "mt-4 mb-2 text-2xl font-bold",
  2: "mt-4 mb-2 text-xl font-bold",
  3: "mt-4 mb-2 text-lg font-semibold",
  4: "mt-3 mb-1.5 text-base font-semibold",
};

export function MarkdownView({ markdown }: MarkdownViewProps) {
  const lines = markdown.split("\n");
  const blocks: React.ReactNode[] = [];
  let i = 0;
  let blockKey = 0;
  const nextKey = () => `b${blockKey++}`;

  while (i < lines.length) {
    const line = lines[i];

    // Fenced code block
    if (line.trimStart().startsWith("```")) {
      const buf: string[] = [];
      i++;
      while (i < lines.length && !lines[i].trimStart().startsWith("```")) {
        buf.push(lines[i]);
        i++;
      }
      i++; // closing fence
      blocks.push(
        <pre
          key={nextKey()}
          className="my-3 overflow-auto rounded-lg bg-slate-100 p-3 font-mono text-xs text-slate-800 dark:bg-slate-900 dark:text-slate-200"
        >
          {buf.join("\n")}
        </pre>
      );
      continue;
    }

    // Blank line
    if (!line.trim()) {
      i++;
      continue;
    }

    // Heading
    const heading = line.match(/^(#{1,4})\s+(.*)$/);
    if (heading) {
      const level = heading[1].length;
      const cls = `${HEADING_CLASSES[level]} text-slate-900 dark:text-slate-100`;
      const children = renderInline(heading[2], nextKey());
      if (level === 1) blocks.push(<h1 key={nextKey()} className={cls}>{children}</h1>);
      else if (level === 2) blocks.push(<h2 key={nextKey()} className={cls}>{children}</h2>);
      else if (level === 3) blocks.push(<h3 key={nextKey()} className={cls}>{children}</h3>);
      else blocks.push(<h4 key={nextKey()} className={cls}>{children}</h4>);
      i++;
      continue;
    }

    // Horizontal rule
    if (/^\s*(-{3,}|\*{3,})\s*$/.test(line)) {
      blocks.push(
        <hr key={nextKey()} className="my-4 border-slate-200 dark:border-slate-700" />
      );
      i++;
      continue;
    }

    // Table: header row + separator row
    if (line.includes("|") && i + 1 < lines.length && isTableSeparator(lines[i + 1])) {
      const header = splitTableRow(line);
      i += 2;
      const rows: string[][] = [];
      while (i < lines.length && lines[i].includes("|") && lines[i].trim()) {
        rows.push(splitTableRow(lines[i]));
        i++;
      }
      const key = nextKey();
      blocks.push(
        <div key={key} className="my-3 overflow-x-auto">
          <table className="min-w-full border-collapse text-sm">
            <thead>
              <tr>
                {header.map((cell, c) => (
                  <th
                    key={`${key}-h${c}`}
                    className="border border-slate-200 bg-slate-50 px-3 py-1.5 text-left font-semibold text-slate-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300"
                  >
                    {renderInline(cell, `${key}-h${c}`)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, r) => (
                <tr key={`${key}-r${r}`}>
                  {row.map((cell, c) => (
                    <td
                      key={`${key}-r${r}c${c}`}
                      className="border border-slate-200 px-3 py-1.5 text-slate-600 dark:border-slate-700 dark:text-slate-400"
                    >
                      {renderInline(cell, `${key}-r${r}c${c}`)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
      continue;
    }

    // Blockquote
    if (line.trimStart().startsWith(">")) {
      const buf: string[] = [];
      while (i < lines.length && lines[i].trimStart().startsWith(">")) {
        buf.push(lines[i].trimStart().replace(/^>\s?/, ""));
        i++;
      }
      blocks.push(
        <blockquote
          key={nextKey()}
          className="my-3 border-l-4 border-indigo-200 pl-3 text-sm text-slate-500 dark:border-indigo-800 dark:text-slate-400"
        >
          {renderInline(buf.join(" "), nextKey())}
        </blockquote>
      );
      continue;
    }

    // Lists (unordered / ordered)
    const listMatch = line.match(/^\s*(?:[-*+]|\d+[.)])\s+/);
    if (listMatch) {
      const ordered = /^\s*\d/.test(line);
      const items: string[] = [];
      while (i < lines.length && /^\s*(?:[-*+]|\d+[.)])\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*(?:[-*+]|\d+[.)])\s+/, ""));
        i++;
      }
      const key = nextKey();
      const cls = "my-2 list-inside space-y-1 text-sm text-slate-700 dark:text-slate-300";
      const children = items.map((item, n) => (
        <li key={`${key}-i${n}`}>{renderInline(item, `${key}-i${n}`)}</li>
      ));
      blocks.push(
        ordered ? (
          <ol key={key} className={`${cls} list-decimal`}>
            {children}
          </ol>
        ) : (
          <ul key={key} className={`${cls} list-disc`}>
            {children}
          </ul>
        )
      );
      continue;
    }

    // Paragraph: consume until blank line or next block starter
    const buf: string[] = [line];
    i++;
    while (
      i < lines.length &&
      lines[i].trim() &&
      !lines[i].trimStart().startsWith("```") &&
      !/^(#{1,4})\s/.test(lines[i]) &&
      !/^\s*(?:[-*+]|\d+[.)])\s+/.test(lines[i]) &&
      !lines[i].trimStart().startsWith(">") &&
      !(lines[i].includes("|") && i + 1 < lines.length && isTableSeparator(lines[i + 1]))
    ) {
      buf.push(lines[i]);
      i++;
    }
    blocks.push(
      <p
        key={nextKey()}
        className="my-2 text-sm leading-6 text-slate-700 dark:text-slate-300"
      >
        {renderInline(buf.join("\n"), nextKey())}
      </p>
    );
  }

  return <div className="max-w-none">{blocks}</div>;
}

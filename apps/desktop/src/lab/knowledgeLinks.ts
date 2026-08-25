import knowledgeLinksJson from "./knowledgeLinks.json";

export interface LinkEntry {
  path: string;
  title: string;
}

const conceptTable = knowledgeLinksJson.concepts as Record<string, LinkEntry>;
const formulaTable = knowledgeLinksJson.formulas as Record<string, LinkEntry>;

export function conceptLink(slug: string): LinkEntry | undefined {
  return conceptTable[slug];
}

export function formulaLink(slug: string): LinkEntry | undefined {
  return formulaTable[slug];
}

export function obsidianUrlFor(
  entry: LinkEntry | undefined,
  slug: string
): string {
  return `obsidian://open?vault=OpticKnowledgeSpace&file=${encodeURIComponent(
    entry?.path ?? slug
  )}`;
}

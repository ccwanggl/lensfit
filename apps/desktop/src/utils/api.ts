/**
 * Aggregate re-export of the domain API modules in `src/api/`.
 *
 * @deprecated New code should import directly from `src/api/<domain>`
 * (e.g. `import { listLenses } from "../api/catalog"`). This file exists
 * only so existing call sites keep working unchanged (slice A of the
 * frontend megafile refactor plan); it will be removed once call sites
 * have migrated.
 */

export { ApiError } from "../api/client";
export * from "../api/types";
export * from "../api/domains";
export * from "../api/matching";
export * from "../api/visualization";
export * from "../api/catalog";
export * from "../api/projects";
export * from "../api/export";
export * from "../api/knowledge";
export * from "../api/lab";
export * from "../api/content";
export * from "../api/curriculum";
export * from "../api/learning";

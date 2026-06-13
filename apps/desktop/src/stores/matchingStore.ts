import { useMemo } from "react";
import { create } from "zustand";
import type { UnifiedMatchResult } from "../hooks/useMatching";
import type { CatalogLens, CatalogDetector } from "../utils/api";
import type { Domain, RightTab } from "../components/domain";

interface DomainCatalogs {
  lensMap: Map<number, CatalogLens>;
  detMap: Map<number, CatalogDetector>;
}

interface DomainMatchingState {
  hasSearched: boolean;
  results: UnifiedMatchResult[];
  selectedResult: UnifiedMatchResult | null;
  rightTab: RightTab;
  catalogs: DomainCatalogs;
}

type MatchingState = Record<Domain, DomainMatchingState>;

interface MatchingStore {
  state: MatchingState;
  setResults: (domain: Domain, results: UnifiedMatchResult[], selectedResult?: UnifiedMatchResult | null) => void;
  setSelectedResult: (domain: Domain, result: UnifiedMatchResult | null) => void;
  setHasSearched: (domain: Domain, hasSearched: boolean) => void;
  setRightTab: (domain: Domain, tab: RightTab) => void;
  setCatalogs: (domain: Domain, catalogs: Partial<DomainCatalogs>) => void;
  clearDomain: (domain: Domain) => void;
}

const INITIAL_CATALOGS: DomainCatalogs = {
  lensMap: new Map(),
  detMap: new Map(),
};

const INITIAL_DOMAIN_STATE: DomainMatchingState = {
  hasSearched: false,
  results: [],
  selectedResult: null,
  rightTab: "viz",
  catalogs: INITIAL_CATALOGS,
};

const INITIAL_STATE: MatchingState = {
  industrial: { ...INITIAL_DOMAIN_STATE },
  photography: { ...INITIAL_DOMAIN_STATE },
  microscope: { ...INITIAL_DOMAIN_STATE },
  infrared: { ...INITIAL_DOMAIN_STATE },
};

/** Global store for domain-scoped matching results, selection and catalogs. */
export const useMatchingStore = create<MatchingStore>((set) => ({
  state: INITIAL_STATE,

  setResults: (domain, results, selectedResult = results[0] ?? null) =>
    set((store) => ({
      state: {
        ...store.state,
        [domain]: {
          ...store.state[domain],
          results,
          selectedResult,
        },
      },
    })),

  setSelectedResult: (domain, result) =>
    set((store) => ({
      state: {
        ...store.state,
        [domain]: {
          ...store.state[domain],
          selectedResult: result,
        },
      },
    })),

  setHasSearched: (domain, hasSearched) =>
    set((store) => ({
      state: {
        ...store.state,
        [domain]: {
          ...store.state[domain],
          hasSearched,
        },
      },
    })),

  setRightTab: (domain, tab) =>
    set((store) => ({
      state: {
        ...store.state,
        [domain]: {
          ...store.state[domain],
          rightTab: tab,
        },
      },
    })),

  setCatalogs: (domain, catalogs) =>
    set((store) => ({
      state: {
        ...store.state,
        [domain]: {
          ...store.state[domain],
          catalogs: {
            lensMap: catalogs.lensMap ?? store.state[domain].catalogs.lensMap,
            detMap: catalogs.detMap ?? store.state[domain].catalogs.detMap,
          },
        },
      },
    })),

  clearDomain: (domain) =>
    set((store) => ({
      state: {
        ...store.state,
        [domain]: { ...INITIAL_DOMAIN_STATE },
      },
    })),
}));

/** Shorthand selector hook for a single domain's matching state.
 *
 * Uses individual primitive selectors to avoid object-reference churn.
 */
export function useDomainMatchingState(domain: Domain) {
  const hasSearched = useMatchingStore((store) => store.state[domain].hasSearched);
  const results = useMatchingStore((store) => store.state[domain].results);
  const selectedResult = useMatchingStore((store) => store.state[domain].selectedResult);
  const rightTab = useMatchingStore((store) => store.state[domain].rightTab);
  const catalogs = useMatchingStore((store) => store.state[domain].catalogs);

  return useMemo(
    () => ({ hasSearched, results, selectedResult, rightTab, catalogs }),
    [hasSearched, results, selectedResult, rightTab, catalogs],
  );
}

/** Combined state + domain-bound actions hook for pages.
 *
 * Actions are selected separately and memoized to avoid triggering
 * unnecessary re-renders from changing function references.
 */
export function useDomainMatching(domain: Domain) {
  const state = useDomainMatchingState(domain);

  const setResults = useMatchingStore((store) => store.setResults);
  const setSelectedResult = useMatchingStore((store) => store.setSelectedResult);
  const setHasSearched = useMatchingStore((store) => store.setHasSearched);
  const setRightTab = useMatchingStore((store) => store.setRightTab);
  const setCatalogs = useMatchingStore((store) => store.setCatalogs);
  const clearDomain = useMatchingStore((store) => store.clearDomain);

  return useMemo(
    () => ({
      ...state,
      setResults: (results: UnifiedMatchResult[], selectedResult?: UnifiedMatchResult | null) =>
        setResults(domain, results, selectedResult),
      setSelectedResult: (result: UnifiedMatchResult | null) => setSelectedResult(domain, result),
      setHasSearched: (value: boolean) => setHasSearched(domain, value),
      setRightTab: (tab: RightTab) => setRightTab(domain, tab),
      setCatalogs: (catalogs: Partial<DomainCatalogs>) => setCatalogs(domain, catalogs),
      clearDomain: () => clearDomain(domain),
    }),
    [state, setResults, setSelectedResult, setHasSearched, setRightTab, setCatalogs, clearDomain, domain],
  );
}

import { useState, useEffect } from "react";

/** In-memory image cache keyed by URL. */
const _cache = new Map<string, string>();

/**
 * Returns a cached object URL for the given image URL.
 * Fetches and caches the image on first use; subsequent calls reuse the blob URL.
 */
export function useCachedImage(url: string | undefined): string | undefined {
  const [blobUrl, setBlobUrl] = useState<string | undefined>(() =>
    url ? _cache.get(url) : undefined
  );

  useEffect(() => {
    if (!url) {
      setBlobUrl(undefined);
      return;
    }

    const cached = _cache.get(url);
    if (cached) {
      setBlobUrl(cached);
      return;
    }

    let cancelled = false;
    fetch(url)
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to load image: ${res.status}`);
        return res.blob();
      })
      .then((blob) => {
        if (cancelled) return;
        const objectUrl = URL.createObjectURL(blob);
        _cache.set(url, objectUrl);
        setBlobUrl(objectUrl);
      })
      .catch(() => {
        // On error, keep undefined so the component can fall back
      });

    return () => {
      cancelled = true;
    };
  }, [url]);

  return blobUrl;
}

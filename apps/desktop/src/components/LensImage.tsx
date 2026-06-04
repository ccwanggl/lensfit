import { useState } from "react";
import { useCachedImage } from "../hooks/useCachedImage";

interface LensImageProps {
  model: string;
  focal: string;
  aperture: string;
  brand: string;
  imageUrl?: string;
  size?: "sm" | "md" | "lg";
}

const BRAND_STYLES: Record<string, { bg: string; accent: string; text: string }> = {
  Canon: { bg: "from-red-700 to-red-900", accent: "#DC0000", text: "text-white" },
  Sony: { bg: "from-slate-800 to-black", accent: "#5865F2", text: "text-white" },
  Nikon: { bg: "from-yellow-500 to-yellow-700", accent: "#FFE600", text: "text-black" },
  Sigma: { bg: "from-slate-100 to-slate-300", accent: "#000000", text: "text-black" },
  Tamron: { bg: "from-red-600 to-red-800", accent: "#E4002B", text: "text-white" },
  Fujifilm: { bg: "from-sky-500 to-sky-700", accent: "#009DE0", text: "text-white" },
};

function getBrand(model: string): string {
  const brands = ["Canon", "Sony", "Nikon", "Sigma", "Tamron", "Fujifilm"];
  return brands.find((b) => model.startsWith(b)) || "Generic";
}

function getBrandStyle(model: string) {
  const brand = getBrand(model);
  return BRAND_STYLES[brand] || { bg: "from-indigo-600 to-violet-800", accent: "#6366f1", text: "text-white" };
}

/** Generated SVG lens concept image - used as fallback when real image fails to load */
function GeneratedLensImage({ model, focal, aperture, brand, size = "md" }: LensImageProps) {
  const style = getBrandStyle(model);
  const isDark = style.text === "text-white";

  const dims = {
    sm: { w: 80, h: 60, fontTitle: 8, fontSpec: 6, ring: 2 },
    md: { w: 320, h: 200, fontTitle: 18, fontSpec: 14, ring: 4 },
    lg: { w: 480, h: 300, fontTitle: 24, fontSpec: 18, ring: 6 },
  }[size];

  const brandText = brand || getBrand(model);

  return (
    <div
      className={`relative overflow-hidden rounded-xl bg-gradient-to-br ${style.bg} flex items-center justify-center`}
      style={{ width: dims.w, height: dims.h }}
    >
      {/* Background pattern */}
      <svg className="absolute inset-0 w-full h-full opacity-10" viewBox={`0 0 ${dims.w} ${dims.h}`}>
        <defs>
          <pattern id={`grid-${size}`} width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke={isDark ? "white" : "black"} strokeWidth="0.5" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill={`url(#grid-${size})`} />
      </svg>

      {/* Lens body SVG */}
      <svg
        className="absolute"
        viewBox="0 0 200 120"
        style={{
          width: size === "sm" ? 50 : size === "md" ? 160 : 240,
          height: size === "sm" ? 30 : size === "md" ? 96 : 144,
        }}
      >
        {/* Lens barrel */}
        <defs>
          <linearGradient id="barrel" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor={isDark ? "#374151" : "#9ca3af"} />
            <stop offset="30%" stopColor={isDark ? "#1f2937" : "#d1d5db"} />
            <stop offset="50%" stopColor={isDark ? "#111827" : "#e5e7eb"} />
            <stop offset="70%" stopColor={isDark ? "#1f2937" : "#d1d5db"} />
            <stop offset="100%" stopColor={isDark ? "#374151" : "#9ca3af"} />
          </linearGradient>
          <linearGradient id="glass" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={isDark ? "#60a5fa" : "#93c5fd"} stopOpacity="0.4" />
            <stop offset="50%" stopColor={isDark ? "#3b82f6" : "#60a5fa"} stopOpacity="0.2" />
            <stop offset="100%" stopColor={isDark ? "#1d4ed8" : "#3b82f6"} stopOpacity="0.3" />
          </linearGradient>
          <linearGradient id="ring" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor={style.accent} stopOpacity="0.8" />
            <stop offset="50%" stopColor={style.accent} stopOpacity="0.5" />
            <stop offset="100%" stopColor={style.accent} stopOpacity="0.8" />
          </linearGradient>
        </defs>

        {/* Main barrel */}
        <rect x="20" y="25" width="140" height="70" rx="4" fill="url(#barrel)" />
        
        {/* Front glass */}
        <ellipse cx="165" cy="60" rx="12" ry="30" fill="url(#glass)" />
        <ellipse cx="165" cy="60" rx="8" ry="24" fill="none" stroke={isDark ? "#60a5fa" : "#3b82f6"} strokeWidth="1" opacity="0.5" />

        {/* Focus ring */}
        <rect x="50" y="22" width="40" height="76" rx="2" fill="none" stroke="url(#ring)" strokeWidth={dims.ring} opacity="0.6" />
        
        {/* Grip texture lines */}
        {Array.from({ length: 8 }).map((_, i) => (
          <line
            key={i}
            x1={52 + i * 5}
            y1="28"
            x2={52 + i * 5}
            y2="92"
            stroke={isDark ? "#4b5563" : "#9ca3af"}
            strokeWidth="0.8"
            opacity="0.4"
          />
        ))}

        {/* Mount */}
        <rect x="8" y="30" width="12" height="60" rx="2" fill={isDark ? "#1f2937" : "#9ca3af"} />
        <rect x="6" y="35" width="4" height="50" rx="1" fill={isDark ? "#374151" : "#6b7280"} />
      </svg>

      {/* Text overlay */}
      <div className={`absolute inset-0 flex flex-col items-center justify-center ${style.text}`}>
        <span
          className="font-bold tracking-tight"
          style={{ fontSize: dims.fontTitle, textShadow: isDark ? "0 1px 4px rgba(0,0,0,0.5)" : "0 1px 4px rgba(255,255,255,0.5)" }}
        >
          {brandText}
        </span>
        {size !== "sm" && (
          <span
            className="font-medium mt-0.5 opacity-90"
            style={{ fontSize: dims.fontSpec, textShadow: isDark ? "0 1px 3px rgba(0,0,0,0.4)" : "0 1px 3px rgba(255,255,255,0.4)" }}
          >
            {focal} · f/{aperture}
          </span>
        )}
      </div>

      {/* Subtle vignette */}
      <div className="absolute inset-0 rounded-xl" style={{ boxShadow: "inset 0 0 30px rgba(0,0,0,0.2)" }} />
    </div>
  );
}

export default function LensImage({ model, focal, aperture, brand, imageUrl, size = "md" }: LensImageProps) {
  const [imgError, setImgError] = useState(false);
  const cachedUrl = useCachedImage(imageUrl);

  const dims = {
    sm: { w: 80, h: 60 },
    md: { w: 320, h: 200 },
    lg: { w: 480, h: 300 },
  }[size];

  // If no image URL or image failed to load, show generated concept image
  if (!imageUrl || imgError) {
    return <GeneratedLensImage model={model} focal={focal} aperture={aperture} brand={brand} size={size} />;
  }

  return (
    <div
      className="relative overflow-hidden rounded-xl bg-gray-100 flex items-center justify-center"
      style={{ width: dims.w, height: dims.h }}
    >
      <img
        src={cachedUrl || imageUrl}
        alt={model}
        className="w-full h-full object-contain"
        onError={() => setImgError(true)}
        loading="lazy"
        decoding="async"
      />
      {/* Subtle vignette overlay */}
      <div className="absolute inset-0 rounded-xl pointer-events-none" style={{ boxShadow: "inset 0 0 30px rgba(0,0,0,0.15)" }} />
    </div>
  );
}

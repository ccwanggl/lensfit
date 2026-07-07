from __future__ import annotations

import re
import posixpath
from pathlib import Path
from urllib.parse import unquote


ROOT = Path("OpticKnowledgeSpace")
SKIP_PARTS = {".compute", ".obsidian", ".hinote", "attachments", "Assets", "templates", "copilot", "Excalidraw"}


ORDERS: dict[str, list[str]] = {
    "10-concepts": [
        "refractive-index",
        "近轴近似",
        "工作距离",
        "focal-length",
        "焦距",
        "f-number",
        "数值孔径",
        "depth-of-field",
        "放大倍率",
        "image-circle",
        "像圈",
        "视场",
        "视角",
        "透视畸变",
        "视差",
        "法兰距",
        "abbe-number",
        "dispersion",
        "色散",
        "chromatic-aberration",
        "色差",
        "interference",
        "干涉",
        "diffraction-grating",
        "衍射光栅",
        "diffraction-limit",
        "衍射极限",
        "airy-disk",
        "艾里斑",
        "瑞利判据",
        "psf",
        "点扩散函数",
        "otf",
        "光学传递函数",
        "mtf",
        "调制传递函数",
        "pixel",
        "像素精度",
        "nyquist-frequency",
        "奈奎斯特频率",
        "aliasing",
        "混叠",
        "过采样",
        "边缘检测",
        "illumination-geometry",
        "照明方式",
        "同轴照明",
        "低角度照明",
        "远心照明",
        "分光镜",
        "polarization",
        "偏振",
        "漫射",
        "镜面反射",
        "半影",
        "均匀性",
        "平场",
        "渐晕",
        "全局快门",
        "global-shutter",
        "卷帘快门",
        "rolling-shutter",
        "动态范围",
        "读出噪声",
        "NETD",
        "微测辐射热计",
        "发射率",
        "果冻效应",
        "spectral-power-distribution",
        "color-temperature",
        "色温",
        "chromaticity-diagram",
        "fluorescence",
        "raman-scattering",
        "multispectral-imaging",
        "hyperspectral-imaging",
        "spectral-resolution",
        "snapshot-spectral-imaging",
        "multispectral-filter-array",
        "fabry-perot-microcavity",
        "metasurface",
        "spectral-reconstruction",
    ],
    "20-formulas": [
        "thin-lens-gauss",
        "lateral-magnification",
        "focal-length-from-wd",
        "angle-of-view",
        "coverage-ratio",
        "pixel-precision",
        "nyquist-frequency",
        "oversampling-ratio",
        "airy-disk-diameter",
        "rayleigh-criterion",
        "瑞利分辨率",
        "double-slit-fringe-spacing",
        "grating-equation",
        "grating-resolving-power",
        "prism-dispersion",
        "planck-blackbody",
        "delta-e",
    ],
    "30-domains": [
        "industrial-vision",
        "photography",
        "microscopy",
        "infrared-imaging",
        "spectroscopy",
        "on-chip-multispectral",
    ],
    "40-devices": [
        "c-mount-lens",
        "telecentric-lens",
        "microscope-objective",
        "global-shutter-cmos",
        "rolling-shutter-cmos",
        "backlight",
        "led-ring-light",
        "coaxial-illumination",
        "telecentric-illumination",
        "bandpass-filter",
        "diffraction-grating",
        "spectrometer",
        "hyperspectral-camera",
        "on-chip-spectral-sensor",
        "integrating-sphere",
        "ir-thermal-detector",
        "ingaas-focal-plane-array",
        "mct-detector",
    ],
    "50-learning": [
        "introduction",
        "light-and-waves",
        "geometric-optics",
        "lens-parameters",
        "sensors",
        "matching-basics",
        "aberrations",
        "interfaces-and-mounts",
        "domain-applications",
        "exercises",
        "physical-optics-advanced",
        "optical-design-basics",
        "otf-and-image-quality",
        "illumination-design",
        "computational-optics",
        "engineering-cases",
        "spectroscopy",
    ],
    "80-sources": [
        "Textbook Index",
        "Textbook Reference Matrix",
        "hecht-optics-5e",
        "saleh-teich-fundamentals-photonics-3e",
        "goodman-introduction-fourier-optics-4e",
        "smith-modern-optical-engineering-4e",
        "wyszecki-stiles-color-science-2e",
        "gonzalez-woods-digital-image-processing-4e",
        "driggers-infrared-electro-optical-systems-3e",
        "on-chip-multispectral-literature",
    ],
    "90-maps": [
        "Knowledge Map",
        "Learning Path",
        "Knowledge Architecture",
        "Visual Learning Toolkit",
        "Visual Index",
        "Interactive Explorer",
        "Obsidian Setup",
        "Optics Lab",
        "On-chip Multispectral Topic",
    ],
}


def normalize_rel(path: Path) -> str:
    return path.as_posix()


def strip_numeric_prefix(stem: str) -> str:
    previous = None
    current = stem
    while previous != current:
        previous = current
        current = re.sub(r"^\d{2,3}-", "", current)
    return current


def should_scan(path: Path) -> bool:
    return not any(part in SKIP_PARTS for part in path.parts)


def build_mapping() -> dict[str, str]:
    mapping: dict[str, str] = {}
    root_abs = ROOT.resolve()
    for dirname, ordered_stems in ORDERS.items():
        directory = ROOT / dirname
        if not directory.exists():
            continue

        files = [p for p in directory.glob("*.md") if p.name != "README.md"]
        by_stem = {strip_numeric_prefix(p.stem): p for p in files}
        ordered: list[Path] = []
        seen: set[Path] = set()

        for stem in ordered_stems:
            path = by_stem.get(stem)
            if path and path not in seen:
                ordered.append(path)
                seen.add(path)

        for path in sorted(files, key=lambda p: strip_numeric_prefix(p.stem).lower()):
            if path not in seen:
                ordered.append(path)
                seen.add(path)

        for index, old_path in enumerate(ordered):
            bare_stem = strip_numeric_prefix(old_path.stem)
            new_path = old_path.with_name(f"{index:03d}-{bare_stem}{old_path.suffix}")
            if old_path.resolve() == new_path.resolve():
                continue
            if new_path.exists():
                raise RuntimeError(f"Target already exists: {new_path}")
            old_rel = normalize_rel(old_path.resolve().relative_to(root_abs))
            new_rel = normalize_rel(new_path.resolve().relative_to(root_abs))
            mapping[old_rel] = new_rel
    return mapping


def add_index_alias(
    path_map: dict[str, str],
    basename_map: dict[str, str],
    alias_rel: str,
    current_rel: str,
) -> None:
    alias_no_ext = alias_rel[:-3] if alias_rel.endswith(".md") else alias_rel
    current_no_ext = current_rel[:-3] if current_rel.endswith(".md") else current_rel
    path_map[alias_rel] = current_rel
    path_map[alias_no_ext] = current_no_ext
    basename_map[Path(alias_no_ext).name] = Path(current_no_ext).name


def build_current_alias_indexes(path_map: dict[str, str], basename_map: dict[str, str]) -> None:
    root_abs = ROOT.resolve()
    for dirname in ORDERS:
        directory = ROOT / dirname
        if not directory.exists():
            continue
        for path in directory.glob("*.md"):
            if path.name == "README.md":
                continue
            current_rel = normalize_rel(path.resolve().relative_to(root_abs))
            bare_stem = strip_numeric_prefix(path.stem)
            if bare_stem == path.stem:
                continue

            add_index_alias(path_map, basename_map, f"{dirname}/{bare_stem}.md", current_rel)

            prefix_match = re.match(r"^(\d{3})-", path.stem)
            if prefix_match:
                legacy_index = f"{int(prefix_match.group(1)):02d}"
                add_index_alias(path_map, basename_map, f"{dirname}/{legacy_index}-{bare_stem}.md", current_rel)


def build_indexes(mapping: dict[str, str]):
    path_map: dict[str, str] = {}
    basename_map: dict[str, str] = {}
    for old_rel, new_rel in mapping.items():
        add_index_alias(path_map, basename_map, old_rel, new_rel)
    build_current_alias_indexes(path_map, basename_map)
    return path_map, basename_map


def resolve_wiki_target(source_rel: str, target: str, path_map: dict[str, str], basename_map: dict[str, str]) -> str | None:
    if not target or target.startswith("#") or target.startswith(("http://", "https://", "mailto:")):
        return None

    decoded = unquote(target).replace("\\", "/")
    suffix = ".md" if decoded.endswith(".md") else ""
    probe = decoded[:-3] if suffix else decoded

    if probe.startswith(("./", "../")):
        source_parent = Path(source_rel).parent
        try:
            normalized = normalize_rel((ROOT.resolve() / source_parent / probe).resolve().relative_to(ROOT.resolve()))
        except ValueError:
            return None
        mapped = path_map.get(normalized + suffix) or path_map.get(normalized)
        if mapped:
            mapped_no_ext = mapped[:-3] if mapped.endswith(".md") else mapped
            rel_text = posixpath.relpath(mapped_no_ext, start=Path(source_rel).parent.as_posix())
            if not rel_text.startswith("."):
                rel_text = "./" + rel_text
            return rel_text + suffix

    mapped = path_map.get(decoded) or path_map.get(probe)
    if mapped:
        if suffix and not mapped.endswith(".md"):
            return mapped + ".md"
        return mapped

    if "/" not in probe:
        mapped_name = basename_map.get(probe)
        if mapped_name:
            return mapped_name + suffix

    return None


def update_wiki_links(text: str, source_rel: str, path_map: dict[str, str], basename_map: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        prefix = match.group(1)
        inner = match.group(2).replace("\\|", "|")
        if "|" in inner:
            target_part, alias = inner.split("|", 1)
            alias_part = "|" + alias
        else:
            target_part, alias_part = inner, ""
        if "#" in target_part:
            target, heading = target_part.split("#", 1)
            heading_part = "#" + heading
        else:
            target, heading_part = target_part, ""
        mapped = resolve_wiki_target(source_rel, target, path_map, basename_map)
        if not mapped:
            return match.group(0)
        return f"{prefix}[[{mapped}{heading_part}{alias_part}]]"

    return re.sub(r"(!?)\[\[([^\]]+)\]\]", repl, text)


MD_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")


def update_markdown_links(text: str, source_rel: str, path_map: dict[str, str], basename_map: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        label, raw_target = match.group(1), match.group(2)
        if raw_target.startswith("<") and raw_target.endswith(">"):
            wrapped = True
            target = raw_target[1:-1]
        else:
            wrapped = False
            target = raw_target
        if target.startswith(("http://", "https://", "mailto:", "#")):
            return match.group(0)

        if "#" in target:
            target_path, anchor = target.split("#", 1)
            anchor_part = "#" + anchor
        else:
            target_path, anchor_part = target, ""

        mapped = resolve_wiki_target(source_rel, target_path, path_map, basename_map)
        if not mapped:
            return match.group(0)
        new_target = mapped + anchor_part
        if wrapped or " " in new_target:
            new_target = f"<{new_target}>"
        return f"[{label}]({new_target})"

    return MD_LINK_RE.sub(repl, text)


def update_links(mapping: dict[str, str]) -> None:
    path_map, basename_map = build_indexes(mapping)
    root_abs = ROOT.resolve()
    for path in ROOT.rglob("*.md"):
        if not should_scan(path):
            continue
        source_rel = normalize_rel(path.resolve().relative_to(root_abs))
        text = path.read_text(encoding="utf-8")
        updated = update_wiki_links(text, source_rel, path_map, basename_map)
        updated = update_markdown_links(updated, source_rel, path_map, basename_map)
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="\n")


def perform_renames(mapping: dict[str, str]) -> None:
    root_abs = ROOT.resolve()
    for old_rel, new_rel in sorted(mapping.items(), key=lambda item: item[0].count("/"), reverse=True):
        old_path = root_abs / old_rel
        new_path = root_abs / new_rel
        old_path.rename(new_path)


def main() -> None:
    if not ROOT.exists():
        raise SystemExit(f"Missing vault root: {ROOT}")
    mapping = build_mapping()
    print(f"Planned renames: {len(mapping)}")
    for old, new in mapping.items():
        print(f"{old} -> {new}")
    update_links(mapping)
    perform_renames(mapping)


if __name__ == "__main__":
    main()

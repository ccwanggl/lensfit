"""Illumination geometry experiment."""

from __future__ import annotations

from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import circle, line, polygon, svg_root, text


class IlluminationGeometryExperiment(OpticsExperiment):
    experiment_id = "illumination-geometry"
    title = "照明方式几何实验"
    description = "切换明场、暗场、同轴、漫射背光、低角度等照明方式，观察表面特征如何被凸显。"
    difficulty = "intermediate"
    prerequisites = ["snell-refraction"]
    linked_concepts = [
        "illumination-geometry",
        "低角度照明",
        "10-concepts/同轴照明",
        "镜面反射",
        "漫射",
    ]
    learning_objectives = [
        "理解照明几何决定了相机看到哪些表面特征。",
        "掌握明场、暗场、同轴、背光、低角度照明的适用场景。",
        "认识镜面反射、漫反射和散射在不同照明下的表现差异。",
    ]
    parameters = [
        Parameter(
            name="mode",
            label="照明方式",
            type="enum",
            default="bright-field",
            options=[
                {"value": "bright-field", "label": "明场照明"},
                {"value": "dark-field", "label": "暗场照明"},
                {"value": "coaxial", "label": "同轴照明"},
                {"value": "diffuse-back", "label": "漫射背光"},
                {"value": "low-angle", "label": "低角度照明"},
            ],
        ),
        Parameter(
            name="feature_type",
            label="表面特征",
            type="enum",
            default="scratch",
            options=[
                {"value": "scratch", "label": "划痕"},
                {"value": "bump", "label": "凸起"},
                {"value": "specular", "label": "镜面区域"},
                {"value": "transparent", "label": "透明边缘"},
            ],
        ),
    ]

    # Configuration for each illumination mode.
    _MODE_INFO: dict[str, dict[str, Any]] = {
        "bright-field": {
            "label": "明场照明",
            "description": "光源靠近相机光轴，漫反射面明亮，镜面区域易过曝。",
            "light_positions": [(120, 60)],
            "light_color": "#f59e0b",
            "ray_angle_deg": 75.0,
            "camera_sees": {
                "scratch": "dim",
                "bump": "shadow",
                "specular": "glare",
                "transparent": "edge",
            },
        },
        "dark-field": {
            "label": "暗场照明",
            "description": "光源以掠射角入射，光滑面暗，划痕/凸起散射光进入相机。",
            "light_positions": [(40, 220)],
            "light_color": "#f59e0b",
            "ray_angle_deg": 10.0,
            "camera_sees": {
                "scratch": "bright",
                "bump": "bright",
                "specular": "dim",
                "transparent": "dim",
            },
        },
        "coaxial": {
            "label": "同轴照明",
            "description": "光源与相机共用光路，镜面反射沿原路返回，表面均匀明亮。",
            "light_positions": [(320, 40)],
            "light_color": "#38bdf8",
            "ray_angle_deg": 90.0,
            "camera_sees": {
                "scratch": "dim",
                "bump": "uniform",
                "specular": "bright",
                "transparent": "edge",
            },
        },
        "diffuse-back": {
            "label": "漫射背光",
            "description": "均匀光源从样品后方照射，形成轮廓，适合边缘与透明物。",
            "light_positions": [(320, 280)],
            "light_color": "#ffffff",
            "ray_angle_deg": 90.0,
            "camera_sees": {
                "scratch": "dim",
                "bump": "silhouette",
                "specular": "silhouette",
                "transparent": "bright",
            },
        },
        "low-angle": {
            "label": "低角度照明",
            "description": "光线几乎平行于表面，微小高度差产生长阴影，凸显纹理。",
            "light_positions": [(80, 230)],
            "light_color": "#f59e0b",
            "ray_angle_deg": 5.0,
            "camera_sees": {
                "scratch": "shadow",
                "bump": "shadow",
                "specular": "glare",
                "transparent": "edge",
            },
        },
    }

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        mode = str(params.get("mode", "bright-field"))
        feature = str(params.get("feature_type", "scratch"))
        if mode not in self._MODE_INFO:
            mode = "bright-field"
        if feature not in {"scratch", "bump", "specular", "transparent"}:
            feature = "scratch"

        info = self._MODE_INFO[mode]
        visibility = info["camera_sees"].get(feature, "dim")

        svg = self._draw_svg(mode, feature, info)

        return ExperimentResult(
            data={
                "mode": mode,
                "mode_label": info["label"],
                "feature_type": feature,
                "visibility": visibility,
                "description": info["description"],
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "明场适合观察漫反射表面的整体形貌。",
                "暗场和低角度适合检测划痕、灰尘和微小凸起。",
                "同轴照明可抑制阴影并突出镜面反射。",
                "背光适合轮廓测量和透明/半透明物体。",
                "本实验是二维光线示意图，未建模三维散射瓣和 BRDF。",
            ],
        )

    def _draw_svg(
        self,
        mode: str,
        feature: str,
        info: dict[str, Any],
    ) -> str:
        width, height = 640, 360
        surface_y = 240
        camera_x, camera_y = 320, 60

        children: list[str] = []

        # Surface.
        children.extend(
            [
                line(80, surface_y, 560, surface_y, stroke="#475569", stroke_width=3),
                text(
                    320, surface_y + 25, "被测表面", fill="#64748b", font_size=11, anchor="middle"
                ),
            ]
        )

        # Feature on the surface.
        feature_x = 320
        children.extend(self._draw_feature(feature, feature_x, surface_y))

        # Camera.
        children.extend(
            [
                polygon(
                    [
                        (camera_x - 20, camera_y - 15),
                        (camera_x + 20, camera_y - 15),
                        (camera_x + 12, camera_y + 10),
                        (camera_x - 12, camera_y + 10),
                    ],
                    fill="#1e293b",
                    stroke="#94a3b8",
                ),
                circle(camera_x, camera_y - 2, 6, fill="#38bdf8", stroke="none"),
                text(
                    camera_x, camera_y - 25, "相机", fill="#94a3b8", font_size=11, anchor="middle"
                ),
            ]
        )

        # Light source(s) and rays.
        light_color = info["light_color"]
        for lx, ly in info["light_positions"]:
            children.extend(
                self._draw_light_and_rays(
                    lx, ly, feature_x, surface_y, camera_x, camera_y, light_color, mode, feature
                )
            )

        # Legend / description panel.
        children.extend(
            [
                polygon(
                    [(20, 20), (620, 20), (620, 55), (20, 55)],
                    fill="#f1f5f9",
                    stroke="#cbd5e1",
                ),
                text(
                    30, 40, f"{info['label']} — {info['description']}", fill="#334155", font_size=12
                ),
                text(
                    30,
                    340,
                    (
                        f"当前特征「{self._feature_label(feature)}」"
                        f"在相机中的可见性："
                        f"{self._visibility_label(info['camera_sees'].get(feature, 'dim'))}"
                    ),
                    fill="#475569",
                    font_size=11,
                ),
            ]
        )

        return svg_root(width, height, children)

    def _draw_feature(self, feature: str, x: float, y: float) -> list[str]:
        if feature == "scratch":
            return [line(x - 15, y - 8, x + 15, y + 2, stroke="#ef4444", stroke_width=3)]
        if feature == "bump":
            return [
                circle(x, y - 12, 12, fill="none", stroke="#ef4444", stroke_width=2),
                circle(x, y - 12, 4, fill="#ef4444", stroke="none"),
            ]
        if feature == "specular":
            return [
                rect(x - 25, y - 4, 50, 4, fill="#e2e8f0", stroke="#94a3b8"),
                text(x, y - 10, "镜面", fill="#94a3b8", font_size=10, anchor="middle"),
            ]
        if feature == "transparent":
            return [
                line(x, y, x, y - 60, stroke="#38bdf8", stroke_width=4, opacity=0.5),
                line(x - 20, y - 60, x + 20, y - 60, stroke="#38bdf8", stroke_width=2),
                text(x, y - 75, "透明边缘", fill="#38bdf8", font_size=10, anchor="middle"),
            ]
        return []

    def _draw_light_and_rays(
        self,
        lx: float,
        ly: float,
        feature_x: float,
        surface_y: float,
        camera_x: float,
        camera_y: float,
        color: str,
        mode: str,
        feature: str,
    ) -> list[str]:
        elements: list[str] = []
        # Light source icon.
        elements.append(circle(lx, ly, 14, fill=color, stroke="#475569", stroke_width=2))
        elements.append(text(lx, ly + 4, "L", fill="#1e293b", font_size=12, anchor="middle"))

        # Incident ray from light toward feature.
        # Backlight mode: rays go upward through the sample.
        if mode == "diffuse-back":
            elements.append(
                line(lx, ly - 14, feature_x, surface_y - 30, stroke=color, stroke_width=2)
            )
            elements.append(
                line(feature_x, surface_y - 30, feature_x, surface_y, stroke=color, stroke_width=2)
            )
            # Transmitted/scattered ray to camera.
            elements.append(
                line(
                    feature_x, surface_y - 30, camera_x, camera_y + 10, stroke=color, stroke_width=2
                )
            )
            return elements

        # Other modes: light hits the surface feature.
        elements.append(line(lx, ly, feature_x, surface_y - 5, stroke=color, stroke_width=2))

        # Reflected / scattered ray to camera.
        if mode == "coaxial":
            # Coaxial: light comes through camera path; draw a beam splitter.
            elements.extend(
                [
                    line(
                        camera_x,
                        camera_y + 10,
                        camera_x,
                        surface_y - 5,
                        stroke=color,
                        stroke_width=2,
                    ),
                    line(
                        feature_x,
                        surface_y - 5,
                        camera_x,
                        surface_y - 5,
                        stroke=color,
                        stroke_width=2,
                    ),
                    line(
                        camera_x,
                        surface_y - 5,
                        camera_x,
                        camera_y + 10,
                        stroke=color,
                        stroke_width=2,
                    ),
                    # Beamsplitter plate.
                    line(
                        camera_x - 25,
                        surface_y - 35,
                        camera_x + 25,
                        surface_y - 75,
                        stroke="#94a3b8",
                        stroke_width=3,
                    ),
                    text(camera_x + 35, surface_y - 55, "分光镜", fill="#94a3b8", font_size=10),
                ]
            )
        elif mode == "dark-field" and feature in {"scratch", "bump"}:
            # Scattered ray upward into camera.
            elements.append(
                line(
                    feature_x,
                    surface_y - 5,
                    camera_x,
                    camera_y + 10,
                    stroke="#22c55e",
                    stroke_width=2,
                )
            )
        elif mode == "low-angle":
            # Long shadow ray.
            shadow_end_x = feature_x + 80 if lx < feature_x else feature_x - 80
            elements.append(
                line(
                    feature_x, surface_y, shadow_end_x, surface_y, stroke="#334155", stroke_width=3
                )
            )
            # Some reflected light to camera.
            elements.append(
                line(
                    feature_x,
                    surface_y - 5,
                    camera_x,
                    camera_y + 10,
                    stroke=color,
                    stroke_width=1,
                    opacity=0.5,
                )
            )
        else:
            # Generic reflected ray.
            elements.append(
                line(
                    feature_x, surface_y - 5, camera_x, camera_y + 10, stroke=color, stroke_width=2
                )
            )

        return elements

    @staticmethod
    def _feature_label(feature: str) -> str:
        return {
            "scratch": "划痕",
            "bump": "凸起",
            "specular": "镜面区域",
            "transparent": "透明边缘",
        }.get(feature, feature)

    @staticmethod
    def _visibility_label(visibility: str) -> str:
        return {
            "bright": "高亮",
            "dim": "暗淡",
            "glare": "眩光",
            "shadow": "阴影/高对比",
            "uniform": "均匀",
            "silhouette": "轮廓",
            "edge": "边缘可见",
        }.get(visibility, visibility)


def rect(
    x: float,
    y: float,
    w: float,
    h: float,
    fill: str = "none",
    stroke: str = "#94a3b8",
    stroke_width: float = 1,
) -> str:
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
    )

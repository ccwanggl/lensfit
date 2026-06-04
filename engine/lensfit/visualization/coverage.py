"""Sensor coverage visualization data generator."""

from __future__ import annotations

from typing import Any


class CoveragePlotData:
    """传感器覆盖图几何数据."""

    def __init__(self, sensor_w: float, sensor_h: float, image_circle: float):
        self.sensor_w = sensor_w
        self.sensor_h = sensor_h
        self.image_circle = image_circle

    def generate(self) -> dict[str, Any]:
        """生成可视化数据.

        Returns:
            {
                sensor_rect: {x, y, w, h},
                image_circle: {cx, cy, r},
                vignetting_regions: [Polygon],
                coverage_ratio: float,
                safe_zone: {x, y, w, h}
            }
        """
        sensor_rect = {
            "x": -self.sensor_w / 2,
            "y": -self.sensor_h / 2,
            "w": self.sensor_w,
            "h": self.sensor_h,
        }

        image_circle = {"cx": 0, "cy": 0, "r": self.image_circle / 2}

        # 计算覆盖率
        sensor_diag = (self.sensor_w**2 + self.sensor_h**2) ** 0.5
        coverage_ratio = min(1.0, (self.image_circle / sensor_diag) ** 2)

        # 计算渐晕区域（传感器四角超出像圆的部分）
        vignetting_regions = self._compute_vignetting_regions()

        # 安全区域（完全无渐晕的内接矩形）
        # 当传感器对角线 > 像圆直径时，按比例缩放至对角线等于像圆直径
        sensor_diag = (self.sensor_w**2 + self.sensor_h**2) ** 0.5
        if sensor_diag <= self.image_circle:
            safe_w, safe_h = self.sensor_w, self.sensor_h
        else:
            scale = self.image_circle / sensor_diag
            safe_w = self.sensor_w * scale
            safe_h = self.sensor_h * scale
        safe_zone = {
            "x": -safe_w / 2,
            "y": -safe_h / 2,
            "w": safe_w,
            "h": safe_h,
        }

        return {
            "sensor_rect": sensor_rect,
            "image_circle": image_circle,
            "vignetting_regions": vignetting_regions,
            "coverage_ratio": round(coverage_ratio, 3),
            "safe_zone": safe_zone,
        }

    def _compute_vignetting_regions(self) -> list[dict[str, Any]]:
        """计算渐晕区域多边形.

        简化为：如果传感器对角线 > 像圆直径，则四角有渐晕.
        """
        sensor_diag = (self.sensor_w**2 + self.sensor_h**2) ** 0.5
        if sensor_diag <= self.image_circle:
            return []

        # 简化：返回四个角的渐晕区域（三角形近似）
        r = self.image_circle / 2
        hw = self.sensor_w / 2
        hh = self.sensor_h / 2

        regions = []
        # 四个角：(hw, hh), (-hw, hh), (-hw, -hh), (hw, -hh)
        corners = [
            (hw, hh, 1, 1),      # 右上
            (-hw, hh, -1, 1),    # 左上
            (-hw, -hh, -1, -1),  # 左下
            (hw, -hh, 1, -1),    # 右下
        ]

        for cx, cy, sx, sy in corners:
            # 渐晕区域：角点到像圆边界的三角形
            # 简化：如果角点到圆心距离 > r，则该角有渐晕
            dist = (cx**2 + cy**2) ** 0.5
            if dist > r:
                # 交点坐标（近似）
                ratio = r / dist
                ix = cx * ratio
                iy = cy * ratio
                regions.append({
                    "points": [
                        {"x": cx, "y": cy},
                        {"x": ix, "y": iy},
                        {"x": cx, "y": iy},
                    ]
                })

        return regions

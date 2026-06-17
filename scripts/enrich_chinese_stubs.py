"""Enrich selected Chinese concept stubs with concise definitions and mark reviewed."""

from __future__ import annotations

import re
from pathlib import Path

VAULT = Path("OpticKnowledgeSpace")

DEFINITIONS: dict[str, tuple[str, str | None]] = {
    "10-concepts/全局快门.md": (
        "全局快门（Global Shutter）指传感器所有像元在同一时刻开始曝光并在同一时刻结束曝光，然后统一读出。"
        "优点：拍摄高速运动物体时不会产生果冻效应或形变。缺点：帧率受限、读出噪声通常高于卷帘快门。"
        "常用于工业检测、机器视觉、科学成像。",
        "10-concepts/global-shutter",
    ),
    "10-concepts/卷帘快门.md": (
        "卷帘快门（Rolling Shutter）逐行曝光和读出，每行像素的曝光时间相同，但起始时刻不同。"
        "优点：结构简单、帧率高、噪声低。缺点：拍摄快速运动物体或高频振动时会产生果冻效应（Jello Effect）、倾斜或形变。"
        "常见于消费级相机和手机。",
        "10-concepts/rolling-shutter",
    ),
    "10-concepts/像圈.md": (
        "像圈（Image Circle）是镜头在焦平面上能够形成清晰、均匀像的圆形区域直径。"
        "选择镜头时必须保证像圈直径 ≥ 传感器对角线，否则四角会出现暗角或黑边。"
        "工业镜头常用 C-mount、F-mount 等接口规格描述像圈范围。",
        "10-concepts/image-circle",
    ),
    "10-concepts/像素精度.md": (
        "像素精度（Pixel Accuracy / Pixel Resolution）指图像中每个像素对应的实际物理尺寸，通常用 mm/pixel 或 μm/pixel 表示。"
        "像素精度 = 视场宽度 / 图像水平像素数。精度越高，每个像素代表的物理尺寸越小，测量或检测分辨率越高。",
        "10-concepts/pixel",
    ),
    "10-concepts/工作距离.md": (
        "工作距离（Working Distance, WD）指镜头前端到被测物体表面之间的距离。"
        "它是镜头选型的核心参数之一，直接影响视场大小、景深和可安装的照明/机械结构。"
        "工作距离通常与焦距、传感器尺寸共同决定成像比例。",
        "20-formulas/working-distance",
    ),
    "10-concepts/数值孔径.md": (
        "数值孔径（Numerical Aperture, NA）是衡量光学系统聚光能力的无量纲参数，NA = n · sinθ，其中 n 为介质折射率，θ 为物方半孔径角。"
        "NA 越大，分辨率越高、景深越浅。显微镜物镜的核心指标之一。",
        "10-concepts/numerical-aperture",
    ),
    "10-concepts/动态范围.md": (
        "动态范围（Dynamic Range）是传感器或成像系统能够同时记录的最亮与最暗信号之比，通常用 dB 或 bit 表示。"
        "动态范围越大，越能在同一场景中保留高光和阴影细节。工业检测中常用于避免过曝或欠曝。",
        "10-concepts/dynamic-range",
    ),
    "10-concepts/渐晕.md": (
        "渐晕（Vignetting）指图像四角或边缘亮度比中心低的现象。"
        "成因包括：镜头像圈不足、光路遮挡、大角度入射光衰减、滤镜或遮光罩遮挡。"
        "可通过选择更大像圈镜头、缩小光圈或后期校正改善。",
        "10-concepts/vignetting",
    ),
    "10-concepts/视场.md": (
        "视场（Field of View, FOV）是相机能够看到的实际空间范围，通常用水平/垂直角度或 mm 表示。"
        "视场与焦距、传感器尺寸和工作距离有关：焦距越短、传感器越大、工作距离越近，视场越大。",
        "10-concepts/field-of-view",
    ),
    "10-concepts/视角.md": (
        "视角（Angle of View）是视场的角度表示，即镜头对场景的张角。"
        "常用水平视角、垂直视角、对角线视角描述。视角与焦距和传感器尺寸成反比。",
        "10-concepts/angle-of-view",
    ),
    "10-concepts/色差.md": (
        "色差（Chromatic Aberration）指镜头对不同波长光的焦距不同，导致白光成像出现彩色边缘或色散的现象。"
        "分为轴向色差（不同颜色焦点前后分离）和倍率色差（放大倍率随波长变化）。"
        "可通过消色差/复消色差镜头、缩小光圈或后期校正减小。",
        "10-concepts/chromatic-aberration",
    ),
    "10-concepts/衍射极限.md": (
        "衍射极限（Diffraction Limit）指由于光的波动性质，理想光学系统也无法将点光源聚焦为无限小的点，而是形成艾里斑。"
        "系统分辨率受衍射限制，最小可分辨细节与波长和光圈大小有关：波长越长、光圈越小（F值越大），衍射极限越明显。",
        "10-concepts/diffraction-limit",
    ),
    "10-concepts/法兰距.md": (
        "法兰距（Flange Distance / Flange Focal Distance）指相机镜头卡口基准面到传感器感光面的距离。"
        "不同卡口（C-mount、F-mount、M42 等）有标准法兰距，镜头与机身法兰距不匹配会导致无法合焦或需要转接环。",
        "10-concepts/flange-distance",
    ),
    "10-concepts/混叠.md": (
        "混叠（Aliasing）指采样频率不足时，高频信号被误判为低频伪影的现象。"
        "在成像中表现为摩尔纹、锯齿边缘。避免方法：满足奈奎斯特采样定理（采样频率 ≥ 2 倍最高空间频率）、使用光学低通滤波器或过采样。",
        "10-concepts/aliasing",
    ),
    "10-concepts/过采样.md": (
        "过采样（Oversampling）指成像系统的采样频率远高于奈奎斯特频率，使得每个细节由多个像素表示。"
        "优点：提高测量精度、降低混叠风险、便于后期缩放。缺点：数据量大、对镜头分辨率要求更高。",
        "10-concepts/oversampling",
    ),
}


def update_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text
    parts = text.split("---", 2)
    fm = parts[1]
    body = parts[2]
    lines = []
    for line in fm.splitlines():
        if line.strip().startswith("status:"):
            lines.append("status: reviewed")
        else:
            lines.append(line)
    if "status: reviewed" not in "\n".join(lines):
        lines.append("status: reviewed")
    return "---\n" + "\n".join(lines) + "---" + body


def main():
    updated = 0
    for rel_path, (definition, en_counterpart) in DEFINITIONS.items():
        md_file = VAULT / rel_path
        if not md_file.exists():
            print(f"Skip missing {md_file}")
            continue
        text = md_file.read_text(encoding="utf-8")
        text = update_frontmatter(text)
        # Replace placeholder stub body
        body_marker = "此笔记为自动生成的占位 stub，用于修复断裂的双链。需要补充定义、公式、适用场景和来源。"
        new_body = f"\n\n# {md_file.stem}\n\n{definition}\n"
        if en_counterpart:
            new_body += f"\n更完整的讨论见 [[{en_counterpart}|英文同名笔记]]。\n"
        if body_marker in text:
            text = text.replace(body_marker, definition)
            text = re.sub(r"# .+\n", f"# {md_file.stem}\n", text, count=1)
        else:
            # If already has content, ensure definition is present
            if md_file.stem not in text[:200]:
                text += new_body
        md_file.write_text(text, encoding="utf-8")
        updated += 1
    print(f"Updated {updated} Chinese stubs")


if __name__ == "__main__":
    main()

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
    "10-concepts/近轴近似.md": (
        "近轴近似（Paraxial Approximation）指光线与光轴夹角很小（sin θ ≈ tan θ ≈ θ）时的简化模型。"
        "在该近似下，球面折射和反射公式可线性化，得到高斯光学公式（薄透镜公式、放大率公式等）。"
        "当角度较大时，近轴近似失效，需要考虑像差和非近轴光线追迹。",
        "10-concepts/paraxial-approximation",
    ),
    "10-concepts/双远心.md": (
        "双远心（Bi-telecentric / Double Telecentricity）指镜头在物方和像方均保持远心光路："
        "物方主光线与光轴平行，像方主光线也与光轴平行。"
        "优点：放大倍率不随工作距离变化，适合精密尺寸测量；缺点：体积大、成本高、需要更大传感器。",
        "10-concepts/bi-telecentricity",
    ),
    "10-concepts/远心照明.md": (
        "远心照明（Telecentric Illumination）使用准直光照射被测物，光线方向几乎平行于光轴。"
        "配合远心镜头可显著减少阴影、镜面反射和边缘模糊，提高边缘检测和尺寸测量精度。"
        "常用于工业视觉中的背光或同轴远心照明系统。",
        "10-concepts/telecentric-illumination",
    ),
    "10-concepts/同轴照明.md": (
        "同轴照明（Coaxial Illumination）将光源通过分光镜与镜头同轴耦合，光线沿镜头光轴照射样品。"
        "优点：可照亮垂直表面、减少阴影，适合检测镜面、光滑平面上的划痕或凹陷。"
        "缺点：对粗糙或倾斜表面效果差，可能产生强烈反光。",
        "10-concepts/coaxial-illumination",
    ),
    "10-concepts/低角度照明.md": (
        "低角度照明（Low-angle Illumination）让光线以接近水平的角度照射样品表面。"
        "优点：能突出表面纹理、划痕、凸起和凹陷（浮雕效应），常用于缺陷检测。"
        "缺点：对颜色信息不敏感，可能丢失部分表面细节。",
        "10-concepts/low-angle-illumination",
    ),
    "10-concepts/分光镜.md": (
        "分光镜（Beam Splitter）是将一束光按波长、偏振或能量比例分成两束或多束的光学元件。"
        "常见类型包括：立方体分光镜、平板分光镜、二向色镜、偏振分光镜。"
        "广泛用于同轴照明、干涉仪、光谱仪、荧光显微镜等系统。",
        "10-concepts/beam-splitter",
    ),
    "10-concepts/镜面反射.md": (
        "镜面反射（Specular Reflection）指光线在光滑表面按入射角等于反射角的规律反射。"
        "成像中常导致高光或过曝；在机器视觉中可利用同轴照明或偏振滤光片抑制。"
        "与漫反射相对，后者将光向多个方向散射。",
        "10-concepts/specular-reflection",
    ),
    "10-concepts/漫射.md": (
        "漫射（Diffuse Reflection / Diffusion）指光线照射粗糙表面后向多个方向散射的现象。"
        "漫射光源（如乳白罩、积分球）可提供均匀照明，减少高光和阴影。"
        "在视觉检测中常用于均匀照亮漫反射材料。",
        "10-concepts/diffuse-reflection",
    ),
    "10-concepts/半影.md": (
        "半影（Penumbra）指光源有一定大小时，被不透明物体遮挡后形成的部分阴影区。"
        "在半影区内，只有部分光源被遮挡，亮度介于全影（本影）和亮区之间。"
        "照明设计时应尽量减小半影，以获得锐利的物体边缘。",
        "10-concepts/penumbra",
    ),
    "10-concepts/透视畸变.md": (
        "透视畸变（Perspective Distortion）指由于拍摄角度或物体离镜头距离不同，导致图像中平行线汇聚、近大远小的几何变形。"
        "在工业测量中通常需要避免；远心镜头和同轴照明可有效抑制透视畸变。",
        "10-concepts/perspective-distortion",
    ),
    "10-concepts/视差.md": (
        "视差（Parallax）指从不同位置观察同一物体时，物体相对于背景的相对位置变化。"
        "在镜头选型中，普通镜头因透视会产生视差；远心镜头主光线平行，可消除视差，适合高精度测量。",
        "10-concepts/parallax",
    ),
    "10-concepts/放大倍率.md": (
        "放大倍率（Magnification）指像高与物高之比，β = v / u = 像高 / 物高。"
        "在显微镜和远心镜头中常直接标注倍率。"
        "测量应用中，稳定的放大倍率是像素精度换算的基础。",
        "10-concepts/magnification",
    ),
    "10-concepts/平场.md": (
        "平场（Flat-field Correction）指消除镜头渐晕、传感器不均匀性和照明不均匀性对图像亮度影响的过程。"
        "通常通过拍摄均匀参考图像（平场帧）获得增益/偏移系数，再对实际图像进行校正。",
        "10-concepts/flat-field-correction",
    ),
    "10-concepts/均匀性.md": (
        "均匀性（Uniformity）指照明或成像系统在整个视场内亮度/响应的一致程度。"
        "不均匀会导致检测阈值难以设定，常用平场校正、漫射光源或匀光板改善。",
        "10-concepts/uniformity",
    ),
    "10-concepts/果冻效应.md": (
        "果冻效应（Jello Effect）是卷帘快门拍摄快速运动物体时出现的倾斜、摇摆或局部形变现象。"
        "成因是不同行曝光时刻不同，物体在行间移动。"
        "避免方法：使用全局快门、降低运动速度、提高帧率、减少振动。",
        "10-concepts/jello-effect",
    ),
    "10-concepts/边缘检测.md": (
        "边缘检测（Edge Detection）是图像处理中提取物体轮廓的算法，常用 Sobel、Canny、Laplacian 等算子。"
        "在机器视觉中，边缘位置精度直接影响尺寸测量结果；照明和镜头 MTF 对边缘质量至关重要。",
        "10-concepts/edge-detection",
    ),
    "10-concepts/NETD.md": (
        "NETD（Noise Equivalent Temperature Difference，噪声等效温差）是红外热成像系统的核心灵敏度指标，"
        "表示系统能分辨的最小温度差。NETD 越低，热灵敏度越高。典型值从 <20 mK（高端科学级）到 >100 mK（工业级）不等。",
        "10-concepts/NETD",
    ),
    "10-concepts/发射率.md": (
        "发射率（Emissivity）是物体表面在相同温度下辐射能量与理想黑体辐射能量之比，取值 0–1。"
        "它直接影响红外测温的准确性：高发射率表面（如哑光金属、人体皮肤）测得准；"
        "低发射率表面（如抛光金属、玻璃）反射环境辐射，需要校正或涂覆高发射率材料。",
        "10-concepts/emissivity",
    ),
    "10-concepts/奈奎斯特频率.md": (
        "奈奎斯特频率（Nyquist Frequency）是采样率的一半，即 f_N = f_s / 2。"
        "根据奈奎斯特采样定理，信号中高于奈奎斯特频率的成分会导致混叠，无法被正确重建。"
        "在成像中对应最高可分辨空间频率；在传感器选型中常用来估算镜头 MTF 与像素尺寸的匹配上限。",
        "10-concepts/nyquist-frequency",
    ),
    "10-concepts/微测辐射热计.md": (
        "微测辐射热计（Microbolometer）是一种非制冷红外探测器，通过吸收红外辐射使敏感元温度升高，"
        "进而改变电阻值并转换为电信号。它无需液氮或斯特林制冷机，体积小、功耗低，"
        "广泛用于手持热像仪、安防监控和工业测温。常见响应波段为 8–14 μm（长波红外）。",
        "10-concepts/microbolometer",
    ),
    "10-concepts/焦距.md": (
        "焦距（Focal Length）是镜头光学中心到焦点的距离，通常用 f 表示，单位为 mm。"
        "焦距决定视角和放大倍率：焦距越长，视角越窄，放大倍率越大；焦距越短，视角越宽。"
        "与物距、像距一起构成薄透镜高斯公式 1/f = 1/u + 1/v。",
        "10-concepts/focal-length",
    ),
    "10-concepts/瑞利判据.md": (
        "瑞利判据（Rayleigh Criterion）指出：当一个点光源衍射图样的中央极大正好落在另一个点光源衍射图样的第一极小处时，"
        "两者刚好可被分辨。对应的最小分辨角约为 θ ≈ 1.22 λ / D，是光学系统衍射极限分辨率的经典判据。",
        "10-concepts/rayleigh-criterion",
    ),
    "10-concepts/色温.md": (
        "色温（Color Temperature）描述光源颜色的冷暖程度，单位为开尔文（K）。"
        "它等于与该光源颜色相同的黑体辐射体的温度：低色温（2700K）偏黄暖，高色温（6500K）偏蓝冷。"
        "摄影、显示和机器视觉白平衡都依赖色温概念。",
        "10-concepts/color-temperature",
    ),
    "10-concepts/艾里斑.md": (
        "艾里斑（Airy Disk）是点光源通过圆形孔径后，由于衍射形成的中心亮斑和同心圆环结构。"
        "中心亮斑直径约为 d ≈ 2.44 λ F#，决定了理想光学系统的极限分辨尺寸。"
        "艾里斑是衍射极限和瑞利判据的物理基础。",
        "10-concepts/airy-disk",
    ),
    "10-concepts/读出噪声.md": (
        "读出噪声（Read Noise）是传感器在将像元电荷转换为电压并数字化过程中引入的电子噪声。"
        "它决定了系统能检测到的最小信号，在低光照或短曝光场景下成为主要噪声源。"
        "读出噪声通常以 e⁻（等效电子数）表示，数值越小越好。",
        "10-concepts/read-noise",
    ),
    "20-formulas/瑞利分辨率.md": (
        "瑞利分辨率（Rayleigh Resolution）基于瑞利判据，给出圆形孔径光学系统刚好能分辨的两个点之间的最小角距离："
        "θ ≈ 1.22 λ / D，其中 λ 为波长，D 为入瞳直径。"
        "在显微镜和望远镜中，瑞利分辨率是衡量极限分辨能力的核心指标。",
        "20-formulas/rayleigh-criterion",
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

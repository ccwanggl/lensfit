from __future__ import annotations

import re
from pathlib import Path

ROOT = Path("OpticKnowledgeSpace/10-concepts")
REFERENCE_MATRIX = "[[../80-sources/Textbook Reference Matrix|教材页码索引矩阵]]"

REFS = {
    "hecht": "- [[../80-sources/hecht-optics-5e|Hecht, *Optics*, 5th ed.]]：适合核对光线模型、波动模型、干涉、衍射和偏振的基础定义。",
    "saleh": "- [[../80-sources/saleh-teich-fundamentals-photonics-3e|Saleh & Teich, *Fundamentals of Photonics*, 3rd ed.]]：适合核对探测器、光与物质相互作用、光子学器件和现代光学系统。",
    "goodman": "- [[../80-sources/goodman-introduction-fourier-optics-4e|Goodman, *Introduction to Fourier Optics*, 4th ed.]]：适合核对傅里叶光学、空间频率、PSF/OTF/MTF、采样和衍射成像。",
    "smith": "- [[../80-sources/smith-modern-optical-engineering-4e|Smith, *Modern Optical Engineering*, 4th ed.]]：适合核对镜头系统、孔径光阑、像差、像质评价和工程约束。",
    "color": "- [[../80-sources/wyszecki-stiles-color-science-2e|Wyszecki & Stiles, *Color Science*, 2nd ed.]]：适合核对色度图、色温、标准光源和颜色测量。",
    "dip": "- [[../80-sources/gonzalez-woods-digital-image-processing-4e|Gonzalez & Woods, *Digital Image Processing*, 4th ed.]]：适合核对采样、混叠、边缘检测和数字图像处理链路。",
    "ir": "- [[../80-sources/driggers-infrared-electro-optical-systems-3e|Driggers et al., *Introduction to Infrared and Electro-Optical Systems*, 3rd ed.]]：适合核对红外探测器、NETD、发射率和 EO/IR 系统性能评价。",
    "onchip": "- [[../80-sources/on-chip-multispectral-literature|片上多光谱/高光谱文献与学习路线]]：适合核对超表面、滤波阵列、快照式光谱成像和光谱重建等前沿主题。",
}

GROUPS = {
    "color": {"chromaticity-diagram", "color-temperature", "色温", "spectral-power-distribution"},
    "spectrum": {
        "spectral-resolution",
        "dispersion",
        "色散",
        "diffraction-grating",
        "衍射光栅",
        "fluorescence",
        "raman-scattering",
        "multispectral-imaging",
        "hyperspectral-imaging",
        "snapshot-spectral-imaging",
        "spectral-reconstruction",
        "metasurface",
        "fabry-perot-microcavity",
        "multispectral-filter-array",
    },
    "fourier": {
        "mtf",
        "otf",
        "psf",
        "调制传递函数",
        "光学传递函数",
        "点扩散函数",
        "aliasing",
        "混叠",
        "nyquist-frequency",
        "奈奎斯特频率",
        "过采样",
        "边缘检测",
    },
    "detector": {
        "pixel",
        "像素精度",
        "读出噪声",
        "动态范围",
        "全局快门",
        "卷帘快门",
        "NETD",
        "微测辐射热计",
        "发射率",
    },
    "wave": {
        "airy-disk",
        "艾里斑",
        "diffraction-limit",
        "衍射极限",
        "interference",
        "干涉",
        "polarization",
        "偏振",
        "瑞利判据",
        "数值孔径",
        "半影",
    },
    "geometry": {
        "refractive-index",
        "focal-length",
        "焦距",
        "f-number",
        "depth-of-field",
        "image-circle",
        "像圈",
        "视角",
        "视场",
        "工作距离",
        "放大倍率",
        "近轴近似",
        "视差",
        "透视畸变",
        "法兰距",
        "渐晕",
        "均匀性",
        "平场",
        "分光镜",
        "双远心",
    },
    "illumination": {"illumination-geometry", "照明方式", "低角度照明", "同轴照明", "远心照明", "镜面反射", "漫射"},
}

SUPPLEMENTS = {
    "均匀性": """
## 补充说明

均匀性描述照明或成像响应在视场内的一致程度。机器视觉里常见的均匀性问题包括中心亮、边缘暗、局部热点、光源条纹和传感器响应不一致。它会直接影响阈值分割、灰度测量、颜色测量和缺陷检测。

## 适用边界

均匀性不是只看光源，也取决于镜头像圈、渐晕、物体表面反射、曝光设置和传感器平场校正。需要定量比较时，应说明测量区域、统计口径和允许偏差，比如最大/最小亮度比或标准差。
""",
    "视差": """
## 补充说明

视差指观察位置改变后，近处物体相对远处背景发生位置变化的现象。在成像系统中，视差会影响双目测距、近距离检测、标定板拍摄和多相机拼接。它不是镜头像差，而是观察几何导致的投影差异。

## 适用边界

远心镜头可以减小由物距变化引起的尺寸变化，但不能让所有多视角问题自动消失。涉及多相机或高精度测量时，应把相机基线、工作距离、物体高度变化和标定误差一起考虑。
""",
    "半影": """
## 补充说明

半影来自扩展光源。物体遮挡光源时，如果某个位置只能看到光源的一部分，就会形成亮度介于本影和全亮区之间的过渡区域。光源越大、离物体越近，半影通常越宽；光源越小或离物体越远，边缘越锐利。

## 适用边界

半影常用于解释背光测量、投影轮廓和低角度照明中的边缘变软。它和镜头失焦、运动模糊都会让边缘变宽，但成因不同。判断半影时应先看光源尺寸、光源到物体距离和物体到成像面的几何关系。
""",
    "平场": """
## 补充说明

平场描述系统在没有样品结构时的参考响应。显微成像、工业视觉和光谱成像都会用平场图来校正照明不均、像素响应差异和镜头渐晕。平场校正的基本思路是先测系统自身响应，再把样品图像归一化到这个响应上。

## 适用边界

平场只适合校正稳定、可重复的系统性不均匀。光源闪烁、样品反射变化、曝光漂移和非线性饱和不能靠一次平场完全消除。做定量测量时，暗场、平场和曝光条件应一起记录。
""",
    "放大倍率": """
## 补充说明

放大倍率描述物体尺寸映射到像面尺寸的比例。工业视觉中更常用横向放大倍率，它可以由传感器尺寸和视场反推，也可以由薄透镜成像关系估算。放大倍率越大，同样大小的物体细节会占据更多像素。

## 常见误区

焦距长不等于放大倍率一定大。放大倍率还取决于物距、像距、传感器尺寸和视场要求。比较不同镜头时，应把工作距离和视场固定下来再谈放大倍率。
""",
    "果冻效应": """
## 补充说明

果冻效应是卷帘快门逐行曝光导致的几何变形。相机不是在同一时刻记录整幅图像，而是按行依次读出；当物体或相机在读出过程中运动时，不同行对应不同时间，直线可能变斜，快速旋转物体可能变弯。

## 适用边界

果冻效应不是镜头畸变。镜头畸变在静态场景中也存在，卷帘变形主要和读出时间、运动速度、曝光同步和触发方式有关。高速检测或运动测量优先考虑全局快门。
""",
    "透视畸变": """
## 补充说明

透视畸变来自投影几何：物体离相机越近，在图像中显得越大；离相机越远，显得越小。它会让高低不同的物体边缘产生位置偏移，也会让倾斜平面上的尺寸测量变得不稳定。

## 适用边界

透视畸变不是镜头畸变。普通镜头即使没有桶形或枕形畸变，也会有透视投影。需要做尺寸测量时，可以通过增加工作距离、使用远心镜头或做几何标定来降低影响。
""",
    "分光镜": """
## 补充说明

分光镜用于把入射光按方向、波长或偏振状态分成多个通道。常见形式包括半反半透分束器、二向色镜、棱镜和光栅。不同分光器件的核心差别在于分光依据不同：有的按能量比例分，有的按波长分，有的按偏振分。

## 适用边界

选择分光镜时不能只看分光比。还要看工作波段、入射角、偏振敏感性、透射/反射效率、镀膜损耗和像质要求。光谱系统中，分光元件还会影响杂散光和光谱分辨率。
""",
    "远心照明": """
## 补充说明

远心照明让照明光线以接近平行的方式照射物体，常和远心镜头配合，用于获得稳定的轮廓边界。它可以减小由于物体高度变化引起的阴影扩张，适合高精度尺寸测量和边缘定位。

## 适用边界

远心照明通常体积大、成本高，对安装同轴度也更敏感。它适合轮廓和尺寸测量，不一定适合观察表面纹理、划痕或低对比缺陷。
""",
    "双远心": """
## 补充说明

双远心系统在物方和像方都接近远心。物方远心降低物距变化带来的倍率变化，像方远心让主光线接近垂直进入传感器，有利于保持边缘位置和像面照度稳定。高精度测量镜头常采用这种结构。

## 适用边界

双远心并不自动提高分辨率，它主要解决倍率稳定和投影几何问题。系统仍然会受数值孔径、衍射、像差、照明和传感器采样限制。
""",
    "视角": """
## 补充说明

视角描述相机能看到的角范围，通常分为水平、垂直和对角线视角。它由焦距和传感器尺寸共同决定：焦距越短、传感器越大，视角越大。工程上不能脱离传感器尺寸单独说某个焦距对应固定视角。

## 适用边界

视角公式通常基于针孔或薄透镜近似。畸变很大的广角镜头、鱼眼镜头和复杂变焦镜头需要使用厂家给出的投影模型或实测标定结果。
""",
    "视场": """
## 补充说明

视场是成像系统在目标平面上覆盖的实际范围，通常用宽度、高度或对角线表示。它和视角不同：视角是角度，视场是目标面上的长度。固定工作距离下，视角越大，视场越大。

## 常见误区

视场不是传感器尺寸。传感器尺寸决定像面接收范围，视场还取决于焦距、工作距离和放大倍率。工业视觉选型时通常先给目标视场，再反推焦距和传感器尺寸。
""",
    "过采样": """
## 补充说明

过采样指采样频率高于信号所需频率的情况。成像里常见的说法是传感器像元足够小，能够以比镜头实际分辨率更高的频率记录图像。适度过采样有利于后续算法和亚像素定位，但过度过采样会增加数据量、噪声压力和成本。

## 适用边界

过采样不是越高越好。若镜头 MTF 已经在高频处很低，继续减小像元不会带来等比例的真实细节提升。需要同时看镜头 MTF、传感器奈奎斯特频率、曝光噪声和算法目标。
""",
    "瑞利判据": """
## 补充说明

瑞利判据给出两个点源刚好可分辨的常用经验条件：一个艾里斑中心落在另一个艾里斑的第一暗环附近时，两者被认为刚好分开。它把衍射图样和分辨率联系起来，常用于显微镜、望远镜和理想圆孔成像的极限估算。

## 适用边界

瑞利判据不是所有图像任务的唯一分辨率标准。真实系统还会受像差、噪声、采样、对比度和图像处理影响。低对比目标通常比高对比点源更难分辨。
""",
    "漫射": """
## 补充说明

漫射指光在粗糙表面或散射介质中向多个方向传播。机器视觉里，漫射照明常用于降低镜面高光，让金属、塑料和曲面物体的亮度更均匀。漫射也可能降低纹理和划痕的方向性对比。

## 适用边界

漫射不是一定更好。检测凹凸、划痕或细小边缘时，过强的漫射可能把有用阴影抹平。照明方式应根据缺陷类型选择，而不是只追求均匀。
""",
    "读出噪声": """
## 补充说明

读出噪声来自传感器把电荷转换成数字信号的过程，包括放大、采样、模数转换和读出电路噪声。它在弱光、短曝光和小信号测量中尤其重要，因为信号本身很小，读出链路的固定噪声会占很大比例。

## 适用边界

读出噪声不同于光子散粒噪声。前者主要来自电子读出链路，后者来自光子到达的统计波动。判断相机低照度表现时，应同时看满阱容量、量子效率、暗电流和读出噪声。
""",
    "动态范围": """
## 补充说明

动态范围描述系统同时记录暗部和亮部的能力，通常由最大不饱和信号与噪声底之比决定。传感器满阱容量越大、噪声越低，动态范围越高。高动态范围对反光目标、背光场景和热成像都有意义。

## 适用边界

动态范围不是只由位深决定。12 bit 或 16 bit ADC 只能表示数字级数，真实可用范围还受传感器噪声、模拟链路、曝光设置和光学杂散光限制。
""",
    "发射率": """
## 补充说明

发射率描述物体实际热辐射能力相对理想黑体的比例。红外测温中，同样温度的高发射率物体和低发射率物体会给探测器不同辐射信号。金属抛光表面发射率低，还容易反射环境辐射。

## 适用边界

发射率通常随材料、表面粗糙度、波长、温度和观察角变化。红外测温若不设置发射率或背景反射条件，温度读数可能有明显偏差。
""",
    "像圈": """
## 补充说明

像圈是镜头在像面上能形成可用图像的区域。传感器对角线必须落在像圈内，否则边缘会出现暗角、清晰度下降或颜色偏移。工程上常把像圈和传感器规格一起检查。

## 适用边界

像圈够大不代表边缘像质一定好。镜头可能覆盖传感器，但边缘 MTF、畸变、色差和照度仍然不满足检测要求。选型时应同时看像圈、分辨率和目标视场。
""",
    "镜面反射": """
## 补充说明

镜面反射指入射光按确定方向反射，入射角等于反射角。光滑金属、玻璃、液体表面和抛光塑料都容易产生镜面高光。机器视觉中，镜面反射既可能造成饱和，也可以用来突出表面划痕或形貌。

## 适用边界

消除镜面反射不总是目标。若缺陷本身通过高光变化表现出来，暗场、低角度或偏振照明可能比均匀漫射更有效。
""",
    "数值孔径": """
## 补充说明

数值孔径（NA）描述光学系统接收或发出光线的角范围，常写作 $NA = n\\sin\\theta$。显微成像中，NA 越大，系统能收集更大角度的光，理论分辨率越高，景深也越浅。

## 适用边界

NA 大不等于实际图像一定更好。高 NA 系统对对焦、盖玻片厚度、浸没介质、像差校正和照明匹配更敏感。分辨率判断还要结合波长和采样。
""",
    "色差": """
## 补充说明

色差来自材料色散。不同波长的光折射率不同，因此焦点位置或放大倍率会随波长变化。轴向色差表现为不同颜色沿光轴焦点不同，横向色差表现为边缘不同颜色的像高不同。

## 适用边界

色差不是所有彩边的唯一来源。传感器去马赛克、过曝、像素串扰和后期锐化也可能造成类似彩边。判断光学色差时，应结合视场位置、焦点变化和波长依赖性。
""",
    "低角度照明": """
## 补充说明

低角度照明让光以很小的入射角掠过表面，表面凸起、划痕和凹坑会产生明显阴影或高光。它适合突出平面上的微小高度变化，常用于金属、玻璃、薄膜和印刷缺陷检测。

## 适用边界

低角度照明对安装高度和角度很敏感，也容易受物体翘曲影响。它能强化表面形貌，但不一定适合测颜色、灰度均匀性或内部结构。
""",
    "同轴照明": """
## 补充说明

同轴照明让光沿相机光轴方向照射目标，通常通过分光镜把光源引入镜头轴线。平整反光表面会把光反回镜头，因此明亮；倾斜、粗糙或凹陷区域反光偏离镜头，因此变暗。

## 适用边界

同轴照明适合平面反光目标、二维码、晶圆、玻璃表面和金属平面缺陷。对粗糙漫反射目标，它的优势可能不明显，还可能造成整体对比下降。
""",
    "法兰距": """
## 补充说明

法兰距是镜头安装基准面到像面的机械距离。它决定镜头能否在指定接口上正确合焦。C-mount、CS-mount、F-mount 等接口都有各自的标准法兰距。

## 适用边界

法兰距不是工作距离。工作距离在物方，法兰距在像方和机械接口侧。转接环、垫片、滤光片厚度和传感器封装都会影响实际后焦位置。
""",
    "近轴近似": """
## 补充说明

近轴近似假设光线与光轴夹角很小，可以把三角函数近似成线性关系。薄透镜公式、焦距定义和一阶成像关系通常都建立在近轴近似上。它让复杂光学系统可以先用简单模型估算。

## 适用边界

大视场、大孔径、强广角和高 NA 系统容易超出近轴近似。此时一阶公式仍可给直觉，但不能替代真实光线追迹、像差分析或实测标定。
""",
    "边缘检测": """
## 补充说明

边缘检测在图像中寻找亮度或颜色快速变化的位置。光学系统的清晰度、照明方式、噪声、采样和运动模糊都会影响边缘检测结果。机器视觉里，边缘常用于定位、测量、轮廓提取和缺陷识别。

## 适用边界

边缘检测不是纯算法问题。若照明让边缘没有稳定对比，或者镜头 MTF 太低，后端算法很难恢复可靠边界。做测量任务时，应把光学成像和算法阈值一起验证。
""",
}


def remove_bad_sections(text: str) -> str:
    return re.sub(r"\n## \?+\n.*?(?=\n## |\Z)", "", text, flags=re.DOTALL)


def normalize_frontmatter(text: str) -> str:
    text = re.sub(r"(aliases:\s*\[\])---", r"\1\n---", text)
    text = re.sub(r"(\n\s*-\s*[^\n]+?)---\n", r"\1\n---\n", text)
    return text


def choose_refs(stem: str) -> list[str]:
    refs: list[str] = []

    def add(key: str) -> None:
        if key not in refs:
            refs.append(key)

    if stem in GROUPS["color"]:
        add("color")
        add("hecht")
        add("saleh")
    if stem in GROUPS["spectrum"]:
        add("hecht")
        add("saleh")
        if stem in {"snapshot-spectral-imaging", "spectral-reconstruction", "metasurface", "fabry-perot-microcavity", "multispectral-filter-array"}:
            add("onchip")
    if stem in GROUPS["fourier"]:
        add("goodman")
        if stem in {"边缘检测", "过采样", "混叠", "aliasing"}:
            add("dip")
    if stem in GROUPS["detector"]:
        add("saleh")
        if stem in {"NETD", "微测辐射热计", "发射率"}:
            add("ir")
    if stem in GROUPS["wave"]:
        add("hecht")
        add("goodman")
    if stem in GROUPS["geometry"]:
        add("hecht")
        add("smith")
    if stem in GROUPS["illumination"]:
        add("smith")
        add("hecht")
    if not refs:
        add("hecht")
        add("smith")
    return refs[:3]


def textbook_section(stem: str) -> str:
    lines = ["## 教材参考", ""]
    lines.extend(REFS[key] for key in choose_refs(stem))
    lines.append(f"- {REFERENCE_MATRIX}：本页引用先保持章节级定位，精确页码待后续核验后回填。")
    return "\n".join(lines) + "\n"


def insert_before_marker(text: str, addition: str, markers: list[str]) -> str:
    positions = [text.find(marker) for marker in markers if text.find(marker) != -1]
    if not positions:
        return text.rstrip() + "\n\n" + addition
    idx = min(positions)
    return text[:idx].rstrip() + "\n\n" + addition + "\n" + text[idx:].lstrip()


def main() -> None:
    changed: list[str] = []
    for path in sorted(ROOT.glob("*.md")):
        if path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8")
        original = text
        text = normalize_frontmatter(remove_bad_sections(text))
        stem = path.stem
        if stem in SUPPLEMENTS and "## 补充说明" not in text:
            text = insert_before_marker(text, SUPPLEMENTS[stem].strip() + "\n", ["## 可视化辅助", "## 来源", "## 关联实验", "## 参见"])
        if "## 教材参考" not in text:
            text = insert_before_marker(text, textbook_section(stem), ["## 来源", "## 关联实验"])
        if text != original:
            path.write_text(text, encoding="utf-8", newline="\n")
            changed.append(str(path))
    print("\n".join(changed))
    print(f"changed={len(changed)}")


if __name__ == "__main__":
    main()

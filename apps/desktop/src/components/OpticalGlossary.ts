export interface GlossaryEntry {
  term: string;
  explanation: string;
  related?: string[];
}

export const OpticalGlossary: Record<string, GlossaryEntry> = {
  focal_length: {
    term: "焦距",
    explanation:
      "镜头光学中心到成像平面（传感器）的距离。焦距越短，视场越宽；焦距越长，放大倍率越高。匹配时焦距需满足目标物距下的成像尺寸要求。",
    related: ["magnification", "field_of_view"],
  },
  magnification: {
    term: "放大倍率",
    explanation:
      "像高与物高之比（β = y'/y）。工业检测中放大倍率直接决定像素精度——倍率越大，单位像素对应的物理尺寸越小，分辨率越高。",
    related: ["focal_length", "pixel_accuracy_mm"],
  },
  pixel_accuracy_mm: {
    term: "像素精度",
    explanation:
      "每个像素对应的物理尺寸（mm/px）。计算公式：像素精度 = 像素尺寸 / 放大倍率。该值越小，系统能分辨的物理细节越精细。",
    related: ["magnification", "pixel_size"],
  },
  pixel_size: {
    term: "像素尺寸",
    explanation:
      "传感器上单个像素的物理边长（μm）。像素尺寸越小，相同像元数下传感器面积越小，但对镜头分辨率要求越高。",
    related: ["pixel_accuracy_mm", "nyquist_limit"],
  },
  nyquist_limit: {
    term: "奈奎斯特频率",
    explanation:
      "数字采样系统的理论最高可分辨空间频率，为采样频率的一半。在成像中，若镜头分辨率低于奈奎斯特极限，会出现混叠（Aliasing）。",
    related: ["pixel_size", "resolution"],
  },
  image_circle: {
    term: "像圈",
    explanation:
      "镜头能够均匀成像的圆形区域直径。像圈必须大于或等于传感器的对角线长度，否则会产生渐晕（暗角）。",
    related: ["sensor_format", "vignetting"],
  },
  sensor_format: {
    term: "传感器靶面",
    explanation:
      "传感器感光区域的有效尺寸（如 1/2\"、2/3\"、1\"）。靶面越大，像圈要求越大；同时视场也越宽，但相机体积和成本增加。",
    related: ["image_circle", "sensor_diagonal"],
  },
  sensor_diagonal: {
    term: "传感器对角线",
    explanation:
      "传感器矩形成像区域的对角线长度，是判断镜头像圈是否足够覆盖传感器的核心指标。",
    related: ["sensor_format", "image_circle"],
  },
  vignetting: {
    term: "渐晕",
    explanation:
      "图像四角或边缘亮度显著降低的现象。通常因镜头像圈小于传感器尺寸，或镜头轴外透过率下降导致。",
    related: ["image_circle", "coverage_ratio"],
  },
  coverage_ratio: {
    term: "覆盖比",
    explanation:
      "传感器面积中不受渐晕影响的区域占比。覆盖比 ≥ 90% 通常视为安全，低于此值可能在边缘引入测量误差。",
    related: ["image_circle", "sensor_format", "vignetting"],
  },
  working_distance: {
    term: "工作距离",
    explanation:
      "镜头前端到被测物体表面的距离。工作距离影响视场大小、景深及可安装的照明结构，需与机械布局匹配。",
    related: ["focal_length", "field_of_view", "depth_of_field"],
  },
  depth_of_field: {
    term: "景深",
    explanation:
      "成像保持可接受清晰度的物距范围。景深越大，对被测物体的高度波动容忍度越高；但景深与光圈、放大倍率相互制约。",
    related: ["aperture", "magnification", "working_distance"],
  },
  aperture: {
    term: "光圈",
    explanation:
      "控制镜头通光孔径的装置，以 F 值（如 F2.8、F4）表示。光圈越大（F 值越小），进光量越多、景深越浅；同时影响衍射极限分辨率。",
    related: ["depth_of_field", "resolution"],
  },
  f_number: {
    term: "F 值",
    explanation:
      "焦距与有效通光孔径之比（f/D）。F 值越小，光圈越大，进光量越多，分辨率越高，但景深变浅。",
    related: ["aperture", "depth_of_field", "resolution"],
  },
  resolution: {
    term: "分辨率",
    explanation:
      "光学系统可分辨的最小细节能力，通常用线对/毫米（lp/mm）表示。需高于传感器奈奎斯特频率，否则细节无法被采样记录。",
    related: ["nyquist_limit", "mtf", "pixel_size"],
  },
  mtf: {
    term: "MTF",
    explanation:
      "调制传递函数（Modulation Transfer Function），量化镜头还原对比度的能力。MTF 值越接近 1，成像越锐利。通常以特定空间频率（如 50 lp/mm）下的 MTF 值评价镜头。",
    related: ["resolution", "contrast"],
  },
  contrast: {
    term: "对比度",
    explanation:
      "图像中明暗区域之间的亮度差异。高对比度有助于边缘检测和缺陷识别。MTF 下降会导致高频细节对比度降低。",
    related: ["mtf", "resolution"],
  },
  field_of_view: {
    term: "视场",
    explanation:
      "镜头在传感器上成像对应的实际物体区域大小。视场 = 传感器尺寸 / 放大倍率。需覆盖被测目标的完整轮廓。",
    related: ["magnification", "sensor_format", "working_distance"],
  },
  distortion: {
    term: "畸变",
    explanation:
      "镜头引起的成像几何变形，使直线在图像中呈弯曲状。分为枕形畸变（负）和桶形畸变（正）。精密测量需选择低畸变镜头或进行标定补偿。",
    related: ["calibration", "accuracy"],
  },
  calibration: {
    term: "标定",
    explanation:
      "通过标准图案（如棋盘格）建立像素坐标与世界坐标的映射关系，用于消除镜头畸变、确定放大倍率和主点位置。",
    related: ["distortion", "pixel_accuracy_mm"],
  },
  accuracy: {
    term: "测量精度",
    explanation:
      "检测结果与真值之间的接近程度。受像素精度、亚像素算法、镜头畸变、标定质量及环境振动等多因素共同影响。",
    related: ["pixel_accuracy_mm", "distortion", "calibration"],
  },
  mount: {
    term: "接口",
    explanation:
      "镜头与相机之间的机械连接标准（如 C-Mount、CS-Mount、F-Mount）。接口需匹配，且法兰距（Flange Distance）必须一致，否则无法合焦。",
    related: ["flange_distance"],
  },
  flange_distance: {
    term: "法兰距",
    explanation:
      "相机接口基准面到传感器感光面的距离。镜头的法兰距必须等于或适配相机的法兰距，否则需加装接圈（Extension Tube）补偿。",
    related: ["mount", "working_distance"],
  },
  c_mount: {
    term: "C 接口",
    explanation:
      "工业相机最常见的镜头接口，螺纹规格 1\"-32UN，法兰距 17.526 mm。与 CS 接口的区别在于法兰距多 5 mm，可通过 5 mm 接圈相互转换。",
    related: ["mount", "flange_distance", "cs_mount"],
  },
  cs_mount: {
    term: "CS 接口",
    explanation:
      "C 接口的短法兰距版本，法兰距 12.5 mm。CS 接口相机可配合 5 mm 接圈使用 C 接口镜头，反之则不行。",
    related: ["mount", "flange_distance", "c_mount"],
  },
  wavelength: {
    term: "波长",
    explanation:
      "光的电磁波波长（nm）。工业视觉常用可见光（400-700 nm）或近红外（NIR）。镜头设计针对特定波段优化，不同波长下的焦距和像差会略有变化。",
    related: ["chromatic_aberration"],
  },
  chromatic_aberration: {
    term: "色差",
    explanation:
      "不同波长光线通过镜头后聚焦位置不一致的现象，表现为物体边缘出现彩色镶边。复消色差（APO）镜头通过特殊玻璃组合显著降低色差。",
    related: ["wavelength", "apochromatic"],
  },
  apochromatic: {
    term: "复消色差",
    explanation:
      "APO（Apochromatic）镜头，将三种以上波长的光线校正到同一焦平面，色差控制远优于普通消色差镜头，适合高精度彩色或白光明场检测。",
    related: ["chromatic_aberration", "wavelength"],
  },
  telecentricity: {
    term: "远心度",
    explanation:
      "镜头主光线与光轴的平行程度。双侧远心镜头在物方和像方均为平行光路，可消除透视畸变和放大倍率随物距变化的问题，适合精密尺寸测量。",
    related: ["distortion", "magnification", "depth_of_field"],
  },
  coaxial_light: {
    term: "同轴光",
    explanation:
      "光源通过半透分光镜与镜头同轴出射，垂直照射被测面。适合镜面、光滑表面的缺陷检测，可消除阴影和反光干扰。",
    related: ["working_distance", "illumination"],
  },
  illumination: {
    term: "照明",
    explanation:
      "机器视觉系统中光源的选择与布置。照明方式（环形、条形、同轴、背光等）直接影响图像对比度和特征可检测性，需配合镜头工作距离和视场设计。",
    related: ["coaxial_light", "contrast"],
  },
};

export function lookupGlossary(key: string): GlossaryEntry | undefined {
  const normalized = key
    .toLowerCase()
    .replace(/\s+/g, "_")
    .replace(/[\-\/\\()]/g, "_");
  return OpticalGlossary[normalized];
}

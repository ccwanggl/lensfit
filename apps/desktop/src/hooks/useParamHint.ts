import { useLearningMode } from "../contexts/LearningModeContext";

/** Educational hints for optical parameters — shown in Learning Mode.
 *
 * These hints are intentionally independent of the backend domain definitions so
 * that every form (auto-generated or hand-written) can share the same learning
 * overlay. Keys map to the *frontend* parameter names used across pages.
 */
const PARAM_HINTS: Record<string, string> = {
  // Industrial vision
  sensor_size: "传感器物理尺寸（对角线）。尺寸越大，单个像素能收集的光子越多，画质通常越好。",
  pixel_size_um: "单个像素的物理边长（μm）。像元越小，同等面积像素数越多，但进光量和动态范围可能下降。",
  target_width_mm: "需要拍摄的区域在水平方向的物理宽度（mm）。与传感器尺寸和工作距离共同决定所需焦距。",
  target_height_mm: "需要拍摄的区域在垂直方向的物理宽度（mm）。",
  working_distance_mm: "镜头前端到被测物体的距离（mm）。WD、视场和传感器尺寸共同决定所需焦距。",
  lens_type: "镜头类型决定了光学设计目标：FA（通用工业）、Telecentric（无透视畸变，精密测量）、Macro（近距离高倍率）等。",
  interface: "机械安装接口。C-mount 最常用（法兰距17.5mm），F-mount 用于大面阵。接口不匹配无法安装。",
  focal_length_mm: "镜头焦距（mm）。焦距越短，视角越广；焦距越长，放大倍率越高。",
  f_number: "光圈值 F# = 焦距/入瞳直径。数字越小光圈越大，进光量越多，景深越浅。",

  // Photography
  sensor_format: "相机传感器尺寸（如全画幅、APS-C）。画幅影响视角、景深和系统体积。",
  purpose: "拍摄用途决定了对景深、视角、压缩感和重量的优先级。",
  focal_range: "期望的焦距范围。不同焦段对应不同的透视和构图风格。",
  max_aperture: "最大光圈。光圈越大，弱光能力越强，背景虚化越明显。",
  brand: "品牌偏好。不同厂商的镜头群、对焦系统和色彩风格各有特色。",
  mount: "镜头卡口。必须与相机机身卡口匹配，否则无法安装或自动对焦。",
  budget_usd: "预算上限（USD）。用于在候选方案中做成本约束。",

  // Microscopy
  microscope_type: "显微镜类型：复式（高倍率、数值孔径关键）或体视（低倍率、大景深、立体视觉）。",
  magnification: "系统总放大倍率 β = 像高/物高。显微镜中通常 >1，受物镜和传感器共同影响。",
  objective_na: "数值孔径 NA = n·sin(θ)。显微镜物镜最重要的参数，直接决定分辨率极限：d = 0.61λ/NA。",
  wavelength_nm: "照明光的波长（nm）。波长越短，衍射极限分辨率越高。可见光中心约 550nm（绿光）。",
  application: "应用场景。明场、荧光、相差等不同应用对 NA、波长和衬度要求不同。",

  // Infrared
  band: "红外波段：SWIR（短波红外，0.9–1.7μm）用于硅片检测；MWIR（3–5μm）用于高温；LWIR（8–14μm）用于常温热成像。",
  wavelength_um: "中心工作波长（μm）。不同材料在红外波段有不同的透射/反射特性。",
  fov_deg: "视场角（度）。由焦距和传感器尺寸共同决定：AFOV = (360/π)·arctan(s/2f)。",
  working_distance_m: "工作距离（m）。红外系统通常距离较远，需考虑大气吸收和镜头通光口径。",
  target_resolution_m: "目标空间分辨率（m）。决定需要识别的最小细节尺寸。",
  netd: "噪声等效温差（mK）。值越小，热像仪对温度差异越敏感。",
};

export interface ParamHintAPI {
  /** The hint string for a parameter, or undefined when Learning Mode is off. */
  hint: (name: string) => string | undefined;
  /** Whether Learning Mode is active and hints should be expanded inline. */
  expanded: boolean;
}

/** Return the educational hint API for parameters. */
export function useParamHint(): ParamHintAPI {
  const { learningMode } = useLearningMode();
  return {
    hint: (name: string) => (learningMode ? PARAM_HINTS[name] : undefined),
    expanded: learningMode,
  };
}

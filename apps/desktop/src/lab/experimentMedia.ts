/**
 * Optional rich media for optics experiments.
 *
 * The media is meant to be compact and supplemental: users can expand a
 * small "实验实操" strip to watch a related demonstration video or see a
 * real-world photo. Media is loaded lazily and never auto-plays.
 */

export interface ExperimentMedia {
  caption?: string;
  video?: {
    provider: "youtube";
    id: string;
    title?: string;
    start?: number;
  };
  image?: {
    src: string;
    alt: string;
    credit?: string;
  };
}

const YOUTUBE = (
  id: string,
  title: string,
  start?: number
): ExperimentMedia["video"] => ({ provider: "youtube", id, title, start });

const IMAGE = (src: string, alt: string, credit?: string): ExperimentMedia["image"] => ({
  src,
  alt,
  credit,
});

export const EXPERIMENT_MEDIA: Record<string, ExperimentMedia> = {
  "thin-lens": {
    caption: "用光具座测量凸透镜焦距的实操演示。",
    video: YOUTUBE("Xbqtj54b3fI", "Focal Length of a Converging Lens"),
  },
  "angle-of-view": {
    caption: "视角与焦距、传感器尺寸的关系示意图。",
    image: IMAGE(
      "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Angle_of_view.svg/640px-Angle_of_view.svg.png",
      "视角示意图",
      "Wikimedia Commons"
    ),
  },
  "depth-of-field": {
    caption: "实拍对比：不同光圈下的景深变化。",
    image: IMAGE(
      "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Shallow_depth_of_field_close-up_photography.jpg/640px-Shallow_depth_of_field_close-up_photography.jpg",
      "景深实拍",
      "Wikimedia Commons"
    ),
  },
  "magnification-scale": {
    caption: "显微镜/视觉系统中放大倍率的标定示意。",
    image: IMAGE(
      "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Magnification_diagram.svg/640px-Magnification_diagram.svg.png",
      "放大倍率示意",
      "Wikimedia Commons"
    ),
  },
  "sensor-coverage": {
    caption: "镜头像圈覆盖传感器示意图。",
    image: IMAGE(
      "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e2/Image_circle.svg/640px-Image_circle.svg.png",
      "像圈覆盖",
      "Wikimedia Commons"
    ),
  },
  "nyquist-sampling": {
    caption: "奈奎斯特采样与混叠示意。",
    image: IMAGE(
      "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Aliasing_after_downsampling.png/640px-Aliasing_after_downsampling.png",
      "采样混叠",
      "Wikimedia Commons"
    ),
  },
  "snell-refraction": {
    caption: "激光在糖度梯度水中的弯曲路径实验。",
    video: YOUTUBE("sft3QYZjNCU", "Bending Light with a Sugar Gradient"),
  },
  "double-slit": {
    caption: "杨氏双缝干涉经典演示。",
    video: YOUTUBE("Iuv6hY6zsd0", "The Original Double Slit Experiment"),
  },
  "single-slit-diffraction": {
    caption: "单缝衍射与中央亮纹宽度。",
    video: YOUTUBE("H79I3VgrnMk", "Single Slit Diffraction Explained"),
  },
  "grating": {
    caption: "衍射光栅分光实验。",
    video: YOUTUBE("cs-HGA1tsgo", "Diffraction Gratings"),
  },
  "diffraction": {
    caption: "夫琅禾费衍射与艾里斑。",
    video: YOUTUBE("sK08n-xtDc", "Diffraction, Gratings, Resolving Power"),
  },
  "chromatic-aberration": {
    caption: "轴向色差：蓝光与红光焦点不重合。",
    image: IMAGE(
      "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Chromatic_aberration_lens_diagram.svg/640px-Chromatic_aberration_lens_diagram.svg.png",
      "轴向色差光路",
      "Wikimedia Commons"
    ),
  },
  "aberration-spot": {
    caption: "像差造成的点扩散函数（光斑）。",
    image: IMAGE(
      "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Airy_disk.png/640px-Airy_disk.png",
      "艾里斑",
      "Wikimedia Commons"
    ),
  },
  "color-mixing": {
    caption: "加色法混色示意。",
    image: IMAGE(
      "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/RGB_color_model.svg/640px-RGB_color_model.svg.png",
      "RGB 加色混色",
      "Wikimedia Commons"
    ),
  },
  "blackbody": {
    caption: "黑体辐射谱随温度变化的实验演示。",
    video: YOUTUBE("r1OiMI9fQBs", "Black Body Radiation"),
  },
  "thermal-ifov-netd": {
    caption: "红外热像仪 IFOV 与 NETD 测量示意。",
    image: IMAGE(
      "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Thermal_imaging_camera.jpg/640px-Thermal_imaging_camera.jpg",
      "红外热成像",
      "Wikimedia Commons"
    ),
  },
  "mtf-explorer": {
    caption: "调制传递函数 MTF 的物理含义。",
    image: IMAGE(
      "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/MTF_of_optical_system.svg/640px-MTF_of_optical_system.svg.png",
      "MTF 曲线",
      "Wikimedia Commons"
    ),
  },
  "polarization-malus": {
    caption: "偏振片与马吕斯定律演示。",
    video: YOUTUBE("fsrq4RTHJvc", "Malus' Law Demonstration"),
  },
  "illumination-geometry": {
    caption: "机器视觉照明角度与缺陷成像。",
    image: IMAGE(
      "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Dark_field_illumination.svg/640px-Dark_field_illumination.svg.png",
      "暗场照明",
      "Wikimedia Commons"
    ),
  },
};

export function getExperimentMedia(id: string): ExperimentMedia | null {
  return EXPERIMENT_MEDIA[id] ?? null;
}

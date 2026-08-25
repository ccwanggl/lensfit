import type { LabExperiment, LabParameter } from "../utils/api";

export interface WorkbenchScene {
  version: 1;
  units: {
    length: "mm";
    angle: "deg";
    wavelength: "nm";
  };
  components: Array<{
    id: string;
    spec_id: "laser-monochrome" | "single-slit" | "double-slit" | "screen";
    category: "source" | "aperture" | "screen";
    transform: {
      x_mm: number;
      y_mm: number;
      rotation_deg: number;
    };
    params: Record<string, unknown>;
  }>;
  observables: Array<{
    type: "fraunhofer_intensity";
    source_id: string;
    aperture_id: string;
    screen_id: string;
  }>;
}

export interface RayOpticsSample {
  y_mm: number;
  intensity: number;
}

export interface RayOpticsData {
  available: boolean;
  samples?: RayOpticsSample[];
  image?: string;
  power?: number;
  normal?: number;
  warning?: string | null;
  error?: string;
}

export interface BreadboardPreset extends LabExperiment {
  kind: "preset";
  buildScene(params: Record<string, unknown>): WorkbenchScene;
}

export const BREADBOARD_PRESETS: BreadboardPreset[] = [
  {
    id: "single-slit-breadboard",
    title: "单缝衍射面包板",
    description:
      "在锁定布局的单缝衍射场景中调整波长、缝宽和屏幕位置，观察夫琅禾费衍射强度分布。",
    difficulty: "intermediate",
    linked_concepts: [
      "diffraction-limit",
    ],
    linked_formulas: ["single-slit-minima"],
    prerequisites: ["diffraction"],
    learning_objectives: [
      "理解单缝衍射中央亮纹宽度与缝宽成反比。",
      "观察波长越长、屏距越大，衍射展宽越明显。",
    ],
    parameters: [
      {
        name: "wavelength_nm",
        label: "波长",
        type: "float",
        default: 550,
        min: 380,
        max: 700,
        step: 10,
        unit: "nm",
      } as LabParameter,
      {
        name: "slit_width_um",
        label: "缝宽",
        type: "float",
        default: 50,
        min: 1,
        max: 500,
        step: 1,
        unit: "μm",
      } as LabParameter,
      {
        name: "screen_x_mm",
        label: "屏幕位置",
        type: "float",
        default: 1600,
        min: 700,
        max: 3000,
        step: 10,
        unit: "mm",
      } as LabParameter,
    ],
    kind: "preset",
    buildScene: (params) => {
      const screen_x_mm = Number(params.screen_x_mm ?? 1600);
      return {
        version: 1,
        units: { length: "mm", angle: "deg", wavelength: "nm" },
        components: [
          {
            id: "laser-1",
            spec_id: "laser-monochrome",
            category: "source",
            transform: { x_mm: 0, y_mm: 0, rotation_deg: 0 },
            params: { wavelength_nm: params.wavelength_nm },
          },
          {
            id: "slit-1",
            spec_id: "single-slit",
            category: "aperture",
            transform: { x_mm: 600, y_mm: 0, rotation_deg: 0 },
            params: { slit_width_um: params.slit_width_um },
          },
          {
            id: "screen-1",
            spec_id: "screen",
            category: "screen",
            transform: {
              x_mm: screen_x_mm,
              y_mm: 0,
              rotation_deg: 0,
            },
            params: {},
          },
        ],
        observables: [
          {
            type: "fraunhofer_intensity",
            source_id: "laser-1",
            aperture_id: "slit-1",
            screen_id: "screen-1",
          },
        ],
      };
    },
  },
  {
    id: "double-slit-breadboard",
    title: "双缝干涉面包板",
    description:
      "在锁定布局的双缝干涉场景中调整波长、缝宽、缝间距和屏幕位置，观察干涉条纹与单缝包络。",
    difficulty: "intermediate",
    linked_concepts: [
      "interference",
      "diffraction-limit",
    ],
    linked_formulas: ["double-slit-fringe-spacing"],
    prerequisites: ["single-slit-diffraction"],
    learning_objectives: [
      "理解条纹间距与缝间距成反比。",
      "观察单缝包络如何限制可见干涉条纹数目。",
    ],
    parameters: [
      {
        name: "wavelength_nm",
        label: "波长",
        type: "float",
        default: 550,
        min: 380,
        max: 700,
        step: 10,
        unit: "nm",
      } as LabParameter,
      {
        name: "slit_width_um",
        label: "缝宽",
        type: "float",
        default: 20,
        min: 1,
        max: 200,
        step: 1,
        unit: "μm",
      } as LabParameter,
      {
        name: "slit_separation_um",
        label: "缝间距",
        type: "float",
        default: 100,
        min: 10,
        max: 1000,
        step: 10,
        unit: "μm",
      } as LabParameter,
      {
        name: "screen_x_mm",
        label: "屏幕位置",
        type: "float",
        default: 1600,
        min: 700,
        max: 3000,
        step: 10,
        unit: "mm",
      } as LabParameter,
    ],
    kind: "preset",
    buildScene: (params) => {
      const screen_x_mm = Number(params.screen_x_mm ?? 1600);
      return {
        version: 1,
        units: { length: "mm", angle: "deg", wavelength: "nm" },
        components: [
          {
            id: "laser-1",
            spec_id: "laser-monochrome",
            category: "source",
            transform: { x_mm: 0, y_mm: 0, rotation_deg: 0 },
            params: { wavelength_nm: params.wavelength_nm },
          },
          {
            id: "slit-1",
            spec_id: "double-slit",
            category: "aperture",
            transform: { x_mm: 600, y_mm: 0, rotation_deg: 0 },
            params: {
              slit_width_um: params.slit_width_um,
              slit_separation_um: params.slit_separation_um,
            },
          },
          {
            id: "screen-1",
            spec_id: "screen",
            category: "screen",
            transform: {
              x_mm: screen_x_mm,
              y_mm: 0,
              rotation_deg: 0,
            },
            params: {},
          },
        ],
        observables: [
          {
            type: "fraunhofer_intensity",
            source_id: "laser-1",
            aperture_id: "slit-1",
            screen_id: "screen-1",
          },
        ],
      };
    },
  },
];


export const WAVELENGTH_PRESETS = [
  { label: "红", value: 650, color: "bg-red-500" },
  { label: "绿", value: 550, color: "bg-emerald-500" },
  { label: "蓝", value: 450, color: "bg-blue-500" },
];

export function getBreadboardPreset(id: string): BreadboardPreset | undefined {
  return BREADBOARD_PRESETS.find((p) => p.id === id);
}

export function isBreadboardPreset(id: string | null): boolean {
  if (!id) return false;
  return BREADBOARD_PRESETS.some((p) => p.id === id);
}

export function validatePresetParams(
  presetId: string,
  params: Record<string, unknown>
): string | null {
  if (
    presetId === "single-slit-breadboard" ||
    presetId === "double-slit-breadboard"
  ) {
    const screen_x_mm = Number(params.screen_x_mm ?? 1100);
    if (!Number.isFinite(screen_x_mm)) {
      return "屏幕位置必须是有效数字";
    }
    if (screen_x_mm <= 700) {
      return "屏幕必须位于光阑之后";
    }
  }
  if (presetId === "double-slit-breadboard") {
    const slit_width_um = Number(params.slit_width_um ?? 20);
    const slit_separation_um = Number(params.slit_separation_um ?? 100);
    if (
      Number.isFinite(slit_width_um) &&
      Number.isFinite(slit_separation_um) &&
      slit_separation_um <= slit_width_um
    ) {
      return "缝间距必须大于缝宽";
    }
  }
  return null;
}

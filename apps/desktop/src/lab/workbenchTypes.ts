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
    spec_id: "laser-monochrome" | "single-slit" | "screen";
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

export interface BreadboardPreset extends LabExperiment {
  kind: "preset";
  buildScene(params: Record<string, unknown>): WorkbenchScene;
}

export const BREADBOARD_PRESETS: BreadboardPreset[] = [
  {
    id: "single-slit-breadboard",
    title: "单缝衍射面包板",
    description:
      "在锁定布局的单缝衍射场景中调整波长、缝宽和屏距，观察夫琅禾费衍射强度分布。",
    difficulty: "intermediate",
    linked_concepts: [
      "10-concepts/diffraction-limit",
      "10-concepts/衍射极限",
    ],
    linked_formulas: ["20-formulas/single-slit-minima"],
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
        name: "screen_distance_m",
        label: "屏距",
        type: "float",
        default: 1.0,
        min: 0.05,
        max: 5.0,
        step: 0.05,
        unit: "m",
      } as LabParameter,
    ],
    kind: "preset",
    buildScene: (params) => {
      const distance_mm = Number(params.screen_distance_m ?? 1.0) * 1000;
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
            transform: { x_mm: 100, y_mm: 0, rotation_deg: 0 },
            params: { slit_width_um: params.slit_width_um },
          },
          {
            id: "screen-1",
            spec_id: "screen",
            category: "screen",
            transform: {
              x_mm: 100 + distance_mm,
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

export function getBreadboardPreset(id: string): BreadboardPreset | undefined {
  return BREADBOARD_PRESETS.find((p) => p.id === id);
}

export function isBreadboardPreset(id: string | null): boolean {
  if (!id) return false;
  return BREADBOARD_PRESETS.some((p) => p.id === id);
}

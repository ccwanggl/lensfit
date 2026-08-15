import { describe, expect, it } from "vitest";
import {
  getBreadboardPreset,
  isBreadboardPreset,
  validatePresetParams,
} from "./workbenchTypes";

describe("validatePresetParams", () => {
  describe("单缝面包板", () => {
    it("合法参数返回 null", () => {
      expect(
        validatePresetParams("single-slit-breadboard", {
          wavelength_nm: 550,
          slit_width_um: 50,
          screen_x_mm: 1600,
        })
      ).toBeNull();
    });

    it("缺省参数使用默认值，返回 null", () => {
      expect(validatePresetParams("single-slit-breadboard", {})).toBeNull();
    });

    it("screen_x_mm 等于 700 时拒绝（屏幕必须位于光阑之后）", () => {
      expect(
        validatePresetParams("single-slit-breadboard", { screen_x_mm: 700 })
      ).toBe("屏幕必须位于光阑之后");
    });

    it("screen_x_mm 小于 700 时拒绝", () => {
      expect(
        validatePresetParams("single-slit-breadboard", { screen_x_mm: 100 })
      ).toBe("屏幕必须位于光阑之后");
    });

    it("screen_x_mm 略大于 700 时通过（边界值）", () => {
      expect(
        validatePresetParams("single-slit-breadboard", { screen_x_mm: 700.1 })
      ).toBeNull();
    });

    it("screen_x_mm 不是有效数字时拒绝", () => {
      expect(
        validatePresetParams("single-slit-breadboard", {
          screen_x_mm: "not-a-number",
        })
      ).toBe("屏幕位置必须是有效数字");
    });

    it("screen_x_mm 为 Infinity 时拒绝", () => {
      expect(
        validatePresetParams("single-slit-breadboard", {
          screen_x_mm: Infinity,
        })
      ).toBe("屏幕位置必须是有效数字");
    });
  });

  describe("双缝面包板", () => {
    it("缝间距大于缝宽时通过", () => {
      expect(
        validatePresetParams("double-slit-breadboard", {
          slit_width_um: 20,
          slit_separation_um: 100,
          screen_x_mm: 1600,
        })
      ).toBeNull();
    });

    it("缝间距等于缝宽时拒绝（边界值）", () => {
      expect(
        validatePresetParams("double-slit-breadboard", {
          slit_width_um: 100,
          slit_separation_um: 100,
          screen_x_mm: 1600,
        })
      ).toBe("缝间距必须大于缝宽");
    });

    it("缝间距小于缝宽时拒绝", () => {
      expect(
        validatePresetParams("double-slit-breadboard", {
          slit_width_um: 200,
          slit_separation_um: 100,
          screen_x_mm: 1600,
        })
      ).toBe("缝间距必须大于缝宽");
    });

    it("同时违反屏幕位置约束时优先返回屏幕错误", () => {
      expect(
        validatePresetParams("double-slit-breadboard", {
          slit_width_um: 200,
          slit_separation_um: 100,
          screen_x_mm: 500,
        })
      ).toBe("屏幕必须位于光阑之后");
    });

    it("缝宽/缝间距不是有效数字时跳过缝几何校验", () => {
      expect(
        validatePresetParams("double-slit-breadboard", {
          slit_width_um: "abc",
          slit_separation_um: 100,
          screen_x_mm: 1600,
        })
      ).toBeNull();
    });
  });

  it("非面包板 preset id 不做校验，返回 null", () => {
    expect(validatePresetParams("some-other-experiment", {})).toBeNull();
  });
});

describe("preset 查询辅助函数", () => {
  it("getBreadboardPreset 能找到已知 preset", () => {
    expect(getBreadboardPreset("single-slit-breadboard")?.id).toBe(
      "single-slit-breadboard"
    );
  });

  it("getBreadboardPreset 对未知 id 返回 undefined", () => {
    expect(getBreadboardPreset("nope")).toBeUndefined();
  });

  it("isBreadboardPreset 正确识别 preset id", () => {
    expect(isBreadboardPreset("double-slit-breadboard")).toBe(true);
    expect(isBreadboardPreset("nope")).toBe(false);
    expect(isBreadboardPreset(null)).toBe(false);
  });
});

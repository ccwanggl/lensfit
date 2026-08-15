import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { BreadboardPresetHeader } from "./LearningHub";

const defaultParams = {
  wavelength_nm: 550,
  slit_width_um: 50,
  screen_x_mm: 1600,
};

describe("BreadboardPresetHeader", () => {
  it("渲染波长切换按钮与面包板示意图", () => {
    render(
      <BreadboardPresetHeader
        presetId="single-slit-breadboard"
        params={defaultParams}
        onChange={() => {}}
      />
    );

    expect(screen.getByRole("button", { name: "红" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "绿" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "蓝" })).toBeInTheDocument();
    expect(screen.getByText("面包板示意")).toBeInTheDocument();
    expect(screen.getByText("激光")).toBeInTheDocument();
    expect(screen.getByText("单缝")).toBeInTheDocument();
    expect(screen.getByText("屏幕")).toBeInTheDocument();
  });

  it("双缝 preset 显示双缝标注", () => {
    render(
      <BreadboardPresetHeader
        presetId="double-slit-breadboard"
        params={defaultParams}
        onChange={() => {}}
      />
    );

    expect(screen.getByText("双缝")).toBeInTheDocument();
    expect(screen.queryByText("单缝")).not.toBeInTheDocument();
  });

  it("点击波长按钮触发 onChange", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(
      <BreadboardPresetHeader
        presetId="single-slit-breadboard"
        params={defaultParams}
        onChange={onChange}
      />
    );

    await user.click(screen.getByRole("button", { name: "红" }));
    expect(onChange).toHaveBeenCalledWith("wavelength_nm", 650);

    await user.click(screen.getByRole("button", { name: "蓝" }));
    expect(onChange).toHaveBeenCalledWith("wavelength_nm", 450);
  });

  it("当前波长对应的按钮处于高亮态", () => {
    render(
      <BreadboardPresetHeader
        presetId="single-slit-breadboard"
        params={defaultParams}
        onChange={() => {}}
      />
    );

    expect(screen.getByRole("button", { name: "绿" }).className).toContain(
      "bg-indigo-50"
    );
    expect(screen.getByRole("button", { name: "红" }).className).not.toContain(
      "bg-indigo-50"
    );
  });

  it("屏幕位置超出上限时示意图按 3000mm 截断", () => {
    const { container } = render(
      <BreadboardPresetHeader
        presetId="single-slit-breadboard"
        params={{ ...defaultParams, screen_x_mm: 5000 }}
        onChange={() => {}}
      />
    );

    // clamp 到 3000 → screenSvgX = 40 + (2300/2300)*220 = 260
    const screenLines = container.querySelectorAll('line[x1="260"]');
    expect(screenLines.length).toBe(1);
  });

  it("屏幕位置低于下限时示意图按 700mm 截断", () => {
    const { container } = render(
      <BreadboardPresetHeader
        presetId="single-slit-breadboard"
        params={{ ...defaultParams, screen_x_mm: 100 }}
        onChange={() => {}}
      />
    );

    // clamp 到 700 → screenSvgX = 40
    const screenLines = container.querySelectorAll('line[x1="40"]');
    expect(screenLines.length).toBeGreaterThan(0);
  });
});

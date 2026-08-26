/** C-0 characterization smoke: MicroscopePage renders its form column unmounted-safe. */
import "@testing-library/jest-dom/vitest";
import { describe, expect, it, vi } from "vitest";

vi.mock("../utils/api", () =>
  import("../test-utils/mockApi").then((m) => m.buildApiMock())
);

import { screen } from "@testing-library/react";
import MicroscopePage from "./MicroscopePage";
import { renderPage } from "../test-utils/renderPage";

describe("MicroscopePage 冒烟（切片C-0表征测试）", () => {
  it("初始渲染出表单列标题与副标题", async () => {
    renderPage(<MicroscopePage />);
    expect(await screen.findByText("显微镜参数")).toBeInTheDocument();
    expect(screen.getByText("配置显微成像系统需求")).toBeInTheDocument();
  });
});

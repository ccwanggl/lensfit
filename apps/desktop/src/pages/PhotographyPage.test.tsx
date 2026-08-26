/** C-0 characterization smoke: PhotographyPage renders its form column unmounted-safe. */
import "@testing-library/jest-dom/vitest";
import { describe, expect, it, vi } from "vitest";

vi.mock("../utils/api", () =>
  import("../test-utils/mockApi").then((m) => m.buildApiMock())
);

import { screen } from "@testing-library/react";
import PhotographyPage from "./PhotographyPage";
import { renderPage } from "../test-utils/renderPage";

describe("PhotographyPage 冒烟（切片C-0表征测试）", () => {
  it("初始渲染出表单列标题与副标题", async () => {
    renderPage(<PhotographyPage />);
    expect(await screen.findByText("摄影参数")).toBeInTheDocument();
    expect(screen.getByText("配置您的摄影系统需求")).toBeInTheDocument();
  });
});

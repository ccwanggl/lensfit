/** C-0 characterization smoke: InfraredPage renders its form column unmounted-safe. */
import "@testing-library/jest-dom/vitest";
import { describe, expect, it, vi } from "vitest";

vi.mock("../utils/api", () =>
  import("../test-utils/mockApi").then((m) => m.buildApiMock())
);

import { screen } from "@testing-library/react";
import InfraredPage from "./InfraredPage";
import { renderPage } from "../test-utils/renderPage";

describe("InfraredPage 冒烟（切片C-0表征测试）", () => {
  it("初始渲染出表单列标题与副标题", async () => {
    renderPage(<InfraredPage />);
    expect(await screen.findByText("红外参数")).toBeInTheDocument();
    expect(screen.getByText("配置红外成像系统需求")).toBeInTheDocument();
  });
});

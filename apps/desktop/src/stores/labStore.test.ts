import { beforeEach, describe, expect, it } from "vitest";
import { useLabStore } from "./labStore";

const STORAGE_KEY = "lensfit-lab-store";

beforeEach(() => {
  localStorage.clear();
  useLabStore.setState({
    activeExperimentId: null,
    paramDrafts: {},
    sceneDrafts: {},
    showDataPanel: true,
    showSidebar: true,
    recentExperiments: [],
  });
});

describe("sceneDrafts 草稿读写", () => {
  it("setSceneDraft 保存草稿并可读取", () => {
    useLabStore
      .getState()
      .setSceneDraft("single-slit-breadboard", { wavelength_nm: 650 });

    expect(
      useLabStore.getState().sceneDrafts["single-slit-breadboard"]
    ).toEqual({ wavelength_nm: 650 });
  });

  it("setSceneDraft 增量合并同一 preset 的参数", () => {
    const { setSceneDraft } = useLabStore.getState();
    setSceneDraft("single-slit-breadboard", { wavelength_nm: 650 });
    setSceneDraft("single-slit-breadboard", { slit_width_um: 80 });

    expect(
      useLabStore.getState().sceneDrafts["single-slit-breadboard"]
    ).toEqual({ wavelength_nm: 650, slit_width_um: 80 });
  });

  it("不同 preset 的草稿互不影响", () => {
    const { setSceneDraft } = useLabStore.getState();
    setSceneDraft("single-slit-breadboard", { wavelength_nm: 650 });
    setSceneDraft("double-slit-breadboard", { wavelength_nm: 450 });

    const drafts = useLabStore.getState().sceneDrafts;
    expect(drafts["single-slit-breadboard"]).toEqual({ wavelength_nm: 650 });
    expect(drafts["double-slit-breadboard"]).toEqual({ wavelength_nm: 450 });
  });

  it("resetSceneDraft 删除指定 preset 的草稿", () => {
    const { setSceneDraft, resetSceneDraft } = useLabStore.getState();
    setSceneDraft("single-slit-breadboard", { wavelength_nm: 650 });
    setSceneDraft("double-slit-breadboard", { wavelength_nm: 450 });

    resetSceneDraft("single-slit-breadboard");

    const drafts = useLabStore.getState().sceneDrafts;
    expect(drafts["single-slit-breadboard"]).toBeUndefined();
    expect(drafts["double-slit-breadboard"]).toEqual({ wavelength_nm: 450 });
  });

  it("草稿持久化到 localStorage", () => {
    useLabStore
      .getState()
      .setSceneDraft("single-slit-breadboard", { wavelength_nm: 650 });

    const raw = localStorage.getItem(STORAGE_KEY);
    expect(raw).not.toBeNull();
    const persisted = JSON.parse(raw!) as {
      state: { sceneDrafts: Record<string, Record<string, unknown>> };
    };
    expect(persisted.state.sceneDrafts["single-slit-breadboard"]).toEqual({
      wavelength_nm: 650,
    });
  });
});

describe("localStorage 数据恢复", () => {
  it("合法的持久化 JSON 在 rehydrate 后恢复草稿", async () => {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        state: {
          sceneDrafts: {
            "single-slit-breadboard": { wavelength_nm: 450 },
          },
          paramDrafts: {},
          recentExperiments: [],
          showDataPanel: true,
          showSidebar: false,
        },
        version: 0,
      })
    );

    await useLabStore.persist.rehydrate();

    expect(
      useLabStore.getState().sceneDrafts["single-slit-breadboard"]
    ).toEqual({ wavelength_nm: 450 });
    expect(useLabStore.getState().showSidebar).toBe(false);
  });

  it("损坏的 JSON 降级为当前内存状态，不抛异常", async () => {
    localStorage.setItem(STORAGE_KEY, "{broken-json");

    await expect(useLabStore.persist.rehydrate()).resolves.toBeUndefined();

    // 状态保持内存中的默认值
    expect(useLabStore.getState().sceneDrafts).toEqual({});
  });

  it("持久化内容不是对象时降级为默认值", async () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify("just a string"));

    await expect(useLabStore.persist.rehydrate()).resolves.toBeUndefined();

    expect(useLabStore.getState().sceneDrafts).toEqual({});
  });
});

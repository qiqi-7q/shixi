import { defineStore } from "pinia";
import { type dashboardType, store } from "../utils";
import { getCurrentProjects, getVehicleModels, getVinList } from "@/api/system";
export const useDashboardStore = defineStore("dashboardList", {
  state: (): dashboardType => ({
    projectOptions: [],
    modelOptions: [],
    vinOptions: []
  }),
  getters: {
    getProjectOptions(state) {
      return state.projectOptions;
    },
    getModelOptions(state) {
      return state.modelOptions;
    },
    getVinOptions(state) {
      return state.vinOptions;
    }
  },
  actions: {
    async SET_PROJECT_OPTIONS() {
      try {
        const res: any = await getCurrentProjects();
        if (res.code === 200 && res.data) {
          this.projectOptions = res.data;
        }
      } catch (e) {
        console.error("加载项目列表失败", e);
      }
    },
    async SET_MODEL_OPTIONS() {
      try {
        const res: any = await getVehicleModels();
        if (res.data) {
          this.modelOptions = res.data;
        }
      } catch (e) {
        console.error("加载车型列表失败", e);
      }
    },
    async SET_VIN_OPTIONS() {
      try {
        const res: any = await getVinList();
        if (res.data) {
          this.vinOptions = res.data;
        }
      } catch (e) {
        console.error("加载VIN列表失败", e);
      }
    }
  }
});
export function useDashboardStoreHook() {
  return useDashboardStore(store);
}

import axios from "axios";
import type { App } from "vue";

let config: object = {};
const { VITE_PUBLIC_PATH } = import.meta.env;

const setConfig = (cfg?: unknown) => {
  config = Object.assign(config, cfg);
};

const getConfig = (key?: string): PlatformConfigs => {
  if (typeof key === "string") {
    const arr = key.split(".");
    if (arr && arr.length) {
      let data = config;
      arr.forEach(v => {
        if (data && typeof data[v] !== "undefined") {
          data = data[v];
        } else {
          data = null;
        }
      });
      return data;
    }
  }
  return config;
};

/** 获取项目动态全局配置 */
export const getPlatformConfig = async (app: App): Promise<PlatformConfigs> => {
  app.config.globalProperties.$config = getConfig();

  const defaultConfig: PlatformConfigs = {
    Version: "6.2.0",
    Title: "自动化管理平台",
    FixedHeader: true,
    HiddenSideBar: false,
    MultiTagsCache: false,
    KeepAlive: true,
    Layout: "vertical",
    Theme: "light",
    DarkMode: false,
    OverallStyle: "light",
    Grey: false,
    Weak: false,
    HideTabs: false,
    HideFooter: false,
    Stretch: false,
    SidebarStatus: true,
    EpThemeColor: "#409EFF",
    ShowLogo: true,
    ShowModel: "smart",
    MenuArrowIconNoTransition: false,
    CachingAsyncRoutes: false,
    TooltipEffect: "light",
    ResponsiveStorageNameSpace: "responsive-",
    MenuSearchHistory: 6
  };

  try {
    const { data: config } = await axios({
      method: "get",
      url: `${VITE_PUBLIC_PATH}platform-config.json`,
      timeout: 3000
    });

    let $config = app.config.globalProperties.$config;
    if (app && $config && typeof config === "object") {
      $config = Object.assign($config, config);
      app.config.globalProperties.$config = $config;
      setConfig($config);
      return $config;
    }
  } catch (error) {
    console.warn("platform-config.json 加载失败，使用默认配置:", error);
    setConfig(defaultConfig);
  }

  return defaultConfig;
};

/** 本地响应式存储的命名空间 */
const responsiveStorageNameSpace = () => getConfig().ResponsiveStorageNameSpace;

export { getConfig, setConfig, responsiveStorageNameSpace };

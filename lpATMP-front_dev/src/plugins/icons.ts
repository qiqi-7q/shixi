// 注册 Element Plus 图标集合到本地（离线可用）
import { addCollection } from "@iconify/vue/dist/offline";
import epIcons from "@iconify/json/json/ep.json";

// 同步注册 ep 图标集合
addCollection(epIcons);

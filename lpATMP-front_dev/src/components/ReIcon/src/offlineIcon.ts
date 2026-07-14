// 这里存放本地图标，在 src/layout/index.vue 文件中加载，避免在首启动加载
import { getSvgInfo } from "@pureadmin/utils";
import { addIcon } from "@iconify/vue/dist/offline";

// https://icon-sets.iconify.design/ep/?keyword=ep
import EpHomeFilled from "~icons/ep/home-filled?raw";
import EpNotebook from "~icons/ep/notebook?raw";
import EpVan from "~icons/ep/van?raw";
import EpMapLocation from "~icons/ep/map-location?raw";
import EpList from "~icons/ep/list?raw";
import EpUser from "~icons/ep/user?raw";
import EpAvatar from "~icons/ep/avatar?raw";
import EpDocument from "~icons/ep/document?raw";
import EpTickets from "~icons/ep/tickets?raw";
import EpOdometer from "~icons/ep/odometer?raw";
import EpDataAnalysis from "~icons/ep/data-analysis?raw";
import EpPieChart from "~icons/ep/pie-chart?raw";
import EpHistogram from "~icons/ep/histogram?raw";
import EpTrendCharts from "~icons/ep/trend-charts?raw";
import EpPosition from "~icons/ep/position?raw";
import EpLock from "~icons/ep/lock?raw";
import EpMenu from "~icons/ep/menu?raw";
import EpLollipop from "~icons/ep/lollipop?raw";
import EpDocumentChecked from "~icons/ep/document-checked?raw";
import EpUserFilled from "~icons/ep/user-filled?raw";
import EpMoreFilled from "~icons/ep/more-filled?raw";
import EpSort from "~icons/ep/sort?raw";
import EpPostcard from "~icons/ep/postcard?raw";
import EpGrid from "~icons/ep/grid?raw";
import EpDataBoard from "~icons/ep/data-board?raw";
import EpSetting from "~icons/ep/setting?raw";
import EpReading from "~icons/ep/reading?raw";
import EpConnection from "~icons/ep/connection?raw";
// https://icon-sets.iconify.design/ri/?keyword=ri
import RiSearchLine from "~icons/ri/search-line?raw";

import RiInformationLine from "~icons/ri/information-line?raw";
import EpCalendar from "~icons/ep/calendar?raw";
import EpMonitor from "~icons/ep/monitor?raw";
import EpPromotion from "~icons/ep/promotion?raw";
import EpRank from "~icons/ep/rank?raw";
const icons = [
  ["ep/rank", EpRank],
  // Element Plus Icon: https://github.com/element-plus/element-plus-icons
  ["ep/home-filled", EpHomeFilled],
  ["ep/notebook", EpNotebook],
  ["ep/promotion", EpPromotion],
  ["ep/map-location", EpMapLocation],
  ["ep/list", EpList],
  ["ep/user", EpUser],
  ["ep/van", EpVan],
  ["ep/avatar", EpAvatar],
  ["ep/document", EpDocument],
  ["ep/monitor", EpMonitor],
  ["ep/tickets", EpTickets],
  ["ep/odometer", EpOdometer],
  ["ep/data-analysis", EpDataAnalysis],
  ["ep/pie-chart", EpPieChart],
  ["ep/histogram", EpHistogram],
  ["ep/trend-charts", EpTrendCharts],
  ["ep/position", EpPosition],
  ["ep/lock", EpLock],
  ["ep/menu", EpMenu],
  ["ep/lollipop", EpLollipop],
  ["ep/document-checked", EpDocumentChecked],
  ["ep/user-filled", EpUserFilled],
  ["ep/more-filled", EpMoreFilled],
  ["ep/sort", EpSort],
  ["ep/postcard", EpPostcard],
  ["ep/grid", EpGrid],
  ["ep/data-board", EpDataBoard],
  // Remix Icon: https://github.com/Remix-Design/RemixIcon
  ["ri/search-line", RiSearchLine],
  ["ri/information-line", RiInformationLine],
  ["ep/setting", EpSetting],
  ["ep/reading", EpReading],
  ["ep/connection", EpConnection],
  ["ep/calendar", EpCalendar]
];

// 本地菜单图标，后端在路由的 icon 中返回对应的图标字符串并且前端在此处使用 addIcon 添加即可渲染菜单图标
icons.forEach(([name, icon]) => {
  addIcon(name as string, getSvgInfo(icon as string));
});

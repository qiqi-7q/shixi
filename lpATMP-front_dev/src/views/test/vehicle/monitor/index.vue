<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from "vue";
import * as echarts from "echarts";
import { PureTableBar } from "@/components/RePureTableBar";
import { useRenderIcon } from "@/components/ReIcon/src/hooks";
import { ReAdvancedSearch } from "@/components/ReAdvancedSearch";
import type { SelectOption } from "@/components/ReAdvancedSearch";
import {
  getVehicleModels,
  getUsagesByDate,
  getDistancesByDate
} from "@/api/system";
import Plus from "~icons/ep/plus";
import Refresh from "~icons/ep/refresh";
import View from "~icons/ep/view";
import Edit from "~icons/ep/edit";
import Delete from "~icons/ep/delete";
import ArrowDown from "~icons/ep/arrow-down";
import MapLocation from "~icons/ep/map-location";
import QuestionFilled from "~icons/ep/question-filled";
import { markRaw } from "vue";

import MonitorDialog from "./dialog.vue";
import VehicleMap from "./VehicleMap.vue";
import { useMonitor } from "./hook";

defineOptions({
  name: "VehicleMonitor"
});

const {
  formRef,
  tableRef,
  advancedSearchRef,
  monitorDialogRef,
  form,
  loading,
  columns,
  dataList,
  pagination,
  selectedNum,
  statistics,
  advancedFilters,
  onSearch,
  handleReset,
  handleSortChange,
  handleSelectionChange,
  handleSizeChange,
  handleCurrentChange,
  onSelectionCancel,
  onAdd,
  onEdit,
  onDetail,
  onDelete,
  onbatchDel,
  handleCommand,
  onSave,
  getCarInfo,
  getGroups,
  getVinList,
  getCarInfoByVin
} = useMonitor();

const modelOptions = ref<string[]>([]);
const vinOptions = ref<string[]>([]);
const chartVin = ref("");
const chartModel = ref("");
let vinSearchTimer: ReturnType<typeof setTimeout> | null = null;

async function fetchModelOptions() {
  try {
    const res: any = await getVehicleModels();
    if (res.data) {
      modelOptions.value = markRaw(res.data);
      if (res.data.length > 0) {
        chartModel.value = res.data[0];
      }
    }
  } catch (e) {}
}

async function fetchVinOptions(keyword?: string) {
  try {
    const res: any = await getVinList(keyword);
    if (res.data) {
      vinOptions.value = markRaw(res.data);
      if (res.data.length > 0 && !keyword) {
        chartVin.value = res.data[0];
      }
    }
  } catch (e) {}
}

function handleVinSearch(query: string) {
  if (vinSearchTimer) clearTimeout(vinSearchTimer);
  vinSearchTimer = setTimeout(() => {
    fetchVinOptions(query);
  }, 200);
}

function handleVinFilter(query: string) {
  handleVinSearch(query);
}

function handleVinVisibleChange(visible: boolean) {
  if (visible) {
    handleVinSearch("");
  }
}

onMounted(async () => {
  fetchModelOptions();
  fetchVinOptions();
  // 默认日期为昨天;
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  const yesterdayStr = yesterday.toISOString().split("T")[0];
  if (!ladderDate.value || ladderDate.value.length === 0) {
    ladderDate.value = [yesterdayStr, yesterdayStr];
  }
  if (!distanceLadderDate.value || distanceLadderDate.value.length === 0) {
    distanceLadderDate.value = [yesterdayStr, yesterdayStr];
  }
  await nextTick();
  await fetchChartData(); // 先渲染前两个图表

  await nextTick();
  await fetchLadderData(); // 再渲染第三个

  await nextTick();
  await fetchDistanceLadderData();
  window.addEventListener("resize", handleResize);
});

const mapVisible = ref(false);
const vehicleMapRef = ref();

const onMapDialogOpened = () => {
  vehicleMapRef.value?.resize();
};

const filterFieldOptions = computed<SelectOption[]>(() =>
  columns
    .filter((col: any) => col.prop && col.label)
    .map((col: any) => ({ label: col.label, value: col.prop }))
);

// 图表相关
const carInfoChartRef = ref<HTMLElement>();
const carInfoDurationChartRef = ref<HTMLElement>();
const groupsChartRef = ref<HTMLElement>();
const ladderChartRef = ref<HTMLElement>();
const distanceLadderChartRef = ref<HTMLElement>();
let carInfoChartInstance: echarts.ECharts | null = null;
let carInfoDurationChartInstance: echarts.ECharts | null = null;
let groupsChartInstance: echarts.ECharts | null = null;
let ladderChartInstance: echarts.ECharts | null = null;
let distanceLadderChartInstance: echarts.ECharts | null = null;

const ladderDate = ref<string[]>([]);
const distanceLadderDate = ref<string[]>([]);
const ladderModel = ref<string[]>([]);
const distanceLadderModel = ref<string[]>([]);

// 图表loading状态
const carInfoChartLoading = ref(false);
const carInfoDurationChartLoading = ref(false);
const groupsChartLoading = ref(false);
const ladderChartLoading = ref(false);
const distanceLadderChartLoading = ref(false);

const fetchChartData = async () => {
  carInfoChartLoading.value = true;
  carInfoDurationChartLoading.value = true;
  groupsChartLoading.value = true;
  try {
    // 第一个图表：根据VIN查询单车信息
    let carInfoRes: any;
    if (chartVin.value) {
      carInfoRes = await getCarInfoByVin(chartVin.value);
    } else {
      carInfoRes = { data: [] };
    }

    // 第二个图表：根据车型查询组别使用率
    let groupsRes: any;
    if (chartModel.value) {
      groupsRes = await getGroups({ model: chartModel.value });
    } else {
      groupsRes = { data: [] };
    }

    await nextTick();
    renderCarInfoChart(carInfoRes?.data || []);
    renderGroupsChart(groupsRes?.data || []);
  } catch (error) {
    console.error("获取图表数据失败:", error);
  } finally {
    carInfoChartLoading.value = false;
    carInfoDurationChartLoading.value = false;
    groupsChartLoading.value = false;
  }
};

const renderCarInfoChart = (data: any[]) => {
  if (!carInfoChartRef.value) return;

  if (!carInfoChartInstance) {
    carInfoChartInstance = echarts.init(carInfoChartRef.value);
  }

  console.log("📊 使用率图表原始数据:", data.length, "条");

  const dates = [...new Set(data.map(item => item.monitor_date))].sort();
  console.log("📅 日期列表:", dates);

  // 单车查询没有 model 字段，使用 vin_code 作为标识
  const vinCode = data.length > 0 ? data[0].vin_code : "";
  const allModels = vinCode ? [vinCode] : [];
  console.log(" 标识:", allModels);

  const modelDateMap: Record<
    string,
    Record<string, { power_duration: number; usage: number; distance: number }>
  > = {};

  data.forEach(item => {
    const key = item.model || item.vin_code || "unknown";
    if (!modelDateMap[key]) {
      modelDateMap[key] = {};
    }
    if (!modelDateMap[key][item.monitor_date]) {
      modelDateMap[key][item.monitor_date] = {
        power_duration: 0,
        usage: 0,
        distance: 0
      };
    }

    const pd =
      item.power_duration !== undefined && item.power_duration !== null
        ? Number(item.power_duration)
        : 0;
    const us =
      item.usage !== undefined && item.usage !== null ? Number(item.usage) : 0;
    const dist =
      item.distance !== undefined && item.distance !== null
        ? Number(item.distance)
        : 0;

    modelDateMap[key][item.monitor_date].power_duration += pd;
    modelDateMap[key][item.monitor_date].usage += us;
    modelDateMap[key][item.monitor_date].distance += dist;
  });

  const totalUsage = allModels.map(m =>
    dates.map(d => {
      const info = modelDateMap[m]?.[d];
      return info ? Number(info.usage.toFixed(2)) : 0;
    })
  );

  const totalPowerDuration = allModels.map(m =>
    dates.map(d => {
      const info = modelDateMap[m]?.[d];
      return info ? Number(info.power_duration.toFixed(2)) : 0;
    })
  );
  const totalDistance = allModels.map(m =>
    dates.map(d => {
      const info = modelDateMap[m]?.[d];
      return info ? Number(info.distance.toFixed(1)) : 0;
    })
  );

  console.log(`📈 数据处理完成:`, {
    车型数: allModels.length,
    日期数: dates.length
  });

  const defaultEnd =
    dates.length > 7 ? Math.round((7 / dates.length) * 100) : 100;

  // ====== 使用率折线图 ======
  carInfoChartInstance.setOption({
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "cross" },
      backgroundColor: "rgba(255,255,255,0.95)",
      borderColor: "#eee",
      borderWidth: 1,
      textStyle: { color: "#333", fontSize: 12 },
      formatter: (params: any) => {
        if (!params?.length) return "";
        let result = `<div style="font-weight:bold;margin-bottom:8px">${params[0].axisValue}</div>`;
        params.forEach((item: any) => {
          if (item && item.value !== undefined) {
            result += `<div style="margin:4px 0">${item.marker} <b>${item.seriesName}</b>: <span style="color:#409eff;font-weight:bold">${item.value}%</span></div>`;
          }
        });
        return result;
      }
    },
    legend: {
      data: allModels.map(m => `使用率(%)`),
      top: 5,
      right: 10,
      textStyle: { fontSize: 11 },
      icon: "roundRect",
      itemWidth: 20,
      itemHeight: 8
    },
    grid: { left: 70, right: 30, top: 35, bottom: 100 },
    xAxis: {
      type: "category",
      data: dates,
      axisLabel: {
        rotate: 30,
        fontSize: 11,
        interval: 0,
        color: "#909399",
        formatter: (value: string) => value.slice(5).replace("-", "/")
      },
      axisLine: { lineStyle: { color: "#ebeef5" } },
      axisTick: { alignWithLabel: true, length: 6 }
    },
    yAxis: {
      type: "value",
      name: "使用率 (%)",
      min: 0,
      max: 100,
      axisLabel: {
        formatter: "{value}%",
        color: "#909399",
        fontSize: 11
      },
      nameTextStyle: { color: "#909399", fontSize: 12 },
      splitLine: { lineStyle: { color: "#ebeef5", type: "dashed" } },
      axisLine: { show: false },
      axisTick: { show: false }
    },
    dataZoom: [
      {
        type: "slider",
        show: true,
        xAxisIndex: [0],
        start: 100 - defaultEnd,
        end: 100,
        bottom: 30,
        height: 20,
        handleSize: "100%",
        showDetail: true,
        filterMode: "filter",
        backgroundColor: "rgba(255,255,255,0.9)",
        borderColor: "#e4e7ed",
        fillerColor: "rgba(64,158,255,0.1)",
        handleStyle: {
          color: "#409eff",
          borderColor: "#fff",
          borderWidth: 2
        },
        textStyle: { color: "#909399", fontSize: 11 },
        dataBackground: {
          lineStyle: { color: "#ddd" },
          areaStyle: { color: "rgba(220,220,220,0.2)" }
        }
      },
      {
        type: "inside",
        xAxisIndex: [0],
        start: 100 - defaultEnd,
        end: 100
      }
    ],
    series: allModels.map((model, index) => ({
      name: `使用率(%)`,
      type: "line",
      smooth: true,
      symbol: "circle",
      symbolSize: 6,
      data: totalUsage[index],
      itemStyle: {
        color: `hsl(${index * 40}, 70%, 55%)`,
        borderColor: "#fff",
        borderWidth: 1
      },
      lineStyle: { width: 2 },
      emphasis: { focus: "series" }
    }))
  });

  console.log("✅ 使用率图表渲染完成");

  // ====== 时长里程折线图 ======
  if (!carInfoDurationChartRef.value) return;
  if (!carInfoDurationChartInstance) {
    carInfoDurationChartInstance = echarts.init(carInfoDurationChartRef.value);
  }

  carInfoDurationChartInstance.setOption({
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "cross" },
      backgroundColor: "rgba(255,255,255,0.95)",
      borderColor: "#eee",
      borderWidth: 1,
      textStyle: { color: "#333", fontSize: 12 },
      formatter: (params: any) => {
        if (!params?.length) return "";
        let result = `<div style="font-weight:bold;margin-bottom:8px">${params[0].axisValue}</div>`;
        params.forEach((item: any) => {
          if (item && item.value !== undefined && item.value > 0) {
            const unit = item.seriesName.includes("时长") ? "h" : "km";
            result += `<div style="margin:4px 0">${item.marker} <b>${item.seriesName}</b>: <span style="font-weight:bold">${item.value}${unit}</span></div>`;
          }
        });
        return result;
      }
    },
    legend: {
      data: ["行驶里程(km)"],
      top: 5,
      right: 10,
      textStyle: { fontSize: 11 },
      icon: "roundRect",
      itemWidth: 16,
      itemHeight: 8
    },
    grid: { left: 70, right: 30, top: 35, bottom: 100 },
    xAxis: {
      type: "category",
      data: dates,
      axisLabel: {
        rotate: 30,
        fontSize: 11,
        interval: 0,
        color: "#909399",
        formatter: (value: string) => value.slice(5).replace("-", "/")
      },
      axisLine: { lineStyle: { color: "#ebeef5" } },
      axisTick: { alignWithLabel: true, length: 6 }
    },
    yAxis: {
      type: "value",
      name: "里程(km)",
      axisLabel: {
        color: "#909399",
        fontSize: 11
      },
      nameTextStyle: { color: "#909399", fontSize: 12 },
      splitLine: { lineStyle: { color: "#ebeef5", type: "dashed" } },
      axisLine: { show: false },
      axisTick: { show: false }
    },
    dataZoom: [
      {
        type: "slider",
        show: true,
        xAxisIndex: [0],
        start: 100 - defaultEnd,
        end: 100,
        bottom: 30,
        height: 20,
        handleSize: "100%",
        showDetail: true,
        filterMode: "filter",
        backgroundColor: "rgba(255,255,255,0.9)",
        borderColor: "#e4e7ed",
        fillerColor: "rgba(64,158,255,0.1)",
        handleStyle: {
          color: "#409eff",
          borderColor: "#fff",
          borderWidth: 2
        },
        textStyle: { color: "#909399", fontSize: 11 },
        dataBackground: {
          lineStyle: { color: "#ddd" },
          areaStyle: { color: "rgba(220,220,220,0.2)" }
        }
      },
      {
        type: "inside",
        xAxisIndex: [0],
        start: 100 - defaultEnd,
        end: 100
      }
    ],
    series: [
      {
        name: "行驶里程(km)",
        type: "line",
        smooth: true,
        symbol: "circle",
        symbolSize: 6,
        data: totalDistance[0] || [],
        itemStyle: {
          color: "#50b5ff",
          borderColor: "#fff",
          borderWidth: 1
        },
        lineStyle: { width: 2 },
        emphasis: { focus: "series" }
      }
    ]
  });

  console.log("✅ 时长里程图表渲染完成");
};

const renderGroupsChart = (data: any[]) => {
  if (!groupsChartRef.value) return;

  if (!groupsChartInstance) {
    groupsChartInstance = echarts.init(groupsChartRef.value);
  }

  console.log("📊 组别图表原始数据:", data.length, "条");

  const dates = [...new Set(data.map(item => item.monitor_date))].sort();
  console.log("📅 日期列表:", dates);

  const allGroups = [...new Set(data.map(item => item.group))].sort();
  console.log("👥 所有组别:", allGroups);

  const groupDateMap: Record<
    string,
    Record<string, { avg_usage: number; count: number }>
  > = {};

  data.forEach(item => {
    if (!groupDateMap[item.group]) {
      groupDateMap[item.group] = {};
    }
    if (!groupDateMap[item.group][item.monitor_date]) {
      groupDateMap[item.group][item.monitor_date] = {
        avg_usage: 0,
        count: 0
      };
    }

    const usage =
      item.avg_usage !== undefined && item.avg_usage !== null
        ? Number(item.avg_usage)
        : 0;
    const cnt =
      item.count !== undefined && item.count !== null ? Number(item.count) : 0;

    groupDateMap[item.group][item.monitor_date].avg_usage += usage;
    groupDateMap[item.group][item.monitor_date].count += cnt;
  });

  const usageData = allGroups.map(g =>
    dates.map(d => {
      const info = groupDateMap[g]?.[d];
      return info ? Number(info.avg_usage.toFixed(2)) : 0;
    })
  );

  console.log(`📈 数据处理完成:`, {
    组别数: allGroups.length,
    日期数: dates.length,
    使用率矩阵: usageData
  });

  const groupColors: Record<string, string> = {
    行车组: "#5470c6",
    泊车组: "#91cc75",
    预警组: "#fac858"
  };

  const defaultEnd =
    dates.length > 7 ? Math.round((7 / dates.length) * 100) : 100;

  groupsChartInstance.setOption({
    title: {
      text: "组别使用率统计（可拖动底部滑块查看不同日期）",
      left: "center",
      top: 5,
      textStyle: { fontSize: 14, fontWeight: "normal", color: "#666" }
    },
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
      backgroundColor: "rgba(255,255,255,0.95)",
      borderColor: "#eee",
      borderWidth: 1,
      textStyle: { color: "#333", fontSize: 12 },
      formatter: (params: any) => {
        if (!params?.length) return "";
        let result = `<div style="font-weight:bold;margin-bottom:10px">${params[0].axisValue}</div>`;
        let totalUsage = 0;

        params.forEach((item: any) => {
          if (item && item.value > 0) {
            const color =
              groupColors[item.seriesName.replace(/\(.*\)$/, "")] || "#999";

            result += `<div style="margin:6px 0;padding:8px;background:${color}15;border-radius:4px;border-left:3px solid ${color}">`;
            result += `<span style="color:${color};font-weight:bold">${item.marker} ${item.seriesName}</span><br/>`;
            result += `<span style="margin-left:16px">使用率: <b style="color:#e74c3c;font-size:13px">${item.value}%</b></span>`;
            result += `</div>`;

            totalUsage += item.value;
          }
        });

        result += `<div style="margin-top:10px;padding-top:10px;border-top:1px solid #eee">`;
        result += `</div>`;

        return result;
      }
    },
    legend: {
      data: allGroups.map(g => `${g}(使用率%)`),
      bottom: 50,
      textStyle: { fontSize: 11 },
      icon: "roundRect",
      itemWidth: 20,
      itemHeight: 8
    },
    grid: { left: 70, right: 90, top: 45, bottom: 100 },
    xAxis: {
      type: "category",
      data: dates,
      barCategoryGap: "40%",
      axisLabel: {
        rotate: 30,
        fontSize: 11,
        interval: 0,
        color: "#909399",
        formatter: (value: string) => value.slice(5).replace("-", "/")
      },
      axisLine: { lineStyle: { color: "#ebeef5" } },
      axisTick: { alignWithLabel: true, length: 6 }
    },
    yAxis: [
      {
        type: "value",
        name: "平均使用率 (%)",
        position: "left",
        min: 0,
        max: 100,
        axisLabel: {
          formatter: "{value}%",
          color: "#909399",
          fontSize: 11
        },
        nameTextStyle: { color: "#909399", fontSize: 12 },
        splitLine: { lineStyle: { color: "#ebeef5", type: "dashed" } },
        axisLine: { show: false },
        axisTick: { show: false }
      }
    ],
    dataZoom: [
      {
        type: "slider",
        show: true,
        xAxisIndex: [0],
        start: 100 - defaultEnd,
        end: 100,
        bottom: 10,
        height: 20,
        handleSize: "80%",
        showDetail: true,
        filterMode: "filter",
        backgroundColor: "rgba(255,255,255,0.9)",
        borderColor: "#e4e7ed",
        fillerColor: "rgba(84,112,198,0.15)",
        handleIcon:
          "M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z",
        handleStyle: {
          color: "#5470c6",
          borderColor: "#fff",
          borderWidth: 2,
          shadowBlur: 5,
          shadowColor: "rgba(84,112,198,0.3)"
        },
        textStyle: { color: "#333", fontSize: 11 },
        dataBackground: {
          lineStyle: { color: "#ddd" },
          areaStyle: { color: "rgba(220,220,220,0.2)" }
        }
      },
      {
        type: "inside",
        xAxisIndex: [0],
        start: 100 - defaultEnd,
        end: 100
      }
    ],
    series: [
      ...allGroups.map((group, index) => ({
        name: `${group}(使用率%)`,
        type: "bar",
        yAxisIndex: 0,
        barMaxWidth: 28,
        barGap: "20%",
        data: usageData[index],
        itemStyle: {
          color: groupColors[group] || `hsl(${index * 120}, 70%, 55%)`,
          borderRadius: [4, 4, 0, 0],
          borderColor: "#fff",
          borderWidth: 1
        },
        label: {
          show: allGroups.length <= 3,
          position: "top",
          formatter: "{c}%",
          fontSize: 10,
          fontWeight: "bold",
          color: "#333"
        },
        emphasis: {
          focus: "series",
          itemStyle: {
            shadowBlur: 15,
            shadowColor: "rgba(0,0,0,0.3)"
          }
        }
      }))
    ]
  });

  console.log("✅ 组别图表渲染完成，使用 DataZoom 时间轴");
};

const fetchLadderData = async () => {
  ladderChartLoading.value = true;
  try {
    const model = ladderModel.value.join(",") || "";
    const params: any = { models: model };
    console.log("ladderDate:", ladderDate.value);
    if (ladderDate.value && ladderDate.value.length === 2) {
      params.start_date = ladderDate.value[0];
      params.end_date = ladderDate.value[1];
    }
    const res: any = await getUsagesByDate(params);
    await nextTick();
    renderLadderChart(res?.data || []);
  } catch (error) {
    console.error("获取天梯图数据失败:", error);
  } finally {
    ladderChartLoading.value = false;
  }
};

const fetchDistanceLadderData = async () => {
  distanceLadderChartLoading.value = true;
  try {
    const model = distanceLadderModel.value.join(",") || "";
    const params: any = { models: model };
    if (distanceLadderDate.value && distanceLadderDate.value.length === 2) {
      params.start_date = distanceLadderDate.value[0];
      params.end_date = distanceLadderDate.value[1];
    }
    const res: any = await getDistancesByDate(params);
    await nextTick();
    renderDistanceLadderChart(res?.data || []);
  } catch (error) {
    console.error("获取里程天梯图数据失败:", error);
  } finally {
    distanceLadderChartLoading.value = false;
  }
};

const getDefaultMonitorDate = () => {
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  return yesterday.toISOString().split("T")[0];
};

const renderLadderChart = (data: any[]) => {
  if (!ladderChartRef.value) return;

  if (!ladderChartInstance) {
    ladderChartInstance = echarts.init(ladderChartRef.value);
  }

  const sortedData = [...data].sort(
    (a, b) => (b.avg_usage || 0) - (a.avg_usage || 0)
  );

  const vinCodes = sortedData.map(item => item.vin_code || "");
  const usages = sortedData.map(item => Number(item.avg_usage || 0));

  const maxUsage = Math.max(...usages, 100);
  const xAxisMax = Math.ceil(maxUsage / 20) * 20;

  const totalItems = vinCodes.length;
  const showCount = Math.min(10, totalItems);
  const defaultEnd =
    totalItems > 10 ? Math.round((showCount / totalItems) * 100) : 100;

  ladderChartInstance.setOption({
    title: {
      text: `车辆使用率排行（${ladderModel.value || "全部"} ${ladderDate.value && ladderDate.value.length === 2 ? `${ladderDate.value[0]} ~ ${ladderDate.value[1]}` : ""}）`,
      left: "center",
      top: 5,
      textStyle: { fontSize: 14, fontWeight: "normal", color: "#666" }
    },
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
      backgroundColor: "rgba(255,255,255,0.95)",
      borderColor: "#eee",
      borderWidth: 1,
      textStyle: { color: "#333", fontSize: 12 },
      formatter: (params: any) => {
        if (!params?.length) return "";
        const item = params[0];
        const idx = item.dataIndex;
        return `<div style="font-weight:bold;margin-bottom:8px">${item.name}</div>
                <div style="margin:4px 0">使用率: <b style="color:#409eff">${usages[idx]}%</b></div>`;
      }
    },
    grid: { left: 150, right: 50, top: 40, bottom: 30 },
    xAxis: {
      type: "value",
      name: "使用率 (%)",
      min: 0,
      max: xAxisMax,
      axisLabel: {
        formatter: "{value}%",
        color: "#909399",
        fontSize: 11
      },
      nameTextStyle: { color: "#909399", fontSize: 12 },
      splitLine: { lineStyle: { color: "#ebeef5", type: "dashed" } },
      axisLine: { show: false },
      axisTick: { show: false }
    },
    yAxis: {
      type: "category",
      data: vinCodes,
      inverse: true,
      axisLabel: {
        color: "#606266",
        fontSize: 10,
        width: 140,
        overflow: "truncate",
        ellipsis: "..."
      },
      axisLine: { lineStyle: { color: "#ebeef5" } },
      axisTick: { show: false }
    },
    dataZoom: [
      {
        type: "slider",
        show: true,
        yAxisIndex: [0],
        start: 0,
        end: defaultEnd,
        left: 5,
        width: 16,
        height: "80%",
        top: "10%",
        handleSize: "100%",
        showDetail: false,
        filterMode: "filter",
        backgroundColor: "rgba(255,255,255,0.9)",
        borderColor: "#e4e7ed",
        fillerColor: "rgba(64,158,255,0.1)",
        handleStyle: {
          color: "#409eff",
          borderColor: "#fff",
          borderWidth: 2
        },
        textStyle: { color: "#909399", fontSize: 11 },
        dataBackground: {
          lineStyle: { color: "#ddd" },
          areaStyle: { color: "rgba(220,220,220,0.2)" }
        }
      },
      {
        type: "inside",
        yAxisIndex: [0],
        start: 0,
        end: defaultEnd
      }
    ],
    series: [
      {
        name: "使用率",
        type: "bar",
        data: usages.map((usage, idx) => ({
          value: usage,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              {
                offset: 0,
                color:
                  usage > 80 ? "#67c23a" : usage >= 60 ? "#e6a23c" : "#f56c6c"
              },
              {
                offset: 1,
                color:
                  usage > 80 ? "#95d475" : usage >= 60 ? "#f0c78a" : "#f8989c"
              }
            ])
          }
        })),
        barWidth: 16,
        label: {
          show: true,
          position: "right",
          formatter: "{c}%",
          fontSize: 10,
          fontWeight: "bold",
          color: "#333"
        }
      }
    ]
  });

  console.log("✅ 天梯图渲染完成");
};

const renderDistanceLadderChart = (data: any[]) => {
  if (!distanceLadderChartRef.value) return;

  if (!distanceLadderChartInstance) {
    distanceLadderChartInstance = echarts.init(distanceLadderChartRef.value);
  }

  const sortedData = [...data].sort(
    (a, b) => (b.avg_distance || 0) - (a.avg_distance || 0)
  );

  const vinCodes = sortedData.map(item => item.vin_code || "");
  const distances = sortedData.map(item => Number(item.avg_distance || 0));

  const totalItems = vinCodes.length;
  const defaultEnd =
    totalItems > 20 ? Math.round((20 / totalItems) * 100) : 100;

  distanceLadderChartInstance.setOption({
    title: {
      text: `行驶里程排行（${distanceLadderModel.value || "全部"} ${distanceLadderDate.value && distanceLadderDate.value.length === 2 ? `${distanceLadderDate.value[0]} ~ ${distanceLadderDate.value[1]}` : ""}）`,
      left: "center",
      top: 5,
      textStyle: { fontSize: 14, fontWeight: "normal", color: "#666" }
    },
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
      backgroundColor: "rgba(255,255,255,0.95)",
      borderColor: "#eee",
      borderWidth: 1,
      textStyle: { color: "#333", fontSize: 12 },
      formatter: (params: any) => {
        if (!params?.length) return "";
        const item = params[0];
        const idx = item.dataIndex;
        return `<div style="font-weight:bold;margin-bottom:8px">${item.name}</div>
                <div style="margin:4px 0">行驶里程: <b style="color:#409eff">${distances[idx]}km</b></div>`;
      }
    },
    grid: { left: 150, right: 50, top: 40, bottom: 30 },
    xAxis: {
      type: "value",
      name: "行驶里程 (km)",
      min: 0,
      axisLabel: {
        formatter: "{value}km",
        color: "#909399",
        fontSize: 11
      },
      nameTextStyle: { color: "#909399", fontSize: 12 },
      splitLine: { lineStyle: { color: "#ebeef5", type: "dashed" } },
      axisLine: { show: false },
      axisTick: { show: false }
    },
    yAxis: {
      type: "category",
      data: vinCodes,
      inverse: true,
      axisLabel: {
        color: "#606266",
        fontSize: 10,
        width: 140,
        overflow: "truncate",
        ellipsis: "..."
      },
      axisLine: { lineStyle: { color: "#ebeef5" } },
      axisTick: { show: false }
    },
    dataZoom: [
      {
        type: "slider",
        show: true,
        yAxisIndex: [0],
        start: 0,
        end: defaultEnd,
        left: 5,
        width: 16,
        height: "80%",
        top: "10%",
        handleSize: "100%",
        showDetail: false,
        filterMode: "filter",
        backgroundColor: "rgba(255,255,255,0.9)",
        borderColor: "#e4e7ed",
        fillerColor: "rgba(64,158,255,0.1)",
        handleStyle: {
          color: "#409eff",
          borderColor: "#fff",
          borderWidth: 2
        },
        textStyle: { color: "#909399", fontSize: 11 },
        dataBackground: {
          lineStyle: { color: "#ddd" },
          areaStyle: { color: "rgba(220,220,220,0.2)" }
        }
      },
      {
        type: "inside",
        yAxisIndex: [0],
        start: 0,
        end: defaultEnd
      }
    ],
    series: [
      {
        name: "行驶里程",
        type: "bar",
        data: distances.map((distance, idx) => ({
          value: distance,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              {
                offset: 0,
                color:
                  distance > 200
                    ? "#67c23a"
                    : distance >= 100
                      ? "#e6a23c"
                      : "#f56c6c"
              },
              {
                offset: 1,
                color:
                  distance > 200
                    ? "#95d475"
                    : distance >= 100
                      ? "#f0c78a"
                      : "#f8989c"
              }
            ])
          }
        })),
        barWidth: 16,
        label: {
          show: true,
          position: "right",
          formatter: "{c}km",
          fontSize: 10,
          fontWeight: "bold",
          color: "#333"
        }
      }
    ]
  });

  console.log("✅ 里程天梯图渲染完成");
};

const handleResize = () => {
  carInfoChartInstance?.resize();
  carInfoDurationChartInstance?.resize();
  groupsChartInstance?.resize();
  ladderChartInstance?.resize();
  distanceLadderChartInstance?.resize();
};

watch(
  () => [chartVin.value, chartModel.value],
  () => {
    fetchChartData();
  }
);

onUnmounted(() => {
  carInfoChartInstance?.dispose();
  carInfoDurationChartInstance?.dispose();
  groupsChartInstance?.dispose();
  ladderChartInstance?.dispose();
  distanceLadderChartInstance?.dispose();
  carInfoChartInstance = null;
  carInfoDurationChartInstance = null;
  groupsChartInstance = null;
  ladderChartInstance = null;
  distanceLadderChartInstance = null;
  window.removeEventListener("resize", handleResize);
});
</script>

<template>
  <div class="main">
    <el-form
      ref="formRef"
      :inline="true"
      :model="form"
      class="search-form bg-bg_color w-full pl-8 pt-3"
    >
      <el-form-item label="车型" prop="model">
        <el-select
          v-model="form.model"
          multiple
          placeholder="请选择/搜索车型"
          filterable
          clearable
          class="w-42.5!"
          collapse-tags
          collapse-tags-tooltip
          :max-collapse-tags="1"
        >
          <el-option v-for="m in modelOptions" :key="m" :label="m" :value="m" />
        </el-select>
      </el-form-item>
      <el-form-item label="车辆VIN号" prop="vin_code">
        <el-select
          v-model="form.vin_code"
          placeholder="请选择VIN号"
          filterable
          :filter-method="handleVinFilter"
          clearable
          class="w-42.5!"
          @visible-change="handleVinVisibleChange"
        >
          <el-option
            v-for="vin in vinOptions"
            :key="vin"
            :label="vin"
            :value="vin"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="组别" prop="group">
        <el-select
          v-model="form.group"
          placeholder="请选择组别"
          clearable
          class="w-37.5!"
        >
          <el-option label="行车组" value="行车组" />
          <el-option label="泊车组" value="泊车组" />
          <el-option label="预警组" value="预警组" />
        </el-select>
      </el-form-item>
      <el-form-item label="监控日期" prop="dateRange">
        <el-date-picker
          v-model="form.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          clearable
          class="w-80!"
        />
      </el-form-item>

      <el-form-item>
        <div class="flex items-center gap-4">
          <ReAdvancedSearch
            ref="advancedSearchRef"
            v-model="advancedFilters"
            :field-options="filterFieldOptions"
            @search="onSearch"
          />
          <el-button
            type="primary"
            :icon="useRenderIcon('ri/search-line')"
            :loading="loading"
            @click="onSearch"
          >
            搜索
          </el-button>
          <el-button :icon="useRenderIcon(Refresh)" @click="handleReset">
            重置
          </el-button>
        </div>
      </el-form-item>
    </el-form>

    <PureTableBar
      title="车辆监控管理"
      :columns="columns"
      tableKey="monitor-record"
      @refresh="onSearch"
    >
      <template #buttons>
        <div
          class="flex items-center gap-2 text-sm text-[var(--el-text-color-secondary)] justify-end"
        >
          <span>使用率说明：</span>
          <span class="flex items-center gap-1">
            <span class="inline-block w-2 h-2 rounded-full bg-[#67C23A]" />
            &gt; 80%
          </span>
          <span class="flex items-center gap-1">
            <span class="inline-block w-2 h-2 rounded-full bg-[#0a0a0a]" />
            60% ~ 80%
          </span>
          <span class="flex items-center gap-1">
            <span class="inline-block w-2 h-2 rounded-full bg-[#F56C6C]" />
            &lt; 60%
          </span>
        </div>
        <div class="flex justify-end flex-1 gap-2" v-if="false">
          <el-button
            type="info"
            :icon="useRenderIcon(MapLocation)"
            @click="mapVisible = true"
          >
            地图查看
          </el-button>
          <el-button
            type="primary"
            :icon="useRenderIcon(Plus)"
            @click="onAdd()"
          >
            新增
          </el-button>
        </div>
      </template>
      <template v-slot="{ size, dynamicColumns }">
        <div
          v-if="selectedNum > 0"
          v-motion-fade
          class="bg-(--el-fill-color-light) w-full h-11.5 mb-2 pl-4 flex items-center"
        >
          <div class="flex-auto">
            <span
              style="font-size: var(--el-font-size-base)"
              class="text-[rgba(42,46,54,0.5)] dark:text-[rgba(220,220,242,0.5)]"
            >
              已选 {{ selectedNum }} 项
            </span>
            <el-button type="primary" text @click="onSelectionCancel">
              取消选择
            </el-button>
          </div>
          <el-popconfirm title="是否确认删除?" @confirm="onbatchDel">
            <template #reference>
              <el-button type="danger" text class="mr-1!"> 批量删除 </el-button>
            </template>
          </el-popconfirm>
        </div>

        <pure-table
          ref="tableRef"
          row-key="id"
          align-whole="center"
          table-layout="auto"
          :loading="loading"
          :size="size"
          :data="dataList"
          :columns="dynamicColumns"
          :pagination="{ ...pagination, size }"
          :header-cell-style="{
            background: 'var(--el-fill-color-light)',
            color: 'var(--el-text-color-primary)',
            whiteSpace: 'nowrap'
          }"
          @selection-change="handleSelectionChange"
          @page-size-change="handleSizeChange"
          @page-current-change="handleCurrentChange"
          @sort-change="handleSortChange"
          tableKey="monitor-record"
          border
        >
          <template #operation="{ row }">
            <div class="flex items-center justify-center gap-2">
              <el-button
                class="reset-margin outline-hidden! ml-0!"
                link
                type="primary"
                :size="size"
                :icon="useRenderIcon(Edit)"
                @click="onEdit(row)"
              >
                编辑
              </el-button>
              <el-dropdown
                trigger="hover"
                @command="(cmd: string) => handleCommand(cmd, row)"
              >
                <el-button
                  class="reset-margin outline-hidden!"
                  link
                  type="primary"
                  :size="size"
                >
                  更多操作
                  <el-icon class="ml-1"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="detail">
                      <el-icon class="mr-1"
                        ><component :is="useRenderIcon(View)"
                      /></el-icon>
                      详情
                    </el-dropdown-item>
                    <el-dropdown-item command="delete" divided>
                      <el-icon
                        class="mr-1"
                        style="color: var(--el-color-danger)"
                        ><component :is="useRenderIcon(Delete)"
                      /></el-icon>
                      <span style="color: var(--el-color-danger)">删除</span>
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
          <template #usage="{ row }">
            <span
              :style="{
                color:
                  Number(row.usage) > 80
                    ? '#67C23A'
                    : Number(row.usage) >= 60
                      ? '#0a0a0a'
                      : '#F56C6C',
                fontWeight: Number(row.usage) > 80 ? '600' : 'normal'
              }"
            >
              {{ row.usage || 0 }}%
            </span>
          </template>
        </pure-table>
      </template>
    </PureTableBar>

    <!-- 图表区域 -->
    <div class="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 车辆使用率天梯图 -->
      <el-card shadow="never" class="lg:col-span-2">
        <div class="flex items-center justify-between mb-4">
          <div class="text-base font-medium flex items-center gap-2">
            <el-icon class="text-purple-500" size="18"
              ><component :is="useRenderIcon('ep/rank')"
            /></el-icon>
            车辆使用率排行
          </div>
          <div class="flex items-center gap-2">
            <el-select
              v-model="ladderModel"
              placeholder="选择车型"
              multiple
              filterable
              clearable
              style="width: 200px"
              collapse-tags
              collapse-tags-tooltip
              :max-collapse-tags="1"
              @change="fetchLadderData"
            >
              <el-option
                v-for="m in modelOptions"
                :key="m"
                :label="m"
                :value="m"
              />
            </el-select>
            <el-date-picker
              v-model="ladderDate"
              type="daterange"
              range-separator="~"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 260px"
              @change="fetchLadderData"
            />
          </div>
        </div>
        <div
          ref="ladderChartRef"
          v-loading="ladderChartLoading"
          style="height: 500px; width: 100%"
        ></div>
      </el-card>

      <!-- 单车使用率折线图 -->
      <el-card shadow="never">
        <div class="flex items-center justify-between mb-4">
          <div class="text-base font-medium flex items-center gap-2">
            <el-icon class="text-blue-500" size="18"
              ><component :is="useRenderIcon('ep/trend-charts')"
            /></el-icon>
            单车使用率统计
          </div>
          <el-select
            v-model="chartVin"
            placeholder="选择VIN号"
            filterable
            clearable
            virtual
            style="width: 200px"
          >
            <el-option
              v-for="vin in vinOptions"
              :key="vin"
              :label="vin"
              :value="vin"
            />
          </el-select>
        </div>
        <div
          ref="carInfoChartRef"
          v-loading="carInfoChartLoading"
          style="height: 380px; width: 100%"
        ></div>
      </el-card>

      <!-- 单车时长里程折线图 -->
      <el-card shadow="never">
        <div class="flex items-center justify-between mb-4">
          <div class="text-base font-medium flex items-center gap-2">
            <el-icon class="text-orange-500" size="18"
              ><component :is="useRenderIcon('ep/trend-charts')"
            /></el-icon>
            单车时长里程统计
          </div>
          <el-select
            v-model="chartVin"
            placeholder="选择VIN号"
            filterable
            clearable
            virtual
            style="width: 200px"
          >
            <el-option
              v-for="vin in vinOptions"
              :key="vin"
              :label="vin"
              :value="vin"
            />
          </el-select>
        </div>
        <div
          ref="carInfoDurationChartRef"
          v-loading="carInfoDurationChartLoading"
          style="height: 380px; width: 100%"
        ></div>
      </el-card>

      <!-- 组别使用率柱状图 -->
      <el-card shadow="never" class="lg:col-span-2">
        <div class="flex items-center justify-between mb-4">
          <div class="text-base font-medium flex items-center gap-2">
            <el-icon class="text-green-500" size="18"
              ><component :is="useRenderIcon('ep/histogram')"
            /></el-icon>
            组别使用率统计
          </div>
          <el-select
            v-model="chartModel"
            placeholder="选择车型"
            filterable
            clearable
            style="width: 150px"
            @change="fetchChartData"
          >
            <el-option
              v-for="m in modelOptions"
              :key="m"
              :label="m"
              :value="m"
            />
          </el-select>
        </div>
        <div
          ref="groupsChartRef"
          v-loading="groupsChartLoading"
          style="height: 380px; width: 100%"
        ></div>
      </el-card>

      <!-- 行驶里程天梯图 -->
      <el-card shadow="never" class="lg:col-span-2">
        <div class="flex items-center justify-between mb-4">
          <div class="text-base font-medium flex items-center gap-2">
            <el-icon class="text-blue-500" size="18"
              ><component :is="useRenderIcon('ep/odometer')"
            /></el-icon>
            行驶里程排行
          </div>
          <div class="flex items-center gap-2">
            <el-select
              v-model="distanceLadderModel"
              placeholder="选择车型"
              multiple
              filterable
              clearable
              style="width: 200px"
              @change="fetchDistanceLadderData"
              collapse-tags
              collapse-tags-tooltip
              :max-collapse-tags="1"
            >
              <el-option
                v-for="m in modelOptions"
                :key="m"
                :label="m"
                :value="m"
              />
            </el-select>
            <el-date-picker
              v-model="distanceLadderDate"
              type="daterange"
              range-separator="~"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 260px"
              @change="fetchDistanceLadderData"
            />
          </div>
        </div>
        <div
          ref="distanceLadderChartRef"
          v-loading="distanceLadderChartLoading"
          style="height: 500px; width: 100%"
        ></div>
      </el-card>
    </div>

    <!-- 车辆监控弹窗 -->
    <MonitorDialog ref="monitorDialogRef" @save="onSave" />

    <!-- 地图弹窗 -->
    <el-dialog
      v-model="mapVisible"
      title="车辆位置地图"
      width="90%"
      top="5vh"
      :close-on-click-modal="false"
      destroy-on-close
      @opened="onMapDialogOpened"
    >
      <VehicleMap ref="vehicleMapRef" :vehicle-list="dataList" />
    </el-dialog>
  </div>
</template>

<style lang="scss" scoped>
.search-form {
  :deep(.el-form-item) {
    margin-bottom: 12px;
  }
}

:deep(.el-table__header th .cell) {
  white-space: nowrap !important;
}
</style>

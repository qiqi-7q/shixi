import { reactive, ref, onMounted, nextTick, watch, computed } from "vue";
import * as echarts from "echarts/core";
import {
  getVehicleOverview,
  getMileageStats,
  getUsagesByDate,
  getDistancesByDate,
  getGroups
} from "@/api/system";
import { useDashboardStoreHook } from "@/store/modules/dashboardList";
export function useDashboard() {
  const dashboardStore = useDashboardStoreHook();
  // ===== 统计数据 =====
  const statistics = reactive({
    vehicleTotal: 0,
    vehicleAvailable: 0,
    vehicleBorrowed: 0,
    vehicleMaintenance: 0,
    vehicleReserved: 0
  });

  const loading = ref(true);

  // ===== 项目筛选 =====
  const projectOptions = computed(() => dashboardStore.getProjectOptions);
  const selectedProject = ref<string>("");

  // ===== 车型列表 =====
  const modelOptions = computed(() => dashboardStore.getModelOptions);

  // ===== 图表 refs =====
  const versionChartRef = ref<HTMLElement>();
  const dailyMileageChartRef = ref<HTMLElement>();
  const ladderChartRef = ref<HTMLElement>();
  const distanceLadderChartRef = ref<HTMLElement>();
  const groupsChartRef = ref<HTMLElement>();
  const ladderDate = ref<string[]>([]);
  const distanceLadderDate = ref<string[]>([]);
  const ladderModel = ref<string[]>([]);
  const distanceLadderModel = ref<string[]>([]);
  const chartModel = ref("");

  // ===== 加载项目列表 =====
  async function loadProjectOptions() {
    await dashboardStore.SET_PROJECT_OPTIONS();
  }

  // ===== 加载车型列表 =====
  async function loadModelOptions() {
    await dashboardStore.SET_MODEL_OPTIONS();
  }

  // ===== 加载统计数据 =====
  async function loadStats() {
    try {
      const res: any = await getVehicleOverview();
      if (res.code === 200 && res.data) {
        statistics.vehicleTotal = res.data.total || 0;
        statistics.vehicleAvailable = res.data.available || 0;
        statistics.vehicleBorrowed = res.data.borrowed || 0;
        statistics.vehicleMaintenance = res.data.maintenance || 0;
        statistics.vehicleReserved = res.data.reserved || 0;
      }
    } catch (e) {
      console.error("加载统计数据失败", e);
    }
  }

  // ===== 加载版本里程和每日里程图表 =====
  async function loadMileageCharts() {
    await nextTick();

    // 版本里程柱状图
    if (versionChartRef.value) {
      try {
        const params: any = {};
        if (selectedProject.value) params.project = selectedProject.value;
        const res: any = await getMileageStats(params);
        if (res.code === 200 && res.data) {
          const versionMileage = res.data.version_mileage || [];
          if (versionMileage.length > 0) {
            const chart = echarts.init(versionChartRef.value);
            chart.setOption({
              tooltip: { trigger: "axis", formatter: "{b}: {c} km" },
              grid: { left: 80, right: 20, bottom: 30, top: 20 },
              xAxis: {
                type: "category",
                data: versionMileage.map((v: any) => v.version),
                axisLabel: { color: "#666" }
              },
              yAxis: {
                type: "value",
                name: "里程(km)",
                nameLocation: "middle",
                nameGap: 50,
                nameTextStyle: { color: "#666" },
                axisLabel: { color: "#666" }
              },
              series: [
                {
                  type: "bar",
                  data: versionMileage.map((v: any) => v.total_mileage),
                  itemStyle: { color: "#409EFF", borderRadius: [4, 4, 0, 0] },
                  barWidth: "40%"
                }
              ]
            });
          }
        }
      } catch (e) {
        console.error("加载版本里程统计失败", e);
      }
    }

    // 每日测试里程折线图
    if (dailyMileageChartRef.value) {
      try {
        const params: any = {};
        if (selectedProject.value) params.project = selectedProject.value;
        const res: any = await getMileageStats(params);
        if (res.code === 200 && res.data) {
          const dailyMileage = res.data.daily_mileage || [];
          if (dailyMileage.length > 0) {
            const chart = echarts.init(dailyMileageChartRef.value);
            chart.setOption({
              tooltip: {
                trigger: "axis",
                formatter: "{b}: {c} km"
              },
              grid: { left: 80, right: 20, bottom: 30, top: 20 },
              xAxis: {
                type: "category",
                data: dailyMileage.map((d: any) => d.date),
                axisLabel: { color: "#666" }
              },
              yAxis: {
                type: "value",
                name: "里程(km)",
                nameLocation: "middle",
                nameGap: 50,
                nameTextStyle: { color: "#666" },
                axisLabel: { color: "#666" }
              },
              series: [
                {
                  type: "line",
                  data: dailyMileage.map((d: any) => d.total_mileage),
                  smooth: true,
                  areaStyle: { opacity: 0.3 },
                  itemStyle: { color: "#67C23A" }
                }
              ]
            });
          }
        }
      } catch (e) {
        console.error("加载每日里程统计失败", e);
      }
    }
  }

  // ===== 监听项目筛选变化 =====
  watch(selectedProject, () => {
    loadMileageCharts();
  });

  // ===== 初始化加载 =====
  onMounted(async () => {
    await Promise.all([loadStats(), loadModelOptions(), loadProjectOptions()]);
    if (modelOptions.value.length > 0 && !chartModel.value) {
      chartModel.value = modelOptions.value[0];
    }
    // 默认日期为昨天
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const yesterdayStr = yesterday.toISOString().split("T")[0];
    if (!ladderDate.value || ladderDate.value.length === 0) {
      ladderDate.value = [yesterdayStr, yesterdayStr];
    }
    if (!distanceLadderDate.value || distanceLadderDate.value.length === 0) {
      distanceLadderDate.value = [yesterdayStr, yesterdayStr];
    }
    // 加载所有图表数据
    await Promise.all([
      loadLadderChart(),
      loadDistanceLadderChart(),
      loadGroupsChart(),
      loadMileageCharts()
    ]);
    // 所有数据加载完成后关闭 loading
    loading.value = false;
  });

  // 📊 车辆使用率天梯图
  async function loadLadderChart() {
    await nextTick();
    if (!ladderChartRef.value) return;

    try {
      const params: any = { models: ladderModel.value.join(",") || "" };
      if (ladderDate.value && ladderDate.value.length === 2) {
        params.start_date = ladderDate.value[0];
        params.end_date = ladderDate.value[1];
      }
      const res: any = await getUsagesByDate(params);
      if (res.code === 200 && res.data) {
        const data = res.data;
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

        const chart = echarts.init(ladderChartRef.value);
        chart.setOption({
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
              }
            },
            {
              type: "inside",
              yAxisIndex: [0],
              start: 0,
              end: defaultEnd,
              filterMode: "filter"
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
                        usage > 80
                          ? "#67c23a"
                          : usage >= 60
                            ? "#e6a23c"
                            : "#f56c6c"
                    },
                    {
                      offset: 1,
                      color:
                        usage > 80
                          ? "#95d475"
                          : usage >= 60
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
                formatter: "{c}%",
                fontSize: 10,
                fontWeight: "bold",
                color: "#333"
              }
            }
          ]
        });
      }
    } catch (e) {
      console.error("加载天梯图数据失败", e);
    }
  }

  // 🚗 行驶里程天梯图
  async function loadDistanceLadderChart() {
    await nextTick();
    if (!distanceLadderChartRef.value) return;

    try {
      const params: any = { models: distanceLadderModel.value || "" };
      if (distanceLadderDate.value && distanceLadderDate.value.length === 2) {
        params.start_date = distanceLadderDate.value[0];
        params.end_date = distanceLadderDate.value[1];
      }
      const res: any = await getDistancesByDate(params);
      if (res.code === 200 && res.data) {
        const data = res.data;
        const sortedData = [...data].sort(
          (a, b) => (b.avg_distance || 0) - (a.avg_distance || 0)
        );

        const vinCodes = sortedData.map(item => item.vin_code || "");
        const distances = sortedData.map(item =>
          Number(item.avg_distance || 0)
        );

        const totalItems = vinCodes.length;
        const defaultEnd =
          totalItems > 20 ? Math.round((20 / totalItems) * 100) : 100;

        const chart = echarts.init(distanceLadderChartRef.value);
        chart.setOption({
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
              }
            },
            {
              type: "inside",
              yAxisIndex: [0],
              start: 0,
              end: defaultEnd,
              filterMode: "filter"
            }
          ],
          series: [
            {
              type: "bar",
              data: distances,
              itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                  { offset: 0, color: "#67C23A" },
                  { offset: 0.5, color: "#5EBD3E" },
                  { offset: 1, color: "#5EBD3E" }
                ]),
                borderRadius: [0, 4, 4, 0]
              },
              barWidth: "60%"
            }
          ]
        });
      }
    } catch (e) {
      console.error("加载里程天梯图数据失败", e);
    }
  }

  // 📊 组别使用率柱状图
  async function loadGroupsChart() {
    await nextTick();
    if (!groupsChartRef.value) return;

    try {
      const params: any = {};
      if (chartModel.value) {
        params.model = chartModel.value;
      }
      const res: any = await getGroups(params);
      if (res.code === 200 && res.data) {
        const data = res.data;

        const dates = [
          ...new Set(data.map((item: any) => item.monitor_date))
        ].sort();
        const allGroups = [
          ...new Set(data.map((item: any) => item.group))
        ].sort();

        const groupDateMap: Record<
          any,
          Record<any, { avg_usage: number; count: number }>
        > = {};

        data.forEach((item: any) => {
          const group = String(item.group);
          const date = String(item.monitor_date);
          if (!groupDateMap[group]) {
            groupDateMap[group] = {};
          }
          if (!groupDateMap[group][date]) {
            groupDateMap[group][date] = {
              avg_usage: 0,
              count: 0
            };
          }

          const usage =
            item.avg_usage !== undefined && item.avg_usage !== null
              ? Number(item.avg_usage)
              : 0;
          const cnt =
            item.count !== undefined && item.count !== null
              ? Number(item.count)
              : 0;

          groupDateMap[group][date].avg_usage += usage;
          groupDateMap[group][date].count += cnt;
        });

        const usageData = allGroups.map((g: any) =>
          dates.map((d: any) => {
            const info = groupDateMap[g]?.[d];
            return info ? Number(info.avg_usage.toFixed(2)) : 0;
          })
        );

        const groupColors: Record<string, string> = {
          行车组: "#5470c6",
          泊车组: "#91cc75",
          预警组: "#fac858"
        };

        const defaultEnd =
          dates.length > 7 ? Math.round((7 / dates.length) * 100) : 100;

        const chart = echarts.init(groupsChartRef.value);
        chart.setOption({
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
                    groupColors[item.seriesName.replace(/\(.*\)$/, "")] ||
                    "#999";

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
          series: allGroups.map((group: string, index: number) => ({
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
        });
      }
    } catch (e) {
      console.error("加载组别图表数据失败", e);
    }
  }

  return {
    statistics,
    loading,
    projectOptions,
    selectedProject,
    modelOptions,
    versionChartRef,
    dailyMileageChartRef,
    ladderChartRef,
    distanceLadderChartRef,
    groupsChartRef,
    ladderDate,
    distanceLadderDate,
    ladderModel,
    distanceLadderModel,
    chartModel,
    loadLadderChart,
    loadDistanceLadderChart,
    loadGroupsChart,
    loadMileageCharts
  };
}

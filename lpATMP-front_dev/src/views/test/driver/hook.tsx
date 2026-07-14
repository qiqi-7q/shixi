import type { PaginationProps } from "@pureadmin/table";
import { type Ref, reactive, ref, onMounted, nextTick } from "vue";
import * as echarts from "echarts/core";
import { ElMessageBox } from "element-plus";
import { message } from "@/utils/message";
import {
  getDriverMonitorList,
  deleteDriverMonitor,
  getDriverMonitorOverview,
  getDriverMonitorDailyFatigue,
  getDriverMonitorDailyDms,
  getDriverMonitorDriverFatigue
} from "@/api/system";
import dayjs from "dayjs";

export function useRole(
  tableRef: Ref,
  advancedFilters?: Ref<
    Array<{ field: string; operator: string; value: string }>
  >
) {
  const form = reactive({
    driverName: "",
    dateRange: [] as string[],
    driverStatus: ""
  });

  const dataList = ref([]);
  const loading = ref(true);
  const selectedNum = ref(0);

  const pagination = reactive<PaginationProps>({
    total: 0,
    pageSize: 10,
    currentPage: 1,
    background: true
  });

  const statistics = reactive({
    total: 0,
    normal: 0,
    slightFatigue: 0,
    severeFatigue: 0,
    fatigue: 0
  });

  const dailyFatigueChartRef = ref<HTMLElement>();
  const dmsTriggerChartRef = ref<HTMLElement>();
  const driverFatigueChartRef = ref<HTMLElement>();

  const columns: TableColumnList = [
    {
      label: "勾选列",
      type: "selection",
      fixed: "left",
      reserveSelection: true
    },
    {
      label: "序号",
      minWidth: 70,
      type: "index"
    },
    
    {
      label: "日期",
      prop: "testDate",
      minWidth: 120,
      formatter: ({ test_date }) => test_date || "-"
    },
    {
      label: "测试时间段",
      prop: "testPeriod",
      minWidth: 180,
      formatter: ({ test_start_time, test_end_time }) => {
        if (!test_start_time || !test_end_time) return "-";
        const start = dayjs(test_start_time).format("HH:mm");
        const end = dayjs(test_end_time).format("HH:mm");
        return `${start}-${end}`;
      }
    },
    {
      label: "测试车辆VIN",
      prop: "vinCode",
      minWidth: 180,
      formatter: ({ vin_code }) => vin_code || "-"
    },
    {
      label: "司机姓名",
      prop: "driverName",
      minWidth: 100,
      formatter: ({ driver_name }) => driver_name || "-"
    },
    {
      label: "驾驶员状态",
      prop: "driverStatus",
      minWidth: 120,
      formatter: ({ driver_status }) => driver_status || "-"
    },
    {
      label: "DMS触发次数",
      prop: "dmsTriggerCount",
      minWidth: 120,
      formatter: ({ dms_trigger_count }) => dms_trigger_count ?? "-"
    },
    {
      label: "行驶里程(km)",
      prop: "distance",
      minWidth: 120,
      formatter: ({ distance }) => (distance != null ? `${distance}km` : "-")
    },
    {
      label: "车辆上电时长",
      prop: "powerOnTime",
      minWidth: 160,
      formatter: ({ power_start_duration, power_end_duration }) => {
        if (!power_start_duration || !power_end_duration) return "-";
        const start = dayjs(power_start_duration);
        const end = dayjs(power_end_duration);
        const diffMinutes = end.diff(start, "minute");
        const hours = Math.floor(diffMinutes / 60);
        const minutes = diffMinutes % 60;
        return hours > 0 ? `${hours}h${minutes}m` : `${minutes}m`;
      }
    },
    {
      label: "备注",
      prop: "remark",
      minWidth: 140,
      formatter: ({ remark }) => remark || "-",
      width: 140,
      slot: "remark"
    },
    {
      label: "操作",
      fixed: "right",
      minWidth: 200,
      slot: "operation"
    }
  ];

  function handleSizeChange(val: number) {
    pagination.pageSize = val;
    pagination.currentPage = 1;
    onSearch();
  }

  function handleCurrentChange(val: number) {
    pagination.currentPage = val;
    onSearch();
  }

  function handleSelectionChange(val) {
    selectedNum.value = val.length;
    tableRef.value.setAdaptive();
  }

  function onSelectionCancel() {
    selectedNum.value = 0;
    tableRef.value.getTableRef().clearSelection();
  }

  async function onbatchDel() {
    const curSelected = tableRef.value.getTableRef().getSelectionRows();
    if (curSelected.length === 0) {
      message("请选择要删除的数据", { type: "warning" });
      return;
    }
    try {
      await ElMessageBox.confirm(
        `确认要删除选中的 ${curSelected.length} 条记录吗？`,
        "系统提示",
        {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          type: "warning",
          draggable: true
        }
      );
      for (const item of curSelected) {
        await deleteDriverMonitor(item.id);
      }
      message("批量删除成功", { type: "success" });
      tableRef.value.getTableRef().clearSelection();
      onSearch();
    } catch (e) {
      if (e !== "cancel") {
        message("批量删除失败", { type: "error" });
      }
    }
  }

  function onAdd() {
    return { mode: "add" as const, row: {} };
  }

  function onDetail(row) {
    return { mode: "detail" as const, row };
  }

  function onEdit(row) {
    return { mode: "edit" as const, row };
  }

  async function onDelete(row) {
    try {
      await ElMessageBox.confirm(`确认要删除该记录吗？`, "系统提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
        draggable: true
      });
      const res = (await deleteDriverMonitor(row.id)) as any;
      if (res.code === 200) {
        message("删除成功", { type: "success" });
        onSearch();
      } else {
        message(res.message || "删除失败", { type: "error" });
      }
    } catch (e) {
      if (e !== "cancel") {
        message("删除失败", { type: "error" });
      }
    }
  }

  async function onSearch() {
    loading.value = true;
    try {
      const params: any = {
        skip: (pagination.currentPage - 1) * pagination.pageSize,
        limit: pagination.pageSize
      };

      if (form.driverName) {
        params.driver_name = form.driverName;
      }

      if (form.driverStatus) {
        const statusMap: Record<string, string> = {
          normal: "正常",
          slightFatigue: "轻微疲劳",
          fatigue: "疲劳",
          severeFatigue: "严重疲劳"
        };
        params.driver_status =
          statusMap[form.driverStatus] || form.driverStatus;
      }

      if (form.dateRange && form.dateRange.length === 2) {
        params.test_start_date = form.dateRange[0];
        params.test_end_date = form.dateRange[1];
      }

      const res = (await getDriverMonitorList(params)) as any;

      if (res.code === 200) {
        dataList.value = res.data?.items || [];
        pagination.total = res.data?.total || 0;
        updateStatistics();
        nextTick(() => updateCharts());
      } else {
        message(res.message || "获取数据失败", { type: "error" });
      }
    } catch (error) {
      message("获取数据失败", { type: "error" });
    } finally {
      loading.value = false;
    }
  }

  async function updateStatistics() {
    try {
      const params: any = {};
      if (form.driverName) {
        params.driver_name = form.driverName;
      }
      if (form.driverStatus) {
        const statusMap: Record<string, string> = {
          normal: "正常",
          slightFatigue: "轻微疲劳",
          fatigue: "疲劳",
          severeFatigue: "严重疲劳"
        };
        params.driver_status =
          statusMap[form.driverStatus] || form.driverStatus;
      }
      if (form.dateRange && form.dateRange.length === 2) {
        params.start_date = form.dateRange[0];
        params.end_date = form.dateRange[1];
      }

      const res = (await getDriverMonitorOverview(params)) as any;
      if (res.code === 200 && res.data) {
        statistics.total = res.data.total || 0;
        const statusCounts = res.data.status_counts || [];
        statistics.normal =
          statusCounts.find(s => s.status === "正常")?.count || 0;
        statistics.slightFatigue =
          statusCounts.find(s => s.status === "轻微疲劳")?.count || 0;
        statistics.fatigue =
          statusCounts.find(s => s.status === "疲劳")?.count || 0;
        statistics.severeFatigue =
          statusCounts.find(s => s.status === "严重疲劳")?.count || 0;
      }
    } catch (error) {
      console.error("获取统计数据失败", error);
    }
  }

  async function updateCharts() {
    const params: any = {};
    if (form.driverName) {
      params.driver_name = form.driverName;
    }
    if (form.driverStatus) {
      const statusMap: Record<string, string> = {
        normal: "正常",
        slightFatigue: "轻微疲劳",
        fatigue: "疲劳",
        severeFatigue: "严重疲劳"
      };
      params.driver_status = statusMap[form.driverStatus] || form.driverStatus;
    }
    if (form.dateRange && form.dateRange.length === 2) {
      params.start_date = form.dateRange[0];
      params.end_date = form.dateRange[1];
    }

    if (dailyFatigueChartRef.value) {
      try {
        const res = (await getDriverMonitorDailyFatigue(params)) as any;
        if (res.code === 200 && res.data) {
          const chart = echarts.init(dailyFatigueChartRef.value);
          const sortedData = res.data.sort((a, b) =>
            a.date.localeCompare(b.date)
          );

          chart.setOption({
            tooltip: { trigger: "axis" },
            xAxis: {
              type: "category",
              data: sortedData.map(item => item.date),
              axisLabel: { color: "#666" }
            },
            yAxis: {
              type: "value",
              minInterval: 1,
              axisLabel: { color: "#666" }
            },
            series: [
              {
                type: "bar",
                data: sortedData.map(item => item.count),
                itemStyle: {
                  color: "#F56C6C",
                  borderRadius: [4, 4, 0, 0]
                },
                barWidth: "40%"
              }
            ]
          });
        }
      } catch (error) {
        console.error("获取每日疲劳统计失败", error);
      }
    }

    if (dmsTriggerChartRef.value) {
      try {
        const res = (await getDriverMonitorDailyDms(params)) as any;
        if (res.code === 200 && res.data) {
          const chart = echarts.init(dmsTriggerChartRef.value);
          const sortedData = res.data.sort((a, b) =>
            a.date.localeCompare(b.date)
          );

          chart.setOption({
            tooltip: { trigger: "axis" },
            xAxis: {
              type: "category",
              data: sortedData.map(item => item.date),
              axisLabel: { color: "#666" }
            },
            yAxis: {
              type: "value",
              minInterval: 1,
              axisLabel: { color: "#666" }
            },
            series: [
              {
                type: "line",
                data: sortedData.map(item => item.total_count),
                smooth: true,
                itemStyle: { color: "#409EFF" },
                areaStyle: {
                  color: {
                    type: "linear",
                    x: 0,
                    y: 0,
                    x2: 0,
                    y2: 1,
                    colorStops: [
                      { offset: 0, color: "rgba(64,158,255,0.3)" },
                      { offset: 1, color: "rgba(64,158,255,0.05)" }
                    ]
                  }
                }
              }
            ]
          });
        }
      } catch (error) {
        console.error("获取每日DMS统计失败", error);
      }
    }

    if (driverFatigueChartRef.value) {
      try {
        const res = (await getDriverMonitorDriverFatigue(params)) as any;
        if (res.code === 200 && res.data) {
          const chart = echarts.init(driverFatigueChartRef.value);

          chart.setOption({
            tooltip: { trigger: "axis" },
            xAxis: {
              type: "category",
              data: res.data.map(item => item.driver_name),
              axisLabel: { color: "#666" }
            },
            yAxis: {
              type: "value",
              minInterval: 1,
              axisLabel: { color: "#666" }
            },
            series: [
              {
                type: "bar",
                data: res.data.map(item => item.fatigue_count),
                itemStyle: {
                  color: "#E6A23C",
                  borderRadius: [4, 4, 0, 0]
                },
                barWidth: "40%"
              }
            ]
          });
        }
      } catch (error) {
        console.error("获取司机疲劳统计失败", error);
      }
    }
  }

  const resetForm = formEl => {
    if (!formEl) return;
    formEl.resetFields();
    onSearch();
  };

  onMounted(() => {
    onSearch();
  });

  return {
    form,
    loading,
    columns,
    dataList,
    pagination,
    selectedNum,
    statistics,
    dailyFatigueChartRef,
    dmsTriggerChartRef,
    driverFatigueChartRef,
    onSearch,
    resetForm,
    onbatchDel,
    onDetail,
    onEdit,
    onDelete,
    onAdd,
    handleSizeChange,
    onSelectionCancel,
    handleCurrentChange,
    handleSelectionChange
  };
}

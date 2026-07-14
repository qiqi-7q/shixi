import type { PaginationProps } from "@pureadmin/table";
import { type Ref, reactive, ref, onMounted, nextTick } from "vue";
import * as echarts from "echarts/core";
import { ElMessageBox } from "element-plus";
import {
  getTaskList,
  getTaskStats,
  createTask,
  updateTask,
  deleteTask
} from "@/api/system";
import { message } from "@/utils/message";
import dayjs from "dayjs";

export function useRole(
  tableRef: Ref,
  advancedFilters?: Ref<
    Array<{ field: string; operator: string; value: string | [string, string] }>
  >
) {
  const form = reactive({
    project: "",
    testTimeRange: "",
    testFeature: "",
    publisher: "",
    tester: "",
    taskStatus: "",
    is_kpi: ""
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
    completed: 0,
    inProgress: 0,
    notStarted: 0,
    notQualified: 0,
    pending: 0
  });

  const dailyChartRef = ref<HTMLElement>();
  const statusChartRef = ref<HTMLElement>();
  const featureChartRef = ref<HTMLElement>();

  const columns: TableColumnList = [
    {
      label: "勾选列",
      type: "selection",
      fixed: "left",
      reserveSelection: true
    },
    {
      label: "序号",
      type: "index",
      minWidth: 60
    },

    {
      label: "项目",
      prop: "project",
      minWidth: 120,
      showOverflowTooltip: true
    },
    {
      label: "测试版本",
      prop: "test_version",
      minWidth: 100,
      showOverflowTooltip: true,
      formatter: ({ test_version }) => test_version || "-"
    },
    {
      label: "时间",
      prop: "test_time",
      minWidth: 180,
      showOverflowTooltip: true,
      formatter: ({ test_time }) =>
        test_time ? dayjs(test_time).format("YYYY-MM-DD HH:mm:ss") : "-"
    },
    {
      label: "测试车辆 VIN",
      prop: "vin_code",
      minWidth: 180
    },
    {
      label: "测试功能",
      prop: "test_function",
      minWidth: 100,
      formatter: ({ test_function }) => test_function || "-"
    },
    {
      label: "任务描述",
      prop: "task_desc",
      minWidth: 180,
      align: "center",
      headerAlign: "center",
      slot: "task_desc"
    },
    {
      label: "测试里程",
      prop: "test_mileage",
      minWidth: 100,
      align: "center",
      formatter: ({ test_mileage }) =>
        test_mileage !== null && test_mileage !== undefined
          ? `${test_mileage}km`
          : "-"
    },
    {
      label: "任务发布人",
      prop: "task_publisher",
      minWidth: 100,
      formatter: ({ task_publisher }) => task_publisher || "-"
    },
    {
      label: "测试人员",
      prop: "test_person",
      minWidth: 100,
      formatter: ({ test_person }) => test_person || "-"
    },
    {
      label: "实际完成里程",
      prop: "actual_mileage",
      minWidth: 180,
      align: "center",
      formatter: ({ actual_mileage }) =>
        actual_mileage !== null && actual_mileage !== undefined
          ? `${actual_mileage}km`
          : "-"
    },
    {
      label: "任务达成率",
      prop: "task_achievement_rate",
      minWidth: 100,
      align: "center",
      formatter: ({ task_achievement_rate }) =>
        task_achievement_rate !== null && task_achievement_rate !== undefined
          ? `${task_achievement_rate}%`
          : "-"
    },
    {
      label: "任务状态",
      prop: "task_status",
      minWidth: 100,
      align: "center",
      formatter: ({ task_status }) => task_status || "-"
    },
    {
      label: "是否用于KPI统计",
      prop: "is_kpi",
      minWidth: 120,
      align: "center",
      formatter: ({ is_kpi }) => (is_kpi ? "是" : "否")
    },
    {
      label: "原因说明",
      prop: "reason_desc",
      minWidth: 140,
      align: "center",
      headerAlign: "center",
      slot: "reason_desc"
    },
    {
      label: "备注",
      prop: "remarks",
      width: 140,
      minWidth: 140,
      align: "center",
      headerAlign: "center",
      // slot: "remarks"
      showOverflowTooltip: true
    },
    {
      label: "操作",
      fixed: "right",
      minWidth: 200,
      align: "center",
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
    const ids = curSelected.map((item: any) => item.id);
    if (ids.length === 0) {
      message("请选择要删除的数据", { type: "warning" });
      return;
    }
    try {
      await ElMessageBox.confirm(
        `确认要删除选中的 ${ids.length} 条测试任务吗？`,
        "系统提示",
        {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          type: "warning",
          draggable: true
        }
      );
      await Promise.all(ids.map((id: number) => deleteTask(id)));
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
      await ElMessageBox.confirm(`确认要删除该测试任务吗？`, "系统提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
        draggable: true
      });
      const res: any = await deleteTask(row.id);
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

  // ===== 查询列表 =====
  async function onSearch() {
    loading.value = true;
    try {
      const params: Record<string, any> = {
        skip: (pagination.currentPage - 1) * pagination.pageSize,
        limit: pagination.pageSize
      };
      if (form.project) params.project = form.project;
      if (form.testFeature) params.test_function = form.testFeature;
      if (form.publisher) params.task_publisher = form.publisher;
      if (form.tester) params.test_person = form.tester;
      if (form.taskStatus) params.task_status = form.taskStatus;
      if (form.is_kpi !== "") params.is_kpi = form.is_kpi;
      // 日期范围
      if (form.testTimeRange && Array.isArray(form.testTimeRange)) {
        params.test_start_date = form.testTimeRange[0];
        params.test_end_date = form.testTimeRange[1];
      }

      // 并行请求列表和统计数据
      const [listRes, statsRes] = await Promise.all([
        getTaskList(params),
        getTaskStats({
          project: form.project || undefined,
          start_date:
            form.testTimeRange && Array.isArray(form.testTimeRange)
              ? form.testTimeRange[0]
              : undefined,
          end_date:
            form.testTimeRange && Array.isArray(form.testTimeRange)
              ? form.testTimeRange[1]
              : undefined
        })
      ]);

      if ((listRes as any).code === 200) {
        const data = (listRes as any).data || {};
        const list = data.items || [];
        dataList.value = list;
        pagination.total = data.total || list.length;

        // 更新统计数据
        if ((statsRes as any).code === 200 && (statsRes as any).data) {
          updateStatistics((statsRes as any).data);
          nextTick(() => updateCharts((statsRes as any).data));
        }
      } else {
        message((listRes as any).message || "查询失败", { type: "error" });
      }
    } catch (e) {
      message("查询失败", { type: "error" });
    } finally {
      loading.value = false;
    }
  }

  // ===== 统计 =====
  function updateStatistics(statsData: any) {
    const statusCounts = statsData.status_counts || [];
    statistics.total = statusCounts.reduce((sum, i) => sum + (i.count || 0), 0);
    statistics.completed =
      statusCounts.find(i => i.status === "完成")?.count || 0;
    statistics.inProgress =
      statusCounts.find(i => i.status === "进行中")?.count || 0;
    statistics.notStarted =
      statusCounts.find(i => i.status === "未开始")?.count || 0;
    statistics.notQualified =
      statusCounts.find(i => i.status === "未达标")?.count || 0;
    statistics.pending =
      statusCounts.find(i => i.status === "挂起")?.count || 0;
  }

  // ===== 图表 =====
  function updateCharts(statsData: any) {
    // 每日任务下发量
    const dailyCounts = statsData.daily_counts || [];
    if (dailyChartRef.value) {
      const chart = echarts.init(dailyChartRef.value);
      chart.setOption({
        tooltip: { trigger: "axis" },
        xAxis: {
          type: "category",
          data: dailyCounts.map(d => d.date),
          axisLabel: { color: "#666", rotate: 30 }
        },
        yAxis: { type: "value", minInterval: 1, axisLabel: { color: "#666" } },
        series: [
          {
            type: "line",
            data: dailyCounts.map(d => d.count),
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

    // 任务状态分布
    const statusCounts = statsData.status_counts || [];
    if (statusChartRef.value) {
      const chart = echarts.init(statusChartRef.value);
      chart.setOption({
        tooltip: { trigger: "item" },
        legend: { bottom: 10, left: "center" },
        series: [
          {
            type: "pie",
            radius: ["45%", "70%"],
            center: ["50%", "45%"],
            avoidLabelOverlap: false,
            label: { show: false },
            data: [
              {
                value: statusCounts.find(i => i.status === "完成")?.count || 0,
                name: "完成",
                itemStyle: { color: "#67C23A" }
              },
              {
                value:
                  statusCounts.find(i => i.status === "进行中")?.count || 0,
                name: "进行中",
                itemStyle: { color: "#409EFF" }
              },
              {
                value:
                  statusCounts.find(i => i.status === "未开始")?.count || 0,
                name: "未开始",
                itemStyle: { color: "#909399" }
              },
              {
                value:
                  statusCounts.find(i => i.status === "未达标")?.count || 0,
                name: "未达标",
                itemStyle: { color: "#F56C6C" }
              },
              {
                value: statusCounts.find(i => i.status === "挂起")?.count || 0,
                name: "挂起",
                itemStyle: { color: "#FF9900" }
              }
            ]
          }
        ]
      });
    }

    // 各功能任务量
    const functionCounts = statsData.function_counts || [];
    if (featureChartRef.value) {
      const chart = echarts.init(featureChartRef.value);
      chart.setOption({
        tooltip: { trigger: "axis" },
        xAxis: {
          type: "category",
          data: functionCounts.map(f => f.function),
          axisLabel: { color: "#666" }
        },
        yAxis: { type: "value", minInterval: 1, axisLabel: { color: "#666" } },
        series: [
          {
            type: "bar",
            data: functionCounts.map(f => f.count),
            itemStyle: {
              color: "#67C23A",
              borderRadius: [4, 4, 0, 0]
            },
            barWidth: "40%"
          }
        ]
      });
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
    dailyChartRef,
    statusChartRef,
    featureChartRef,
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

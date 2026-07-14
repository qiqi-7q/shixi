import { message } from "@/utils/message";
import type { PaginationProps } from "@pureadmin/table";
import { type Ref, reactive, ref, onMounted, nextTick } from "vue";
import * as echarts from "echarts/core";
import { ElMessageBox } from "element-plus";
import {
  getTestMilesList,
  getMileageStats,
  createTestMiles,
  updateTestMiles,
  deleteTestMiles
} from "@/api/system";
import dayjs from "dayjs";

export function useRole(tableRef: Ref, dialogRef: Ref) {
  // ===== 搜索表单 =====
  const form = reactive({
    project: "",
    version: "",
    testFeature: "",
    testTime: "" as string | [string, string]
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

  // 统计数据
  const statistics = reactive({
    totalMileage: 0,
    totalRecords: 0,
    napMileage: 0,
    cnapMileage: 0,
    lccMileage: 0,
    accMileage: 0
  });

  // 图表 refs
  const versionChartRef = ref<HTMLElement>();
  const dailyChartRef = ref<HTMLElement>();
  const featureChartRef = ref<HTMLElement>();

  // ===== 列配置 =====
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
      label: "项目",
      prop: "project",
      minWidth: 120
    },
    {
      label: "测试版本",
      prop: "test_version",
      minWidth: 100,
      align: "center",
      formatter: ({ test_version }) => test_version || "-"
    },
    {
      label: "测试开始时间",
      prop: "test_start_time",
      minWidth: 160,
      formatter: ({ test_start_time }) =>
        test_start_time
          ? dayjs(test_start_time).format("YYYY-MM-DD HH:mm:ss")
          : "-"
    },
    {
      label: "测试结束时间",
      prop: "test_end_time",
      minWidth: 160,
      formatter: ({ test_end_time }) =>
        test_end_time ? dayjs(test_end_time).format("YYYY-MM-DD HH:mm:ss") : "-"
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
      label: "功能测试里程 (km)",
      prop: "mileage",
      minWidth: 120,
      align: "center",
      formatter: ({ mileage }) =>
        mileage !== null && mileage !== undefined ? mileage : "-"
    },
    {
      label: "车辆行驶里程 (km)",
      prop: "driving_mileage",
      minWidth: 120,
      align: "center",
      formatter: ({ driving_mileage }) =>
        driving_mileage !== null && driving_mileage !== undefined
          ? driving_mileage
          : "-"
    },
    {
      label: "是否用于 KPI 统计",
      prop: "is_kpi",
      minWidth: 140,
      align: "center",
      formatter: ({ is_kpi }) => (is_kpi ? "是" : "否")
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
      minWidth: 160,
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
  }

  function onSelectionCancel() {
    selectedNum.value = 0;
    tableRef.value.getTableRef().clearSelection();
  }

  // ===== 批量删除 =====
  async function onbatchDel() {
    const curSelected = tableRef.value.getTableRef().getSelectionRows();
    const ids = curSelected.map((item: any) => item.id);
    if (ids.length === 0) {
      message("请选择要删除的数据", { type: "warning" });
      return;
    }
    try {
      await ElMessageBox.confirm(
        `确认要删除选中的 ${ids.length} 条里程记录吗？`,
        "系统提示",
        {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          type: "warning",
          draggable: true
        }
      );
      await Promise.all(ids.map((id: number) => deleteTestMiles(id)));
      message("批量删除成功", { type: "success" });
      tableRef.value.getTableRef().clearSelection();
      onSearch();
    } catch (e) {
      if (e !== "cancel") {
        message("批量删除失败", { type: "error" });
      }
    }
  }

  // ===== 操作按钮 =====
  function onDetail(row) {
    dialogRef.value.open("detail", row);
  }

  function onAdd() {
    dialogRef.value.open("add");
  }

  function onEdit(row) {
    dialogRef.value.open("edit", row);
  }

  async function onDelete(row) {
    try {
      await ElMessageBox.confirm(`确认要删除该里程记录吗？`, "系统提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
        draggable: true
      });
      const res: any = await deleteTestMiles(row.id);
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

  // ===== 新增 / 编辑保存 =====
  async function onSave(vals: Record<string, any>) {
    try {
      let res: any;
      if (vals.id) {
        res = await updateTestMiles(vals.id, vals);
      } else {
        res = await createTestMiles(vals);
      }
      if (res.code === 200) {
        message(vals.id ? "编辑成功" : "新增成功", { type: "success" });
        onSearch();
      } else {
        message(res.message || "操作失败", { type: "error" });
      }
    } catch (e) {
      message("操作失败", { type: "error" });
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
      if (form.version) params.test_version = form.version;
      if (form.testFeature) params.test_function = form.testFeature;
      // 日期范围
      if (form.testTime && Array.isArray(form.testTime)) {
        params.test_start_date = form.testTime[0];
        params.test_end_date = form.testTime[1];
      }

      // 并行请求列表和统计数据，互不影响
      const [listResult, statsResult] = (await Promise.allSettled([
        getTestMilesList(params),
        getMileageStats({
          project: form.project || undefined,
          version: form.version || undefined,
          test_function: form.testFeature || undefined,
          start_date:
            form.testTime && Array.isArray(form.testTime)
              ? form.testTime[0]
              : undefined,
          end_date:
            form.testTime && Array.isArray(form.testTime)
              ? form.testTime[1]
              : undefined
        })
      ])) as any;

      // 处理列表数据
      if (listResult.status === "fulfilled") {
        const listRes = listResult.value;
        if (listRes.code === 200) {
          const data = listRes.data || {};
          const list = data.items || [];
          dataList.value = list;
          pagination.total = data.total || list.length;
        } else {
          message(listRes.message || "查询列表失败", { type: "error" });
        }
      } else {
        message("查询列表失败", { type: "error" });
      }

      // 处理统计数据
      if (statsResult.status === "fulfilled") {
        const statsRes = statsResult.value;
        if (statsRes.code === 200 && statsRes.data) {
          updateStatistics(statsRes.data);
          nextTick(() => updateCharts(statsRes.data));
        }
      }
    } catch (e) {
      message("查询失败", { type: "error" });
    } finally {
      loading.value = false;
    }
  }

  // ===== 统计 =====
  function updateStatistics(statsData: any) {
    const overview = statsData.overview || {};
    statistics.totalRecords = overview.total_records || 0;
    statistics.totalMileage = overview.total_mileage || 0;
    statistics.napMileage = overview.nap || 0;
    statistics.cnapMileage = overview.cnap || 0;
  }

  // ===== 图表 =====
  function updateCharts(statsData: any) {
    // 版本里程柱状图
    const versionMileage = statsData.version_mileage || [];
    if (versionChartRef.value) {
      const chart = echarts.init(versionChartRef.value);
      chart.setOption({
        tooltip: { trigger: "axis", formatter: "{b}: {c} km" },
        xAxis: { type: "category", data: versionMileage.map(v => v.version) },
        yAxis: { type: "value", name: "里程 (km)" },
        series: [
          {
            type: "bar",
            data: versionMileage.map(v => v.total_mileage),
            itemStyle: { color: "#409EFF", borderRadius: [4, 4, 0, 0] },
            barWidth: "40%"
          }
        ]
      });
    }

    // 每日里程折线图
    const dailyMileage = statsData.daily_mileage || [];
    if (dailyChartRef.value) {
      const chart = echarts.init(dailyChartRef.value);
      chart.setOption({
        tooltip: { trigger: "axis", formatter: "{b}: {c} km" },
        xAxis: { type: "category", data: dailyMileage.map(d => d.date) },
        yAxis: { type: "value", name: "里程 (km)" },
        series: [
          {
            type: "line",
            data: dailyMileage.map(d => d.total_mileage),
            smooth: true,
            areaStyle: { opacity: 0.3 },
            itemStyle: { color: "#67C23A" }
          }
        ]
      });
    }

    // 功能里程饼图
    const functionMileage = statsData.function_mileage || [];
    if (featureChartRef.value) {
      const chart = echarts.init(featureChartRef.value);
      chart.setOption({
        tooltip: { trigger: "item", formatter: "{b}: {c} km ({d}%)" },
        legend: { bottom: 10, left: "center" },
        series: [
          {
            type: "pie",
            radius: ["45%", "70%"],
            center: ["50%", "45%"],
            label: { show: false },
            data: [
              {
                value:
                  functionMileage.find(f => f.function === "NAP")
                    ?.total_mileage || 0,
                name: "NAP",
                itemStyle: { color: "#409EFF" }
              },
              {
                value:
                  functionMileage.find(f => f.function === "CNAP")
                    ?.total_mileage || 0,
                name: "CNAP",
                itemStyle: { color: "#67C23A" }
              },
              {
                value:
                  functionMileage.find(f => f.function === "LCC")
                    ?.total_mileage || 0,
                name: "LCC",
                itemStyle: { color: "#E6A23C" }
              },
              {
                value:
                  functionMileage.find(f => f.function === "ACC")
                    ?.total_mileage || 0,
                name: "ACC",
                itemStyle: { color: "#F56C6C" }
              }
            ]
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
    versionChartRef,
    dailyChartRef,
    featureChartRef,
    onSearch,
    resetForm,
    onbatchDel,
    onDetail,
    onAdd,
    onEdit,
    onSave,
    onDelete,
    handleSizeChange,
    onSelectionCancel,
    handleCurrentChange,
    handleSelectionChange
  };
}

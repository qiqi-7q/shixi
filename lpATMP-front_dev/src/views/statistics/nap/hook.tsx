import type { PaginationProps } from "@pureadmin/table";
import { type Ref, reactive, ref, onMounted, nextTick } from "vue";
import * as echarts from "echarts/core";
import { ElMessageBox } from "element-plus";
import { message } from "@/utils/message";
import { useMultiTagsStoreHook } from "@/store/modules/multiTags";
import { useRouter } from "vue-router";
import dayjs from "dayjs";
import {
  getAnalysisList,
  getAnalysisDetail,
  deleteAnalysis,
  createAnalysis,
  getVersionStats,
  getAnalysisOverview,
  getFieldOptions
} from "@/api/system";

export function useRole(tableRef: Ref) {
  const router = useRouter();
  const form = reactive({
    project: "",
    carModel: "",
    version: "",
    funcMode: ""
  });

  const projectOptions = ref<string[]>([]);
  const carTypeOptions = ref<string[]>([]);
  const softwareVersionOptions = ref<string[]>([]);

  async function fetchFieldOptions() {
    try {
      const res: any = await getFieldOptions();
      if (res.code === 200 && res.data) {
        projectOptions.value = res.data.projects || [];
        carTypeOptions.value = res.data.car_types || [];
        softwareVersionOptions.value = res.data.software_versions || [];
      }
    } catch (e) {}
  }

  onMounted(() => {
    fetchFieldOptions();
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
    avgKpiMileage: 0,
    avgTotalScore: 0,
    maxTotalScore: 0
  });

  const versionScoreChartRef = ref<HTMLElement>();

  const columns: TableColumnList = [
    {
      label: "序号",
      minWidth: 70,
      type: "index"
    },

    {
      label: "项目",
      prop: "project",
      minWidth: 120,
      cellRenderer: ({ row }) => (
        <el-link
          type="primary"
          underline="never"
          onClick={() => handleProjectClick(row)}
        >
          {row.project || "-"}
        </el-link>
      )
    },
    {
      label: "车型",
      prop: "carModel",
      minWidth: 120,
      formatter: ({ carModel }) => carModel || "-"
    },
    {
      label: "版本",
      prop: "version",
      minWidth: 120,
      formatter: ({ version }) => version || "-"
    },
    {
      label: "功能模式",
      prop: "funcMode",
      minWidth: 140,
      formatter: ({ funcMode }) => funcMode || "-"
    },
    {
      label: "KPI里程",
      prop: "kpiMileage",
      minWidth: 120,
      formatter: ({ kpiMileage }) =>
        kpiMileage != null ? `${kpiMileage} km` : "-"
    },
    {
      label: "总分",
      prop: "totalScore",
      minWidth: 100,
      formatter: ({ totalScore }) => totalScore ?? "-"
    },
    {
      label: "创建时间",
      prop: "createTime",
      minWidth: 170,
      formatter: ({ createTime }) =>
        createTime ? dayjs(createTime).format("YYYY-MM-DD HH:mm:ss") : "-"
    },
    {
      label: "更新时间",
      prop: "updateTime",
      minWidth: 170,
      formatter: ({ updateTime }) =>
        updateTime ? dayjs(updateTime).format("YYYY-MM-DD HH:mm:ss") : "-"
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
      // Mock 删除操作
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

      const res: any = await deleteAnalysis(row.id);
      if (res?.code === 200) {
        message("删除成功", { type: "success" });
        onSearch();
      } else {
        message(res?.message || "删除失败", { type: "error" });
      }
    } catch (e) {
      if (e !== "cancel") {
        message("删除失败", { type: "error" });
      }
    }
  }

  function handleProjectClick(row) {
    router.push({
      name: "NapProjectDetail",
      params: { id: row.id },
      query: {
        project: row.project,
        carModel: row.carModel,
        version: row.version,
        funcMode: row.funcMode,
        kpiMileage: row.kpiMileage,
        totalScore: row.totalScore
      }
    });
  }

  async function onSearch() {
    loading.value = true;
    try {
      const skip = (pagination.currentPage - 1) * pagination.pageSize;
      const limit = pagination.pageSize;

      const params: any = {
        skip,
        limit
      };

      if (form.project) params.project = form.project;
      if (form.carModel) params.carModel = form.carModel;
      if (form.version) params.version = form.version;
      if (form.funcMode) params.funcMode = form.funcMode;

      const res: any = await getAnalysisList(params);

      if (res?.code === 200) {
        dataList.value = res.data || [];
        pagination.total = res.total || 0;

        // 调用总览统计接口
        const overviewRes: any = await getAnalysisOverview({
          project: form.project || undefined,
          carModel: form.carModel || undefined,
          funcMode: form.funcMode || undefined
        });

        if (overviewRes?.code === 200) {
          const overviewData = overviewRes.data;
          statistics.total = overviewData.total_records || 0;
          statistics.avgKpiMileage = overviewData.avg_mileage || 0;
          statistics.avgTotalScore = overviewData.avg_score || 0;
          statistics.maxTotalScore = overviewData.max_score || 0;
        }

        // nextTick(() => updateCharts(form.project));
      } else {
        message(res?.message || "获取数据失败", { type: "error" });
      }
    } catch (error) {
      message("获取数据失败", { type: "error" });
    } finally {
      loading.value = false;
    }
  }

  async function updateStatistics() {
    statistics.total = dataList.value.length;
    const totalMileage = dataList.value.reduce(
      (sum: number, item: any) => sum + (item.kpiMileage || 0),
      0
    );
    const totalScore = dataList.value.reduce(
      (sum: number, item: any) => sum + (item.totalScore || 0),
      0
    );
    statistics.avgKpiMileage =
      dataList.value.length > 0
        ? Number((totalMileage / dataList.value.length).toFixed(2))
        : 0;
    statistics.avgTotalScore =
      dataList.value.length > 0
        ? Number((totalScore / dataList.value.length).toFixed(2))
        : 0;
    statistics.maxTotalScore =
      dataList.value.length > 0
        ? Math.max(...dataList.value.map((item: any) => item.totalScore || 0))
        : 0;
  }

  async function updateCharts(projectFilter: string = "") {
    if (versionScoreChartRef.value) {
      try {
        // 调用版本得分统计接口
        const params: any = {};
        if (projectFilter) params.project = projectFilter;
        if (form.carModel) params.carModel = form.carModel;
        if (form.funcMode) params.funcMode = form.funcMode;

        const res: any = await getVersionStats(params);

        if (res?.code === 200) {
          const versionStats = res.data?.version_stats || [];

          if (versionStats.length === 0) {
            // 清空图表
            const chart = echarts.init(versionScoreChartRef.value);
            chart.clear();
            return;
          }

          const chart = echarts.init(versionScoreChartRef.value);
          chart.setOption({
            tooltip: {
              trigger: "axis",
              formatter: params => {
                const item = params[0];
                const dataIndex = item.dataIndex;
                const versionData = versionStats[dataIndex];
                return `${versionData.project} - ${versionData.version}<br/>平均得分: ${versionData.avg_score}<br/>总里程: ${versionData.total_mileage} km<br/>记录数: ${versionData.record_count}`;
              }
            },
            xAxis: {
              type: "category",
              data: versionStats.map((item: any) => item.version),
              axisLabel: { color: "#666", rotate: 30, interval: 0 }
            },
            yAxis: {
              type: "value",
              axisLabel: { color: "#666" }
            },
            series: [
              {
                type: "line",
                data: versionStats.map((item: any) => item.avg_score),
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
        console.error("获取版本得分统计失败:", error);
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
    versionScoreChartRef,
    projectOptions,
    carTypeOptions,
    softwareVersionOptions,
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
    handleSelectionChange,
    handleProjectClick,
    updateCharts
  };
}

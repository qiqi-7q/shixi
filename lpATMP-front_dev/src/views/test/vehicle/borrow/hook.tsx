  import { message } from "@/utils/message";
import type { PaginationProps } from "@pureadmin/table";
import { type Ref, reactive, ref, onMounted, nextTick } from "vue";
import * as echarts from "echarts/core";
import { toRaw } from "vue";
import { ElMessageBox } from "element-plus";
import dayjs from "dayjs";
import {
  getBorrowOverview,
  getBorrowStatusDistribution,
  advBorrowSearch,
  createBorrow,
  updateBorrow,
  deleteBorrow,
  returnVehicle,
  cancelBorrow
} from "@/api/system";

// ===== 借用状态转换 =====
const borrowStatusMap: Record<string, string> = {
  borrowing: "借用中",
  returned: "已归还",
  cancelled: "已取消",
  reserved: "已预约"
};

/** 转换借用状态为中文 */
function transformBorrowStatus(value: any): string {
  if (!value) return "";
  return borrowStatusMap[value] || value;
}

export function useRole(
  tableRef: Ref,
  advancedFilters?: Ref<
    Array<{ field: string; operator: string; value: string | [string, string] }>
  >
) {
  // ===== 搜索表单 =====
  const form = reactive({
    model: [] as string[],
    vin_code: "",
    borrow_status: "",
    driver_name: ""
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
    total: 0,
    borrowing: 0,
    returned: 0,
    cancelled: 0,
    reserved: 0
  });

  // 图表 refs
  const modelChartRef = ref<HTMLElement>();
  const statusChartRef = ref<HTMLElement>();

  const columns: TableColumnList = [
    {
      label: "序号",
      type: "index",
      width: 60
    },
    {
      label: "车型",
      prop: "model",
      minWidth: 100,
      formatter: ({ model }) => model || "-"
    },
    // {
    //   label: "车辆编号",
    //   prop: "vehicle_code",
    //   minWidth: 120,
    //   formatter: ({ vehicle_code }) => vehicle_code || "-"
    // },
    {
      label: "VIN 码",
      prop: "vin_code",
      minWidth: 170,
      formatter: ({ vin_code }) => vin_code || "-"
    },
    {
      label: "借用人",
      prop: "borrower",
      minWidth: 100,
      formatter: ({ borrower }) => borrower || "-"
    },
    {
      label: "借用时间",
      prop: "borrow_time",
      minWidth: 110,
      showOverflowTooltip: true,
      formatter: ({ borrow_time }) =>
        borrow_time ? dayjs(borrow_time).format("YYYY-MM-DD") : ""
    },
    {
      label: "借用状态",
      prop: "borrow_status",
      minWidth: 90,
      formatter: ({ borrow_status }) => transformBorrowStatus(borrow_status)
    },
    {
      label: "司机姓名",
      prop: "driver_name",
      minWidth: 100,
      formatter: ({ driver_name }) => driver_name || "-"
    },
    // {
    //   label: "司机工作安排",
    //   prop: "driver_work",
    //   minWidth: 160,
    //   showOverflowTooltip: true,
    //   formatter: ({ driver_work }) => driver_work || "-"
    // },
    // {
    //   label: "司机绩效",
    //   prop: "driver_performance",
    //   minWidth: 180,
    //   showOverflowTooltip: true,
    //   formatter: ({ driver_performance }) => driver_performance || "-"
    // },
    {
      label: "记录创建人",
      prop: "record_creator",
      minWidth: 100,
      formatter: ({ record_creator }) => record_creator || "-"
    },
    {
      label: "创建时间",
      prop: "created_at",
      minWidth: 110,
      formatter: ({ created_at }) =>
        created_at ? dayjs(created_at).format("YYYY-MM-DD HH:mm:ss") : ""
    },
    {
      label: "最后编辑时间",
      prop: "updated_at",
      minWidth: 110,
      formatter: ({ updated_at }) =>
        updated_at ? dayjs(updated_at).format("YYYY-MM-DD HH:mm:ss") : ""
    },
    {
      label: "备注",
      prop: "remarks",
      minWidth: 170,
      align: "center",
      // slot: "remarks"
      showOverflowTooltip: true,
      formatter: ({ remarks }) => remarks || "-"
    },
    { label: "操作", fixed: "right", width: 150, slot: "operation" }
  ];

  // ===== 操作按钮 =====
  function onAdd() {
    return { mode: "add" as const, row: null };
  }

  function onDetail(row) {
    return { mode: "detail" as const, row };
  }

  function onEdit(row) {
    return { mode: "edit" as const, row };
  }

  async function onDelete(row) {
    try {
      await ElMessageBox.confirm(`确认要删除该借用记录吗？`, "系统提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
        draggable: true
      });
      const res: any = await deleteBorrow(row.id);
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
        `确认要删除选中的 ${ids.length} 条借用记录吗？`,
        "系统提示",
        {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          type: "warning",
          draggable: true
        }
      );
      await Promise.all(ids.map((id: number) => deleteBorrow(id)));
      message("批量删除成功", { type: "success" });
      tableRef.value.getTableRef().clearSelection();
      onSearch();
    } catch (e) {
      if (e !== "cancel") {
        message("批量删除失败", { type: "error" });
      }
    }
  }

  // ===== 归还车辆 =====
  async function onReturn(row) {
    try {
      await ElMessageBox.confirm(`确认要归还该车辆吗？`, "系统提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
        draggable: true
      });
      const res: any = await returnVehicle(row.id);
      if (res.code === 200) {
        message("车辆已归还", { type: "success" });
        onSearch();
      } else {
        message(res.message || "归还失败", { type: "error" });
      }
    } catch (e) {
      if (e !== "cancel") {
        message("归还失败", { type: "error" });
      }
    }
  }

  // ===== 取消借用 =====
  async function onCancel(row) {
    try {
      await ElMessageBox.confirm(`确认要取消该借用记录吗？`, "系统提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
        draggable: true
      });
      const res: any = await cancelBorrow(row.id);
      if (res.code === 200) {
        message("借用记录取消成功", { type: "success" });
        onSearch();
      } else {
        message(res.message || "取消失败", { type: "error" });
      }
    } catch (e) {
      if (e !== "cancel") {
        message("取消失败", { type: "error" });
      }
    }
  }

  // ===== 新增/编辑保存 =====
  async function onSave(vals: Record<string, any>) {
    try {
      let res: any;
      if (vals.id) {
        res = await updateBorrow(vals.id, vals);
      } else {
        res = await createBorrow(vals);
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

  function buildFixConditions() {
    const conditions: object[] = [];
    const raw = toRaw(form);
    if (raw.model && raw.model.length > 0)
      conditions.push({
        advanced_field: "model",
        advanced_operator: "eq",
        advanced_value: raw.model.join(",")
      });
    if (raw.vin_code)
      conditions.push({
        advanced_field: "vin_code",
        advanced_operator: "icontains",
        advanced_value: raw.vin_code
      });
    if (raw.borrow_status)
      conditions.push({
        advanced_field: "borrow_status",
        advanced_operator: "eq",
        advanced_value: raw.borrow_status
      });
    if (raw.driver_name)
      conditions.push({
        advanced_field: "driver_name",
        advanced_operator: "icontains",
        advanced_value: raw.driver_name
      });
    return conditions;
  }

  // ===== 搜索（支持按条件过滤）=====
  async function onSearch() {
    loading.value = true;
    try {
      const skip = (pagination.currentPage - 1) * pagination.pageSize;
      const limit = pagination.pageSize;
      const params: any = { skip, limit };

      let res: any;
      const hasAdvanced = advancedFilters?.value?.length > 0;

      if (hasAdvanced) {
        const conditions = advancedFilters.value
          .filter(f => f.field && f.value)
          .map(f => ({
            advanced_field: f.field,
            advanced_operator:
              f.operator === "equals"
                ? "eq"
                : f.operator === "notEquals"
                  ? "neq"
                  : f.operator,
            advanced_value: f.value
          }));
        if (conditions.length === 0) {
          const fixConditions = buildFixConditions();
          res = await advBorrowSearch(fixConditions, params);
        } else {
          res = await advBorrowSearch(conditions, params);
        }
      } else {
        const conditions = buildFixConditions();
        res = await advBorrowSearch(conditions, params);
      }

      if (res.code === 200) {
        const list = Array.isArray(res.data.items) ? res.data.items : [];
        dataList.value = list;
        pagination.total = res.data.total || 0;
        nextTick(() => updateCharts());
      } else {
        message(res.message || "查询失败", { type: "error" });
      }
    } catch (e) {
      message("查询失败", { type: "error" });
    } finally {
      loading.value = false;
    }

    // 并行加载统计数据
    loadStats();
  }

  // ===== 统计（独立 API）=====
  async function loadStats() {
    try {
      const params: any = {};
      const raw = toRaw(form);
      if (raw.model && raw.model.length > 0) params.model = raw.model.join(",");
      if (raw.vin_code) params.vin_code = raw.vin_code;
      if (raw.borrow_status) params.borrow_status = raw.borrow_status;
      if (raw.driver_name) params.driver_name = raw.driver_name;

      const res: any = await getBorrowOverview(params);
      if (res.code === 200 && res.data) {
        statistics.total = res.data.total || 0;
        statistics.borrowing = res.data.borrowing || 0;
        statistics.returned = res.data.returned || 0;
        statistics.cancelled = res.data.cancelled || 0;
        statistics.reserved = res.data.reserved || 0;
      }
    } catch (e) {
      // 统计加载失败不影响主流程
    }
  }

  // 更新图表
  async function updateCharts() {
    const params: any = {};
    const raw = toRaw(form);
    if (raw.model && raw.model.length > 0) params.model = raw.model.join(",");
    if (raw.vin_code) params.vin_code = raw.vin_code;
    if (raw.borrow_status) params.borrow_status = raw.borrow_status;
    if (raw.driver_name) params.driver_name = raw.driver_name;

    // 车型统计（前端计算）
    const modelCount: Record<string, number> = {};
    dataList.value.forEach((item: any) => {
      modelCount[item.model] = (modelCount[item.model] || 0) + 1;
    });

    // 渲染车型柱状图
    if (modelChartRef.value) {
      const chart = echarts.init(modelChartRef.value);
      chart.setOption({
        tooltip: { trigger: "axis" },
        xAxis: {
          type: "category",
          data: Object.keys(modelCount),
          axisLabel: { color: "#666" }
        },
        yAxis: { type: "value", minInterval: 1, axisLabel: { color: "#666" } },
        series: [
          {
            type: "bar",
            data: Object.values(modelCount),
            itemStyle: {
              color: "#409EFF",
              borderRadius: [4, 4, 0, 0]
            },
            barWidth: "40%"
          }
        ]
      });
    }

    // 渲染借用状态环形图（调用后端 API）
    if (statusChartRef.value && false) {
      try {
        const res: any = await getBorrowStatusDistribution(params);
        if (res.code === 200 && res.data) {
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
                data: res.data.map((item: any) => {
                  const colorMap: Record<string, string> = {
                    借用中: "#409EFF",
                    已归还: "#67C23A",
                    已取消: "#909399",
                    已预定: "#E6A23C"
                  };
                  return {
                    value: item.count,
                    name: item.status,
                    itemStyle: { color: colorMap[item.status] || "#909399" }
                  };
                })
              }
            ]
          });
        }
      } catch (error) {
        console.error("获取借用状态分布统计失败", error);
      }
    }
  }

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
    modelChartRef,
    statusChartRef,
    onSearch,
    resetForm,
    onbatchDel,
    onDetail,
    onEdit,
    onDelete,
    onReturn,
    onCancel,
    onSave,
    onAdd,
    handleSizeChange,
    onSelectionCancel,
    handleCurrentChange,
    handleSelectionChange
  };
}

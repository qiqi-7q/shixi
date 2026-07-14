import { message } from "@/utils/message";
import type { PaginationProps } from "@pureadmin/table";
import { type Ref, reactive, ref, onMounted, nextTick } from "vue";
import * as echarts from "echarts/core";
import { toRaw } from "vue";
import { ElMessageBox } from "element-plus";
import dayjs from "dayjs";
import {
  advsearch,
  getVehicleOverview,
  getVehicleModelDistribution,
  createVehicle,
  updateVehicle,
  deleteVehicle,
  createBorrow,
  batchImportVehicle,
  returnVehicle,
  cancelBorrow,
  getBorrowedRecords
} from "@/api/system";

// ===== 枚举值转换 =====
// 使用状态
const vehicleStatusMap: Record<string, string> = {
  AVAILABLE: "可借用",
  BORROWED: "已借出",
  MAINTENANCE: "维护中",
  RESERVED: "已预定"
};

// 车辆组别
const vehicleGroupMap: Record<string, string> = {
  DRIVEING: "行车组",
  PARKING: "泊车组",
  WARNNING: "预警组"
};

// 车辆状态
const testStatusMap: Record<string, string> = {
  ALL_SUPPORT: "支持全部测试",
  NO_PARKING: "不支持泊车测试",
  NO_DRIVING: "不支持行车测试",
  NO_BACKWARNING: "不支持后向预警测试",
  NO_SUPPORT: "不支持全部测试",
  PRODUCING: "生产中",
  BORROWING: "外借中"
};

/** 转换枚举值为中文 */
function transformEnumValue(field: string, value: any): string {
  if (!value) return "";
  if (field === "vehicle_status") return vehicleStatusMap[value] || value;
  if (field === "group") return vehicleGroupMap[value] || value;
  if (field === "test_status") return testStatusMap[value] || value;
  return value;
}

export function useRole(
  tableRef: Ref,
  dialogRef: Ref,
  advancedFilters?: Ref<
    Array<{ field: string; operator: string; value: string | [string, string] }>
  >,
  borrowDialogRef?: Ref
) {
  // ===== 搜索表单 =====
  const form = reactive({
    model: [] as string[],
    vin_code: "",
    group: "",
    vehicle_status: "",
    test_status: ""
  });

  const dataList = ref([]);
  const loading = ref(true);
  const selectedNum = ref(0);
  const importDialogVisible = ref(false);
  const importLoading = ref(false);
  const importFile = ref<File | null>(null);

  const pagination = reactive<PaginationProps>({
    total: 0,
    pageSize: 10,
    currentPage: 1,
    background: true
  });

  // 排序状态
  const sortState = reactive({
    sort_by: "",
    sort_order: ""
  });

  // 存储所有过滤后的数据（用于图表/统计）
  let allFilteredData = [];

  // 统计数据
  const statistics = reactive({
    total: 0,
    available: 0,
    borrowed: 0,
    maintenance: 0,
    reserved: 0
  });

  // 车型分布图表
  const modelDistributionData = ref<{ model: string; count: number }[]>([]);
  const modelChartRef = ref<HTMLElement>();

  // 自定义图表
  interface CustomChart {
    id: number;
    config: {
      type: string;
      name: string;
      topN: number | null;
      filters: { field: string; operator: string; value: string }[];
      dimension: string;
      sortBy: string;
      sortOrder: string;
      colorScheme: string;
      showDataColumn: boolean;
    };
    elRef: HTMLElement;
  }
  const customCharts = ref<CustomChart[]>([]);
  let chartIdCounter = 0;

  // 操作符映射：前端 → 后端
  const operatorMap: Record<string, string> = {
    icontains: "icontains",
    equals: "eq",
    notEquals: "not_eq",
    startsWith: "startswith",
    endsWith: "endswith"
  };

  // ===== 列配置（snake_case 对齐 API）=====
  const columns: TableColumnList = [
    // {
    //   label: "勾选列",
    //   type: "selection",
    //   fixed: "left",
    //   reserveSelection: true,
    //   width: 50
    // },
    {
      label: "序号",
      type: "index",
      width: 60
    },
    {
      label: "车型",
      prop: "model",
      minWidth: 120,
      sortable: "custom"
    },
    {
      label: "组别",
      prop: "group",
      width: 80,
      sortable: "custom",
      formatter: ({ group }) => transformEnumValue("group", group)
    },
    {
      label: "临牌到期时间",
      prop: "temp_plate_expire_date",
      minWidth: 130,
      sortable: "custom",
      formatter: ({ temp_plate_expire_date }) =>
        temp_plate_expire_date
          ? dayjs(temp_plate_expire_date).format("YYYY-MM-DD")
          : ""
    },
    {
      label: "车辆阶段",
      prop: "vehicle_stage",
      minWidth: 100,
      sortable: "custom"
    },
    {
      label: "车辆配置",
      prop: "configuration",
      minWidth: 120,
      sortable: "custom"
    },
    {
      label: "车主权限",
      prop: "owner_name",
      minWidth: 100,
      sortable: "custom",
      formatter: ({ owner_name }) => owner_name || "-"
    },
    {
      label: "车辆编号",
      prop: "vehicle_code",
      minWidth: 110,
      sortable: "custom"
    },
    {
      label: "停车地点",
      prop: "parking_location",
      minWidth: 180,
      sortable: "custom"
    },
    {
      label: "使用状态",
      prop: "vehicle_status",
      minWidth: 90,
      sortable: "custom",
      formatter: ({ vehicle_status }) =>
        transformEnumValue("vehicle_status", vehicle_status)
    },
    {
      label: "车辆状态",
      prop: "test_status",
      minWidth: 140,
      sortable: "custom",
      formatter: ({ test_status }) =>
        transformEnumValue("test_status", test_status)
    },
    {
      label: "VIN 码",
      prop: "vin_code",
      minWidth: 180,
      sortable: "custom"
    },
    {
      label: "车牌号",
      prop: "plate_number",
      minWidth: 100,
      sortable: "custom"
    },
    {
      label: "驱动电机号/发动机号",
      prop: "engine_num",
      minWidth: 160,
      sortable: "custom",
      formatter: ({ engine_num }) => engine_num || "-"
    },

    {
      label: "临牌已办理次数",
      prop: "temp_plate_count",
      minWidth: 130,
      sortable: "custom"
    },
    {
      label: "备注",
      prop: "remarks",
      minWidth: 160,
      align: "center",
      headerAlign: "center",
      // slot: "remarks"
      showOverflowTooltip: true
    },
    {
      label: "创建时间",
      prop: "created_at",
      minWidth: 170,
      sortable: "custom",
      formatter: ({ created_at }) =>
        created_at ? dayjs(created_at).format("YYYY-MM-DD HH:mm:ss") : ""
    },
    {
      label: "最后编辑时间",
      prop: "updated_at",
      minWidth: 170,
      sortable: "custom",
      formatter: ({ updated_at }) =>
        updated_at ? dayjs(updated_at).format("YYYY-MM-DD HH:mm:ss") : ""
    },
    { label: "操作", fixed: "right", width: 150, slot: "operation" }
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

  function handleSortChange({ prop, order }) {
    if (prop && order) {
      sortState.sort_by = prop;
      sortState.sort_order = order === "ascending" ? "asc" : "desc";
    } else {
      sortState.sort_by = "created_at";
      sortState.sort_order = "desc";
    }
    pagination.currentPage = 1;
    onSearch();
  }

  function updatePageData() {
    const start = (pagination.currentPage - 1) * pagination.pageSize;
    const end = start + pagination.pageSize;
    dataList.value = allFilteredData.slice(start, end);
  }

  function handleSelectionChange(val) {
    selectedNum.value = val.length;
    tableRef.value.setAdaptive();
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
        `确认要删除选中的 ${ids.length} 条车辆资源吗？`,
        "系统提示",
        {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          type: "warning",
          draggable: true
        }
      );
      await Promise.all(ids.map((id: number) => deleteVehicle(id)));
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
  function onAdd() {
    dialogRef.value.open("add");
  }

  async function onBorrow(row: any) {
    if (borrowDialogRef?.value) {
      // 如果车辆状态是已借出或已预定，先查询其他借用记录
      let borrowedRecords: any[] = [];
      if (row.vehicle_status === "已借出" || row.vehicle_status === "已预定") {
        try {
          const res: any = await getBorrowedRecords({
            record_id: 0, // 新增记录，record_id 传 0 排除自身
            vehicle_id: row.id
          });
          if (res.code === 200 && res.data) {
            borrowedRecords = res.data;
          }
        } catch (e) {
          console.error("获取车辆其他借用记录失败", e);
        }
      }

      borrowDialogRef.value.open("add", {
        vehicle_id: row.id,
        model: row.model,
        vehicle_code: row.vehicle_code,
        vin_code: row.vin_code,
        group: row.group,
        vehicle_status: row.vehicle_status,
        borrowedRecords
      });
    }
  }

  async function onBorrowSave(data: any) {
    try {
      const res: any = await createBorrow(data);
      if (res.code === 200 || res.code === 201) {
        message("借用记录创建成功", { type: "success" });
        onSearch();
      } else {
        message(res.message || "创建失败", { type: "error" });
      }
    } catch (error: any) {
      console.error("创建借用记录失败:", error);
      message(error?.message || "创建借用记录失败", { type: "error" });
    }
  }

  async function onReturnVehicle(row: any) {
    try {
      await ElMessageBox.confirm("确认要归还该车辆吗？", "系统提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
        draggable: true
      });
      const res: any = await returnVehicle(row.borrow_id);
      if (res.code === 200) {
        message("归还成功", { type: "success" });
        onSearch();
      } else {
        message(res.message || "归还失败", { type: "error" });
      }
    } catch (error: any) {
      if (error !== "cancel") {
        message("归还失败", { type: "error" });
      }
    }
  }

  async function onCancelBorrow(row: any) {
    try {
      await ElMessageBox.confirm("确认要取消该借用记录吗？", "系统提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
        draggable: true
      });
      const res: any = await cancelBorrow(row.borrow_id);
      if (res.code === 200) {
        message("取消成功", { type: "success" });
        onSearch();
      } else {
        message(res.message || "取消失败", { type: "error" });
      }
    } catch (error: any) {
      if (error !== "cancel") {
        message("取消失败", { type: "error" });
      }
    }
  }

  function onImport() {
    importFile.value = null;
    importDialogVisible.value = true;
  }

  function handleFileChange(file: any) {
    importFile.value = file.raw;
  }

  function handleFileRemove() {
    importFile.value = null;
  }

  async function handleImport() {
    if (!importFile.value) {
      message("请选择Excel文件", { type: "warning" });
      return;
    }
    importLoading.value = true;
    try {
      const res: any = await batchImportVehicle(importFile.value);
      if (res?.msg || res?.message) {
        message(res.msg || res.message, { type: "success" });
        importDialogVisible.value = false;
        onSearch();
      } else {
        message("导入失败", { type: "error" });
      }
    } catch (error: any) {
      const errMsg =
        error?.response?.data?.detail ||
        error?.response?.data?.message ||
        error?.message ||
        "导入失败";
      message(errMsg, { type: "error" });
    } finally {
      importLoading.value = false;
    }
  }

  /** 下载导入模板 */
  async function onDownloadTemplate() {
    try {
      // 请求模板文件
      const res = await fetch("/车辆资源表.xlsx");
      if (!res.ok) throw new Error("文件不存在");

      // 转为二进制blob
      const blob = await res.blob();
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "车辆资源导入模板.xlsx";
      link.click();
      // 下载请求成功后再弹窗
      message("模板下载成功", { type: "success" });
      // 释放内存
      URL.revokeObjectURL(link.href);
    } catch (err) {
      message("模板下载失败，请稍后重试", { type: "error" });
      console.error(err);
    }
  }
  function onDetail(row) {
    dialogRef.value.open("detail", row);
  }

  function onEdit(row) {
    dialogRef.value.open("edit", row);
  }

  async function onDelete(row) {
    try {
      await ElMessageBox.confirm(`确认要删除该车辆资源吗？`, "系统提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
        draggable: true
      });
      const res: any = await deleteVehicle(row.id);
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
        res = await updateVehicle(vals.id, vals);
      } else {
        res = await createVehicle(vals);
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
    if (raw.group)
      conditions.push({
        advanced_field: "group",
        advanced_operator: "eq",
        advanced_value: raw.group
      });
    if (raw.vehicle_status)
      conditions.push({
        advanced_field: "vehicle_status",
        advanced_operator: "eq",
        advanced_value: raw.vehicle_status
      });
    if (raw.test_status)
      conditions.push({
        advanced_field: "test_status",
        advanced_operator: "eq",
        advanced_value: raw.test_status
      });
    return conditions;
  }

  // ===== 查询列表 =====
  async function onSearch() {
    loading.value = true;
    try {
      const skip = (pagination.currentPage - 1) * pagination.pageSize;
      const limit = pagination.pageSize;
      const params: any = { skip, limit };
      if (sortState.sort_by) params.sort_by = sortState.sort_by;
      if (sortState.sort_order) params.sort_order = sortState.sort_order;

      let res: any;
      const hasAdvanced = advancedFilters?.value?.length > 0;

      if (hasAdvanced) {
        const conditions = advancedFilters.value
          .filter(f => f.field && f.value)
          .map(f => ({
            advanced_field: f.field,
            advanced_operator: operatorMap[f.operator] || f.operator,
            advanced_value: f.value
          }));
        if (conditions.length === 0) {
          const fixConditions = buildFixConditions();
          res = await advsearch(fixConditions, params);
        } else {
          res = await advsearch(conditions, params);
        }
      } else {
        const conditions = buildFixConditions();
        res = await advsearch(conditions, params);
      }

      if (res.code === 200) {
        const list = Array.isArray(res.data.items) ? res.data.items : [];
        dataList.value = list;
        pagination.total = res.data.total || 0;
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
    const params: any = {};
    const raw = toRaw(form);
    if (raw.model && raw.model.length > 0) params.model = raw.model.join(",");
    if (raw.vin_code) params.vin_code = raw.vin_code;
    if (raw.group) params.group = raw.group;
    if (raw.vehicle_status) params.vehicle_status = raw.vehicle_status;
    if (raw.test_status) params.test_status = raw.test_status;

    try {
      const res: any = await getVehicleOverview(params);
      if (res.code === 200 && res.data) {
        statistics.total = res.data.total || 0;
        statistics.available = res.data.available || 0;
        statistics.borrowed = res.data.borrowed || 0;
        statistics.maintenance = res.data.maintenance || 0;
        statistics.reserved = res.data.reserved || 0;
      }
    } catch (e) {
      // 统计加载失败不影响主流程
    }

    // 加载车型分布图表数据
    try {
      const res: any = await getVehicleModelDistribution(params);
      if (res.code === 200 && res.data) {
        modelDistributionData.value = res.data;
        nextTick(() => renderModelChart());
      }
    } catch (e) {
      // 图表加载失败不影响主流程
    }
  }

  function renderModelChart() {
    if (!modelChartRef.value) return;
    const instance = echarts.init(modelChartRef.value);
    const data = modelDistributionData.value;
    instance.setOption({
      tooltip: {
        trigger: "axis",
        backgroundColor: "rgba(255,255,255,0.95)",
        borderColor: "#ebeef5",
        borderWidth: 1,
        textStyle: { color: "#303133", fontSize: 13 },
        formatter: params => {
          const p = params[0];
          return `<div style="padding:4px 0">
            <span style="font-weight:600">${p.name}</span><br/>
            <span style="color:#909399">车辆数：</span>
            <span style="font-weight:600;color:#409eff">${p.value}</span>
          </div>`;
        }
      },
      grid: { left: 50, right: 30, top: 30, bottom: 50, containLabel: false },
      xAxis: {
        type: "category",
        data: data.map(d => d.model),
        axisLine: { lineStyle: { color: "#ebeef5" } },
        axisTick: { show: false },
        axisLabel: {
          color: "#606266",
          fontSize: 12,
          rotate: data.length > 10 ? 30 : 0,
          interval: 0
        }
      },
      yAxis: {
        type: "value",
        splitLine: { lineStyle: { color: "#f2f6fc", type: "dashed" } },
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: "#909399", fontSize: 12 }
      },
      series: [
        {
          type: "bar",
          barWidth: "50%",
          data: data.map(d => d.count),
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: "#66b1ff" },
              { offset: 1, color: "#409eff" }
            ]),
            borderRadius: [4, 4, 0, 0]
          },
          emphasis: {
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: "#79bbff" },
                { offset: 1, color: "#66b1ff" }
              ])
            }
          },
          label: {
            show: true,
            position: "top",
            color: "#606266",
            fontSize: 11,
            fontWeight: 500
          }
        }
      ]
    });
  }

  // ===== 自定义图表 =====
  function addCustomChart(config: CustomChart["config"]) {
    chartIdCounter++;
    const chart: CustomChart = {
      id: chartIdCounter,
      config,
      elRef: null as any
    };
    customCharts.value.push(chart);
    nextTick(() => renderCustomChart(chart));
  }

  function setCustomChartRef(chartId: number, el: HTMLElement) {
    // const chart = customCharts.value.find(c => c.id === chartId);
    // if (chart) {
    //   chart.elRef = el;
    //   nextTick(() => renderCustomChart(chart));
    // }
  }

  function removeCustomChart(chartId: number) {
    const idx = customCharts.value.findIndex(c => c.id === chartId);
    if (idx !== -1) customCharts.value.splice(idx, 1);
  }

  function renderCustomChart(chart: CustomChart) {
    if (!chart.elRef) return;
    const instance = echarts.init(chart.elRef);
    const colors = getColorsByScheme(chart.config.colorScheme);
    const data = generateChartData(chart.config);

    if (chart.config.type === "pie" || chart.config.type === "ring") {
      const radius = chart.config.type === "ring" ? ["40%", "70%"] : "70%";
      instance.setOption({
        tooltip: { trigger: "item" },
        legend: { type: "scroll", orient: "vertical", right: 10, top: 20 },
        color: colors,
        series: [
          {
            type: "pie",
            radius,
            center: ["40%", "50%"],
            data: data.map((d, i) => ({
              ...d,
              itemStyle: { color: colors[i % colors.length] }
            })),
            label: { show: true, formatter: "{b}: {c}" }
          }
        ]
      });
    } else if (chart.config.type === "bar" || chart.config.type === "hbar") {
      const isH = chart.config.type === "hbar";
      instance.setOption({
        tooltip: { trigger: "axis" },
        color: colors,
        grid: { left: 60, right: 20, top: 20, bottom: 40 },
        xAxis: {
          type: isH ? "value" : "category",
          data: isH ? undefined : data.map(d => d.name)
        },
        yAxis: {
          type: isH ? "category" : "value",
          data: isH ? data.map(d => d.name) : undefined
        },
        series: [
          {
            type: "bar",
            data: data.map((d, i) => ({
              value: d.value,
              itemStyle: { color: colors[i % colors.length] }
            }))
          }
        ]
      });
    } else if (chart.config.type === "line") {
      instance.setOption({
        tooltip: { trigger: "axis" },
        color: colors,
        grid: { left: 60, right: 20, top: 20, bottom: 40 },
        xAxis: { type: "category", data: data.map(d => d.name) },
        yAxis: { type: "value" },
        series: [
          {
            type: "line",
            data: data.map(d => d.value),
            smooth: true,
            areaStyle: { opacity: 0.2 }
          }
        ]
      });
    }
  }

  function getColorsByScheme(scheme: string): string[] {
    const map: Record<string, string[]> = {
      色系1: ["#5B8FF9", "#5AD8A6", "#5D7092", "#F6BD16"],
      色系2: ["#6DC8EC", "#945FB9", "#FF9845", "#1E9493"],
      色系3: ["#FF99C3", "#FFE0ED", "#C9E9CA", "#87E8C7"]
    };
    return map[scheme] ?? map["色系1"];
  }

  function generateChartData(config: CustomChart["config"]) {
    // 基于当前查询结果按维度统计
    const dimFieldMap: Record<string, string> = {
      功能: "test_status",
      车型: "model",
      组别: "group",
      车辆阶段: "vehicle_stage",
      使用状态: "vehicle_status"
    };
    const field = dimFieldMap[config.dimension] || "model";
    const count: Record<string, number> = {};
    allFilteredData.forEach((item: any) => {
      const key = item[field] || "未知";
      count[key] = (count[key] || 0) + 1;
    });
    let data = Object.entries(count)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value);
    if (config.topN && config.topN > 0) data = data.slice(0, config.topN);
    return data;
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
    modelDistributionData,
    modelChartRef,
    customCharts,
    addCustomChart,
    setCustomChartRef,
    removeCustomChart,
    importDialogVisible,
    importLoading,
    importFile,
    onSearch,
    resetForm,
    onbatchDel,
    onDetail,
    onEdit,
    onSave,
    onDelete,
    onAdd,
    onBorrow,
    onBorrowSave,
    onReturnVehicle,
    onCancelBorrow,
    onImport,
    onDownloadTemplate,
    handleFileChange,
    handleFileRemove,
    handleImport,
    handleSizeChange,
    onSelectionCancel,
    handleCurrentChange,
    handleSelectionChange,
    handleSortChange
  };
}

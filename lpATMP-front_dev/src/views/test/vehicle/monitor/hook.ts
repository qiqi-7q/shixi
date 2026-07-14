import { ref, reactive, computed, onMounted } from "vue";
import type { PaginationProps } from "@pureadmin/table";
import type { FilterItem } from "@/components/ReAdvancedSearch";
import { ElMessageBox, ElMessage } from "element-plus";
import {
  getVehicleMonitor,
  advSearchVehicleMonitor,
  getCarInfo,
  getGroups,
  getVinList,
  getCarInfoByVin,
  getUsagesByDate
} from "@/api/system";

export function useMonitor() {
  const formRef = ref();
  const tableRef = ref();
  const advancedSearchRef = ref();
  const monitorDialogRef = ref();

  const loading = ref(false);
  const dataList = ref<any[]>([]);
  const selectedNum = ref(0);
  const advancedFilters = ref<FilterItem[]>([]);

  const form = reactive({
    vin_code: "",
    model: [] as string[],
    group: "",
    dateRange: [] as string[]
  });

  const pagination = reactive<PaginationProps>({
    total: 0,
    pageSize: 10,
    currentPage: 1,
    background: true,
    pageSizes: [10, 20, 50, 100]
  });

  const sortState = reactive({
    sort_by: "",
    sort_order: ""
  });

  const statistics = computed(() => ({
    total: pagination.total,
    powered: dataList.value.filter(item => item.power === 1).length,
    connected: dataList.value.filter(item => item.remoteMQ === 1).length,
    avgUsage:
      dataList.value.length > 0
        ? (
            dataList.value.reduce((sum, item) => sum + (item.usage || 0), 0) /
            dataList.value.length
          ).toFixed(2)
        : "0"
  }));

  const columns: TableColumnList = [
    // {
    //   type: "selection",
    //   width: 55,
    //   align: "center"
    // },

    {
      label: "车型",
      prop: "model",
      minWidth: 120,
      sortable: "custom"
    },
    {
      label: "组别",
      prop: "group",
      minWidth: 100,
      sortable: "custom"
    },
    {
      label: "车辆VIN号",
      prop: "vin_code",
      minWidth: 180,
      sortable: "custom"
    },
    {
      label: "日期",
      prop: "monitor_date",
      minWidth: 120,
      sortable: "custom"
    },
    {
      label: "上电时长（小时）",
      prop: "power_duration",
      minWidth: 100,
      sortable: "custom"
    },
    {
      label: "行驶里程（公里）",
      prop: "distance",
      minWidth: 100,
      sortable: "custom"
    },
    {
      label: "使用率（%）",
      prop: "usage",
      minWidth: 120,
      slot: "usage",
      sortable: "custom",
      align: "center",
      headerAlign: "center"
    }
    // {
    //   label: "操作",
    //   fixed: "right",
    //   width: 200,
    //   slot: "operation"
    // }
  ];

  const operatorMap: Record<string, string> = {
    icontains: "icontains",
    equals: "eq",
    notEquals: "not_eq",
    lt: "lt",
    lte: "lte",
    gt: "gt",
    gte: "gte",
    startsWith: "startswith",
    endsWith: "endswith"
  };

  const onSearch = async () => {
    loading.value = true;
    tableRef.value?.getTableRef().clearSelection();
    selectedNum.value = 0;
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
          const conditions = buildFixConditions();
          res = await advSearchVehicleMonitor(conditions, params);
        } else {
          res = await advSearchVehicleMonitor(conditions, params);
        }
      } else {
        const conditions = buildFixConditions();
        if (conditions.length === 0) {
          res = await advSearchVehicleMonitor([], params);
        } else {
          res = await advSearchVehicleMonitor(conditions, params);
        }
      }

      if (res?.code === 200 && res.data) {
        dataList.value = res.data.items || [];
        pagination.total = res.data.total || 0;
      } else {
        ElMessage.error(res?.message || "获取数据失败");
        dataList.value = [];
        pagination.total = 0;
      }
    } catch (error) {
      ElMessage.error("查询失败");
      dataList.value = [];
      pagination.total = 0;
    } finally {
      loading.value = false;
    }
  };

  function handleSortChange({ prop, order }) {
    if (prop && order) {
      sortState.sort_by = prop;
      sortState.sort_order = order === "ascending" ? "asc" : "desc";
    } else {
      sortState.sort_by = "";
      sortState.sort_order = "";
    }
    pagination.currentPage = 1;
    onSearch();
  }

  function buildFixConditions() {
    const conditions: object[] = [];
    if (form.vin_code)
      conditions.push({
        advanced_field: "vin_code",
        advanced_operator: "icontains",
        advanced_value: form.vin_code
      });
    if (form.model && form.model.length > 0)
      conditions.push({
        advanced_field: "model",
        advanced_operator: "eq",
        advanced_value: form.model.join(",")
      });
    if (form.group)
      conditions.push({
        advanced_field: "group",
        advanced_operator: "eq",
        advanced_value: form.group
      });
    if (form.dateRange && form.dateRange.length === 2)
      conditions.push({
        advanced_field: "monitor_date",
        advanced_operator: "between",
        advanced_value: form.dateRange
      });
    return conditions;
  }

  const handleReset = () => {
    form.vin_code = "";
    form.model = [];
    form.group = "";
    form.dateRange = [];
    advancedFilters.value = [];
    advancedSearchRef.value?.clearFilters();
    pagination.currentPage = 1;
    onSearch();
  };

  const handleSelectionChange = (selection: any[]) => {
    selectedNum.value = selection.length;
  };

  const handleSizeChange = (size: number) => {
    pagination.pageSize = size;
    pagination.currentPage = 1;
    onSearch();
  };

  const handleCurrentChange = (page: number) => {
    pagination.currentPage = page;
    onSearch();
  };

  const onSelectionCancel = () => {
    selectedNum.value = 0;
    tableRef.value?.getTableRef().clearSelection();
  };

  const onAdd = () => {
    monitorDialogRef.value?.open("add");
  };

  const onEdit = (row: any) => {
    monitorDialogRef.value?.open("edit", row);
  };

  const onDetail = async (row: any) => {
    try {
      const res: any = await getVehicleMonitor(row.id);
      if (res?.code === 200 && res.data) {
        monitorDialogRef.value?.open("detail", res.data);
      } else {
        ElMessage.error(res?.message || "获取详情失败");
      }
    } catch (error) {
      ElMessage.error("获取详情失败");
    }
  };

  const onDelete = async (row: any) => {
    try {
      await ElMessageBox.confirm("确认删除该车辆监控记录?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      });
      ElMessage.success("删除成功");
      onSearch();
    } catch (error) {
      if (error !== "cancel") {
        ElMessage.error("删除失败");
      }
    }
  };

  const onbatchDel = async () => {
    try {
      await ElMessageBox.confirm("确认删除选中的记录?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      });
      ElMessage.success("批量删除成功");
      onSearch();
    } catch (error) {
      if (error !== "cancel") {
        ElMessage.error("批量删除失败");
      }
    }
  };

  const handleCommand = (command: string, row: any) => {
    if (command === "detail") {
      onDetail(row);
    } else if (command === "delete") {
      onDelete(row);
    }
  };

  const onSave = (data: any) => {
    ElMessage.success("保存成功");
    onSearch();
  };

  onMounted(() => {
    onSearch();
  });

  return {
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
    getCarInfoByVin,
    getUsagesByDate
  };
}

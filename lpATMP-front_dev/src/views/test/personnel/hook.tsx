import { message } from "@/utils/message";
import type { PaginationProps } from "@pureadmin/table";
import { type Ref, reactive, ref, onMounted } from "vue";
import { ElMessageBox } from "element-plus";
import {
  getEmployeeList,
  createEmployee,
  updateEmployee,
  deleteEmployee
} from "@/api/system";

export function useRole(tableRef: Ref, dialogRef: Ref) {
  // ===== 搜索条件 =====
  const form = reactive({
    name: "",
    module_name: ""
  });

  const dataList = ref([]);
  const loading = ref(true);
  const selectedNum = ref(0);

  const pagination = reactive<PaginationProps>({
    total: 5,
    pageSize: 10,
    currentPage: 1,
    background: true
  });

  // 排序状态
  const sortState = reactive({
    sort_by: "",
    sort_order: ""
  });

  // ===== 列配置（人员管理）=====
  const columns: TableColumnList = [
  
    {
      label: "序号",
      minWidth: 70,
      align: "center",
      type: "index"
    },

    {
      label: "姓名",
      prop: "name",
      minWidth: 100,
      align: "center",
      sortable: "custom"
    },
    {
      label: "模块名称",
      prop: "module_name",
      minWidth: 120,
      align: "center",
      sortable: "custom",
      formatter: ({ module_name }) => module_name || "-"
    },
    {
      label: "模块负责人",
      prop: "module_manager",
      minWidth: 120,
      align: "center",
      sortable: "custom",
      formatter: ({ module_manager }) => module_manager || "-"
    },
    {
      label: "岗位类型",
      prop: "job_type",
      minWidth: 100,
      align: "center",
      sortable: "custom",
      formatter: ({ job_type }) => job_type || "-"
    },
    {
      label: "负责任务",
      prop: "task",
      minWidth: 120,
      align: "center",
      sortable: "custom",
      formatter: ({ task }) => task || "-"
    },
    {
      label: "内照有效期",
      prop: "card_validity",
      minWidth: 150,
      align: "center",
      sortable: "custom",
      formatter: ({ card_validity }) =>
        card_validity ? new Date(card_validity).toLocaleDateString() : "-"
    },
    {
      label: "创建时间",
      prop: "created_at",
      minWidth: 160,
      align: "center",
      sortable: "custom",
      formatter: ({ created_at }) =>
        created_at ? new Date(created_at).toLocaleString() : "-"
    },
    {
      label: "更新时间",
      prop: "updated_at",
      minWidth: 160,
      align: "center",
      sortable: "custom",
      formatter: ({ updated_at }) =>
        updated_at ? new Date(updated_at).toLocaleString() : "-"
    },
    {
      label: "操作",
      fixed: "right",
      align: "center",
      slot: "operation"
    }
  ];

  function handleSizeChange(val: number) {
    pagination.pageSize = val;
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
      sortState.sort_by = "";
      sortState.sort_order = "";
    }
    pagination.currentPage = 1;
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
        `确认要删除选中的 ${ids.length} 个人员吗？`,
        "系统提示",
        {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          type: "warning",
          draggable: true
        }
      );
      await Promise.all(ids.map((id: number) => deleteEmployee(id)));
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
    dialogRef.value.open("add", {});
  }

  function onDetail(row) {
    dialogRef.value.open("detail", row);
  }

  function onEdit(row) {
    dialogRef.value.open("edit", row);
  }

  async function onDelete(row) {
    try {
      await ElMessageBox.confirm(`确认要删除该人员吗？`, "系统提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
        draggable: true
      });
      const res: any = await deleteEmployee(row.id);
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
        // 编辑
        res = await updateEmployee(vals.id, vals);
      } else {
        // 新增
        res = await createEmployee(vals);
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
      if (sortState.sort_by) params.sort_by = sortState.sort_by;
      if (sortState.sort_order) params.sort_order = sortState.sort_order;
      if (form.name) params.name = form.name;
      if (form.module_name) params.module_name = form.module_name;
      const res: any = await getEmployeeList(params);
      if (res.code === 200) {
        const data = res.data || {};
        const list = data.items || [];
        dataList.value = list;
        pagination.total = data.total || list.length;
      } else {
        message(res.message || "查询失败", { type: "error" });
      }
    } catch (e) {
      message("查询失败", { type: "error" });
    } finally {
      loading.value = false;
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
    onSearch,
    resetForm,
    onbatchDel,
    onAdd,
    onDetail,
    onEdit,
    onSave,
    onDelete,
    handleSizeChange,
    onSelectionCancel,
    handleCurrentChange,
    handleSelectionChange,
    handleSortChange
  };
}

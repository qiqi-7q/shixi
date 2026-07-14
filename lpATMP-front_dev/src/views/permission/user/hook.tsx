import { message } from "@/utils/message";
import type { PaginationProps } from "@pureadmin/table";
import { type Ref, reactive, ref, onMounted, onActivated } from "vue";
import { ElMessageBox } from "element-plus";
import {
  getAuthUserList,
  createAuthUser,
  updateAuthUser,
  deleteAuthUser
} from "@/api/system";

export function useUserManage(tableRef: Ref, dialogRef: Ref) {
  const form = reactive({
    username: "",
    role: ""
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

  const sortState = reactive({
    sort_by: "",
    sort_order: ""
  });

  const columns: TableColumnList = [
    {
      label: "账号",
      prop: "username",
      minWidth: 120,
      align: "center",
      sortable: "custom"
    },
    {
      label: "姓名",
      prop: "full_name",
      minWidth: 120,
      align: "center",
      sortable: "custom",
      formatter: ({ full_name }) => full_name || "-"
    },
    {
      label: "邮箱",
      prop: "email",
      minWidth: 180,
      align: "center",
      sortable: "custom"
    },
    {
      label: "角色",
      prop: "role_name",
      minWidth: 100,
      align: "center",
      sortable: "custom",
      // formatter: ({ role }) => {
      //   if (role === "superuser") return "超级管理员";
      //   if (role === "admin") return "管理员";
      //   if (role === "user") return "普通用户";
      //   return role || "-";
      // }
    },
    {
      label: "状态",
      prop: "is_active",
      minWidth: 100,
      align: "center",
      sortable: "custom",
      slot: "is_active"
    },
    // {
    //   label: "超级管理员",
    //   prop: "is_superuser",
    //   minWidth: 120,
    //   align: "center",
    //   sortable: "custom",
    //   slot: "is_superuser"
    // },
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

  async function onbatchDel() {
    const curSelected = tableRef.value.getTableRef().getSelectionRows();
    const ids = curSelected.map((item: any) => item.id);
    if (ids.length === 0) {
      message("请选择要删除的数据", { type: "warning" });
      return;
    }
    try {
      await ElMessageBox.confirm(
        `确认要删除选中的 ${ids.length} 个用户吗？`,
        "系统提示",
        {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          type: "warning",
          draggable: true
        }
      );
      await Promise.all(ids.map((id: number) => deleteAuthUser(id)));
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
      await ElMessageBox.confirm(`确认要删除该用户吗？`, "系统提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
        draggable: true
      });
      const res: any = await deleteAuthUser(row.id);
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

  async function onSave(vals: Record<string, any>) {
    try {
      let res: any;
      if (vals.id) {
        res = await updateAuthUser(vals.id, vals);
      } else {
        res = await createAuthUser(vals);
      }
      if (res.code === 200 || res.code === 201) {
        message(vals.id ? "编辑成功" : "新增成功", { type: "success" });
        onSearch();
      } else {
        message(res.message || "操作失败", { type: "error" });
      }
    } catch (e) {
      message(e?.response?.data?.detail || e?.message || "操作失败", {
        type: "error"
      });
    }
  }

  async function onToggleActive(row: any) {
    try {
      const res: any = await updateAuthUser(row.id, {
        is_active: row.is_active
      });
      if (res.code === 200) {
        message("状态更新成功", { type: "success" });
      } else {
        message(res.message || "更新失败", { type: "error" });
        row.is_active = !row.is_active;
      }
    } catch (e: any) {
      message(e?.response?.data?.detail || e?.message || "更新失败", {
        type: "error"
      });
      row.is_active = !row.is_active;
    }
  }

  async function onToggleSuperuser(row: any) {
    try {
      const res: any = await updateAuthUser(row.id, {
        is_superuser: row.is_superuser
      });
      if (res.code === 200) {
        message("超级管理员状态更新成功", { type: "success" });
      } else {
        message(res.detail || res.message || "更新失败", { type: "error" });
        row.is_superuser = !row.is_superuser;
      }
    } catch (e: any) {
      message(e?.response?.data?.detail || e?.message || "更新失败", {
        type: "error"
      });
      row.is_superuser = !row.is_superuser;
    }
  }

  async function onSearch() {
    loading.value = true;
    try {
      const params: Record<string, any> = {
        skip: (pagination.currentPage - 1) * pagination.pageSize,
        limit: pagination.pageSize
      };
      if (sortState.sort_by) params.sort_by = sortState.sort_by;
      if (sortState.sort_order) params.sort_order = sortState.sort_order;
      if (form.username) params.username = form.username;
      if (form.role) params.role = form.role;
      const res: any = await getAuthUserList(params);
      if (res.code === 200) {
        const data = res.data || {};
        const list = Array.isArray(data) ? data : data.items || [];
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
    handleSortChange,
    onToggleActive,
    onToggleSuperuser
  };
}

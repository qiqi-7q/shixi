import { message } from "@/utils/message";
import type { PaginationProps } from "@pureadmin/table";
import { type Ref, reactive, ref, onMounted } from "vue";
import { ElMessageBox } from "element-plus";
import {
  getAuthRoleList,
  deleteAuthRole,
  getAuthRoleDetail
} from "@/api/system";

export function useRole(tableRef: Ref, dialogRef: Ref) {
  const form = reactive({
    search: ""
  });

  const dataList = ref([]);
  const loading = ref(true);
  const selectedNum = ref(0);
  const permissionMap = ref<Record<number, string>>({});

  const pagination = reactive<PaginationProps>({
    total: 0,
    pageSize: 10,
    currentPage: 1,
    background: true
  });

  const columns: TableColumnList = [
    {
      label: "序号",
      minWidth: 70,
      align: "center",
      type: "index"
    },
    {
      label: "角色名称",
      prop: "name",
      minWidth: 120,
      align: "center"
    },
    // {
    //   label: "角色编码",
    //   prop: "code",
    //   minWidth: 120,
    //   align: "center"
    // },
    {
      label: "描述",
      prop: "description",
      minWidth: 150,
      align: "center"
    },
    {
      label: "等级",
      prop: "level",
      minWidth: 80,
      align: "center",
      cellRenderer: ({ row }) => {
        const levelMap: Record<number, { label: string; type: string }> = {
          100: { label: "超级管理员", type: "danger" },
          50: { label: "管理员", type: "warning" },
          1: { label: "普通用户", type: "info" }
        };
        const info = levelMap[row.level] || {
          label: `Lv.${row.level}`,
          type: "info"
        };
        return (
          <el-tag type={info.type} size="small">
            {info.label}
          </el-tag>
        );
      }
    },
    {
      label: "权限数量",
      prop: "permissions",
      minWidth: 100,
      align: "center",
      cellRenderer: ({ row }) => {
        const count = row.permissions?.length || 0;
        return <el-tag type="success">{count}</el-tag>;
      }
    },
    {
      label: "创建时间",
      prop: "create_at",
      minWidth: 160,
      align: "center",
      cellRenderer: ({ row }) => {
        return row.create_at
          ? row.create_at.replace("T", " ").substring(0, 19)
          : "-";
      }
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
      message("请选择要删除的角色", { type: "warning" });
      return;
    }
    try {
      await ElMessageBox.confirm(
        `确认要删除选中的 ${curSelected.length} 个角色吗？`,
        "系统提示",
        {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          type: "warning",
          draggable: true
        }
      );
      for (const item of curSelected) {
        if (item.code === "superuser") {
          message("超级管理员角色不可删除", { type: "warning" });
          continue;
        }
        await deleteAuthRole(item.id);
      }
      message("批量删除成功", { type: "success" });
      tableRef.value.getTableRef().clearSelection();
      onSearch();
    } catch (eq) {
      if (eq !== "cancel") {
        const errorMsg =
          eq?.response?.data?.detail ||
          eq?.response?.data?.message ||
          eq?.message ||
          "批量删除失败";
        message(errorMsg, { type: "error" });
      }
    }
  }

  function onAdd() {
    dialogRef.value.open("add", {});
  }

  async function onEdit(row) {
    try {
      const res: any = await getAuthRoleDetail(row.id);
      const detail = { ...(res?.data || {}), id: row.id };
      dialogRef.value.open("edit", detail);
    } catch {
      // 获取详情失败，使用列表数据兜底
      dialogRef.value.open("edit", row);
    }
  }

  async function onDetail(row) {
    try {
      const res: any = await getAuthRoleDetail(row.id);
      const detail = { ...(res?.data || {}), id: row.id };
      dialogRef.value.open("detail", detail);
    } catch {
      dialogRef.value.open("detail", row);
    }
  }

  async function onDelete(row) {
    if (row.code === "superuser") {
      message("超级管理员角色不可删除", { type: "warning" });
      return;
    }
    try {
      await ElMessageBox.confirm(
        `确认要删除角色"${row.name}"吗？`,
        "系统提示",
        {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          type: "warning",
          draggable: true
        }
      );
      await deleteAuthRole(row.id);
      message("删除成功", { type: "success" });
      onSearch();
    } catch (e) {
      console.log("e:", e.response.data.detail || "删除失败");
      if (e !== "cancel") {
        message(e.response.data.detail || "删除失败", { type: "error" });
      }
    }
  }

  async function onSearch() {
    loading.value = true;
    try {
      const skip = (pagination.currentPage - 1) * pagination.pageSize;
      const res: any = await getAuthRoleList({
        skip,
        limit: pagination.pageSize,
        search: form.search || undefined
      });
      const result = res.data;
      if (result && Array.isArray(result.items)) {
        dataList.value = result.items;
        pagination.total = result.total || 0;
      } else {
        dataList.value = [];
        pagination.total = 0;
      }
    } catch (e) {
      message("获取角色列表失败", { type: "error" });
      dataList.value = [];
    } finally {
      loading.value = false;
    }
  }

  function resetForm(formEl: any) {
    if (!formEl) return;
    formEl.resetFields();
    form.search = "";
    pagination.currentPage = 1;
    onSearch();
  }

  async function handleSave(formData: any) {
    // message("保存成功", { type: "success" });
    onSearch();
  }

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
    onEdit,
    onDetail,
    onDelete,
    handleSave,
    handleSizeChange,
    onSelectionCancel,
    handleCurrentChange,
    handleSelectionChange
  };
}

import type { PaginationProps } from "@pureadmin/table";
import { type Ref, reactive, ref, onMounted } from "vue";
import { ElMessageBox } from "element-plus";
import { message } from "@/utils/message";
import {
  getRouteList,
  getRouteDetail,
  createRoute,
  updateRoute,
  deleteRoute
} from "@/api/system";

export function useRole(tableRef: Ref) {
  const form = reactive({
    test_func: "",
    diff: undefined as number | undefined as any,
    location: ""
  });

  const dataList = ref([]);
  const loading = ref(true);
  const selectedNum = ref(0);
  const sortState = reactive({
    prop: "",
    order: ""
  });

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
      type: "index"
    },
    {
      label: "路线名称",
      prop: "routeName",
      minWidth: 140,
      width: 130
    },
    {
      label: "路线创建人",
      prop: "creator",
      minWidth: 100
    },
    {
      label: "测试功能",
      prop: "testFunc",
      minWidth: 100
    },
    {
      label: "里程(km)",
      prop: "routeLength",
      minWidth: 130,
      width: 130,
      sortable: "custom"
    },
    {
      label: "难度系数",
      prop: "diff",
      minWidth: 90,
      width: 90
    },
    {
      label: "城市",
      prop: "location",
      minWidth: 140,
      width: 130
    },
    {
      label: "路线描述",
      prop: "routeDesc",
      minWidth: 200,
      slot: "routeDesc"
    },
    {
      label: "路线链接",
      prop: "routeLink",
      minWidth: 180,
      cellRenderer: ({ row }) => (
        <a
          href={row.routeLink}
          target="_blank"
          rel="noopener noreferrer"
          style="color: #3b82f6;"
          class="hover:underline"
          title={`跳转链接：${row.routeLink}`}
        >
          {row.routeLink}
        </a>
      )
    },
    {
      label: "路线特征",
      prop: "routeFeature",
      minWidth: 160,
      slot: "routeFeature"
    },
    {
      label: "备注",
      prop: "remark",
      minWidth: 140,
      slot: "remark"
    },
    {
      label: "操作",
      fixed: "right",
      slot: "operation",
      minWidth: 160
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

  function handleSortChange({ prop, order }) {
    sortState.prop = prop;
    sortState.order = order;
    pagination.currentPage = 1;
    onSearch();
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
        `确认要删除选中的 ${curSelected.length} 条路线吗？`,
        "系统提示",
        {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          type: "warning",
          draggable: true
        }
      );
      const ids = curSelected.map((item: any) => item.id);
      await Promise.all(ids.map((id: number) => deleteRoute(id)));
      message("批量删除成功", { type: "success" });
      tableRef.value.getTableRef().clearSelection();
      onSearch();
    } catch (e) {
      if (e !== "cancel") {
        message("批量删除失败", { type: "error" });
      }
    }
  }

  function onDetail(row) {
    return { mode: "detail" as const, row };
  }

  function onAdd() {
    return { mode: "add" as const, row: null };
  }

  function onEdit(row) {
    return { mode: "edit" as const, row };
  }

  async function onDelete(row) {
    try {
      await ElMessageBox.confirm(`确认要删除该路线吗？`, "系统提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
        draggable: true
      });
      const res: any = await deleteRoute(row.id);
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
      if (form.test_func) params.test_func = form.test_func;
      if (form.diff !== undefined && form.diff !== null && form.diff !== "") {
        params.diff = form.diff;
      }

      if (form.location) params.location = form.location;
      if (sortState.prop === "routeLength" && sortState.order) {
        params.order_by_length =
          sortState.order === "ascending" ? "asc" : "desc";
      }
      console.log("form.diff:", form.diff, params.diff);

      const res: any = await getRouteList(params);
      if (res.code === 200) {
        const items = res.data.items || [];
        dataList.value = items.map((item: any) => ({
          ...item,
          id: item.id,
          routeName: item.route_name,
          routeLength: item.route_length,
          diff: item.diff,
          testFunc: item.test_func,
          routeDesc: item.route_desc,
          routeFeature: item.route_feature,
          routeLink: item.route_link,
          remark: item.remark,
          creator: item.creator,
          createTime: item.create_time,
          updateTime: item.update_time
        }));
        pagination.total = res.data.total || 0;
      } else {
        message(res.message || "获取数据失败", { type: "error" });
      }
    } catch (e) {
      message("获取数据失败", { type: "error" });
    } finally {
      loading.value = false;
    }
  }

  const resetForm = formEl => {
    if (!formEl) return;
    formEl.resetFields();
    sortState.prop = "";
    sortState.order = "";
    tableRef.value.getTableRef().clearSort();
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
    onDetail,
    onAdd,
    onEdit,
    onDelete,
    handleSizeChange,
    onSelectionCancel,
    handleCurrentChange,
    handleSelectionChange,
    handleSortChange
  };
}

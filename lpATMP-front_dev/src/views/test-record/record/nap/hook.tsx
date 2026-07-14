import type { PaginationProps } from "@pureadmin/table";
import type { Ref } from "vue";
import { reactive, ref, onMounted } from "vue";
import type { FilterItem } from "@/components/ReAdvancedSearch";
import { ElMessageBox } from "element-plus";
import { message } from "@/utils/message";
import { useMultiTagsStoreHook } from "@/store/modules/multiTags";
import { useRouter } from "vue-router";
import dayjs from "dayjs";
import {
  getTestRecordList,
  getTestRecordDetail,
  deleteTestRecord,
  batchImportTestRecord,
  batchExportTestRecord,
  advsearchTestRecord,
  createTestRecord,
  updateTestRecord,
  getFieldOptions,
  getLabelQuery
} from "@/api/system";

export function useTestRecord(
  tableRef: Ref,
  advancedFilters: Ref<FilterItem[]>
) {
  const router = useRouter();
  const form = reactive({
    project: "",
    car_type: "",
    function_mode: "",
    issue_time: "",
    vin: "",
    evaluation_dimension: "",
    software_version: ""
  });

  // 数据字典选项配置
  const projectOptions = ref<string[]>([]);
  const carTypeOptions = ref<string[]>([]);
  const softwareVersionOptions = ref<string[]>([]);
  const problemDescOptions = ref<string[]>([]); // 问题描述
  const problemPhenomenonOptions = ref<string[]>([]); // 问题现象
  const vinCodeOptions = ref<string[]>([]); // 车辆VIN号
  const problemCategoryOptions = ref<string[]>([]); // 评价维度
  const takeoverTypeOptions = ref<string[]>([]); // 接管类型
  const problemSceneOptions = ref<string[]>([]); // 问题场景
  const kpiTypeOptions = ref<string[]>([]); // KPI项
  const problemTypeOptions = ref<string[]>([]); // 问题分类
  const analyzeResultOptions = ref<string[]>([]); // 分析结果
  const remarksOptions = ref<string[]>([]); // 备注

  async function fetchFieldOptions() {
    try {
      // 使用新的数据字典接口获取所有配置项（除了车型）
      const res: any = await getLabelQuery({ module_name: "test_records" });
      if (res.code === 200 && res.data) {
        // 根据 field 匹配对应的 options
        res.data.forEach((item: { field: string; labels: string[] }) => {
          switch (item.field) {
            case "project":
              projectOptions.value = item.labels || [];
              break;
            case "software_version":
              softwareVersionOptions.value = item.labels || [];
              break;
            case "problem_desc":
              problemDescOptions.value = item.labels || [];
              break;
            case "problem_phenomenon":
              problemPhenomenonOptions.value = item.labels || [];
              break;
            case "vin_code":
              vinCodeOptions.value = item.labels || [];
              break;
            case "problem_category":
              problemCategoryOptions.value = item.labels || [];
              break;
            case "takeover_type":
              takeoverTypeOptions.value = item.labels || [];
              break;
            case "problem_scene":
              problemSceneOptions.value = item.labels || [];
              break;
            case "kpi_type":
              kpiTypeOptions.value = item.labels || [];
              break;
            case "problem_type":
              problemTypeOptions.value = item.labels || [];
              break;
            case "analyze_result":
              analyzeResultOptions.value = item.labels || [];
              break;
            case "remarks":
              remarksOptions.value = item.labels || [];
              break;
          }
        });
      }

      // 车型保持原来的方法获取
      const fieldRes: any = await getFieldOptions();
      if (fieldRes.code === 200 && fieldRes.data) {
        carTypeOptions.value = fieldRes.data.car_types || [];
      }
    } catch (e) {}
  }

  const dataList = ref([]);
  const loading = ref(true);
  const selectedNum = ref(0);
  const importDialogVisible = ref(false);
  const importLoading = ref(false);
  const importFile = ref<File | null>(null);
  const editMap = ref({});

  // 操作符映射：前端 → 后端
  const operatorMap: Record<string, string> = {
    icontains: "icontains",
    equals: "eq",
    notEquals: "not_eq",
    startsWith: "startswith",
    endsWith: "endswith"
  };

  const pagination = reactive<PaginationProps>({
    total: 0,
    pageSize: 10,
    currentPage: 1,
    background: true
  });

  const columns: TableColumnList = [
    {
      label: "选择",
      type: "selection",
      width: 55
    },
    {
      label: "序号",
      minWidth: 70,
      type: "index"
    },
    {
      label: "项目",
      prop: "project",
      minWidth: 120,
      cellRenderer: ({ row, index }) => {
        const editRow = editMap.value[index];
        if (editRow?.editable) {
          return (
            <el-select
              style={{ minWidth: "150px" }}
              v-model={editRow.project}
              placeholder="请选择或输入项目"
              filterable
              clearable
              allow-create
              default-first-option
            >
              {projectOptions.value.map(p => (
                <el-option key={p} label={p} value={p} />
              ))}
            </el-select>
          );
        }
        return row.project ? (
          <p>{row.project}</p>
        ) : (
          <p class="text-gray-400">-</p>
        );
      }
    },
    {
      label: "车型",
      prop: "car_type",
      minWidth: 100,
      width: 100,
      cellRenderer: ({ row, index }) => {
        const editRow = editMap.value[index];
        if (editRow?.editable) {
          return (
            <el-select
              style={{ minWidth: "150px" }}
              v-model={editRow.car_type}
              placeholder="请选择车型"
              filterable
              clearable
            >
              {carTypeOptions.value.map(c => (
                <el-option key={c} label={c} value={c} />
              ))}
            </el-select>
          );
        }
        return row.car_type ? (
          <p>{row.car_type}</p>
        ) : (
          <p class="text-gray-400">-</p>
        );
      }
    },
    {
      label: "软件版本",
      prop: "software_version",
      minWidth: 120,
      cellRenderer: ({ row, index }) => {
        const editRow = editMap.value[index];
        if (editRow?.editable) {
          return (
            <el-select
              style={{ minWidth: "200px" }}
              v-model={editRow.software_version}
              placeholder="请选择或输入软件版本"
              filterable
              clearable
              allow-create
              default-first-option
            >
              {softwareVersionOptions.value.map(s => (
                <el-option key={s} label={s} value={s} />
              ))}
            </el-select>
          );
        }
        return row.software_version ? (
          <p>{row.software_version}</p>
        ) : (
          <p class="text-gray-400">-</p>
        );
      }
    },
    {
      label: "问题时间",
      prop: "problem_time",
      minWidth: 150,
      width: 150,
      cellRenderer: ({ row, index }) => {
        const editRow = editMap.value[index];
        if (editRow?.editable) {
          return (
            <el-date-picker
              v-model={editRow.problem_time}
              type="datetime"
              value-format="YYYY-MM-DDTHH:mm:ss"
              placeholder="请选择问题时间"
            />
          );
        }
        return row.problem_time ? (
          <p>{dayjs(row.problem_time).format("YYYY-MM-DD HH:mm")}</p>
        ) : (
          <p class="text-gray-400">-</p>
        );
      }
    },
    {
      label: "问题描述",
      prop: "problem_desc",
      minWidth: 200,
      cellRenderer: ({ row, index }) => {
        const editRow = editMap.value[index];
        if (editRow?.editable) {
          return (
            <el-select
              style={{ minWidth: "180px" }}
              v-model={editRow.problem_desc}
              placeholder="请选择或输入问题描述"
              filterable
              clearable
              allow-create
              default-first-option
            >
              {problemDescOptions.value.map(p => (
                <el-option key={p} label={p} value={p} />
              ))}
            </el-select>
          );
        }
        return row.problem_desc ? (
          <p>{row.problem_desc}</p>
        ) : (
          <p class="text-gray-400">-</p>
        );
      }
    },
    {
      label: "问题现象",
      prop: "problem_phenomenon",
      minWidth: 200,
      cellRenderer: ({ row, index }) => {
        const editRow = editMap.value[index];
        if (editRow?.editable) {
          return (
            <el-select
              style={{ minWidth: "180px" }}
              v-model={editRow.problem_phenomenon}
              placeholder="请选择或输入问题现象"
              filterable
              clearable
              allow-create
              default-first-option
            >
              {problemPhenomenonOptions.value.map(p => (
                <el-option key={p} label={p} value={p} />
              ))}
            </el-select>
          );
        }
        return row.problem_phenomenon ? (
          <p>{row.problem_phenomenon}</p>
        ) : (
          <p class="text-gray-400">-</p>
        );
      }
    },
    {
      label: "创建人",
      prop: "creator",
      minWidth: 180
      // cellRenderer: ({ row, index }) => {
      //   const editRow = editMap.value[index];
      //   if (editRow?.editable) {
      //     return (
      //       <el-input
      //         style={{ minWidth: "150px" }}
      //         v-model={editRow.creator}
      //         placeholder="请输入创建人"
      //       />
      //     );
      //   }
      //   return row.creator ? (
      //     <p>{row.creator}</p>
      //   ) : (
      //     <p class="text-gray-400">-</p>
      //   );
      // }
    },
    {
      label: "数据链接",
      prop: "data_link",
      minWidth: 140,
      cellRenderer: ({ row, index }) => {
        const editRow = editMap.value[index];
        if (editRow?.editable) {
          return (
            <el-input
              style={{ minWidth: "150px" }}
              v-model={editRow.data_link}
              placeholder="请输入数据链接"
            />
          );
        }
        if (row.data_link) {
          return (
            <el-link
              type="primary"
              underline="never"
              href={row.data_link}
              target="_blank"
              class="text-sm"
            >
              {row.data_link}
            </el-link>
          );
        }
        return <p class="text-gray-400">-</p>;
      }
    },
    {
      label: "车辆VIN号",
      prop: "vin_code",
      minWidth: 150,
      cellRenderer: ({ row, index }) => {
        const editRow = editMap.value[index];
        if (editRow?.editable) {
          return (
            <el-input
              style={{ minWidth: "150px" }}
              v-model={editRow.vin_code}
              placeholder="请输入VIN号"
              maxlength={17}
            />
          );
        }
        return row.vin_code ? (
          <p>{row.vin_code}</p>
        ) : (
          <p class="text-gray-400">-</p>
        );
      }
    },
    {
      label: "分析人员",
      prop: "analyze_user",
      minWidth: 100,
      cellRenderer: ({ row, index }) => {
        const editRow = editMap.value[index];
        if (editRow?.editable) {
          return (
            <el-input
              style={{ minWidth: "150px" }}
              v-model={editRow.analyze_user}
              placeholder="请输入分析人员"
            />
          );
        }
        return row.analyze_user ? (
          <p>{row.analyze_user}</p>
        ) : (
          <p class="text-gray-400">-</p>
        );
      }
    },
    {
      label: "评价维度",
      prop: "problem_category",
      minWidth: 150,
      cellRenderer: ({ row, index }) => {
        const editRow = editMap.value[index];
        if (editRow?.editable) {
          return (
            <el-select
              style={{ minWidth: "150px" }}
              v-model={editRow.problem_category}
              placeholder="请选择或输入评价维度"
              filterable
              clearable
              allow-create
              default-first-option
            >
              {problemCategoryOptions.value.map(p => (
                <el-option key={p} label={p} value={p} />
              ))}
            </el-select>
          );
        }
        return row.problem_category ? (
          <p>{row.problem_category}</p>
        ) : (
          <p class="text-gray-400">-</p>
        );
      }
    },
    {
      label: "接管类型",
      prop: "takeover_type",
      minWidth: 100,
      cellRenderer: ({ row, index }) => {
        const editRow = editMap.value[index];
        if (editRow?.editable) {
          return (
            <el-input
              style={{ minWidth: "150px" }}
              v-model={editRow.takeover_type}
              placeholder="请输入接管类型"
            />
          );
        }
        return row.takeover_type ? (
          <p>{row.takeover_type}</p>
        ) : (
          <p class="text-gray-400">-</p>
        );
      }
    },
    {
      label: "问题场景",
      prop: "problem_scene",
      minWidth: 120,
      cellRenderer: ({ row, index }) => {
        const editRow = editMap.value[index];
        if (editRow?.editable) {
          return (
            <el-select
              style={{ minWidth: "150px" }}
              v-model={editRow.problem_scene}
              placeholder="请选择或输入问题场景"
              filterable
              clearable
              allow-create
              default-first-option
            >
              {problemSceneOptions.value.map(p => (
                <el-option key={p} label={p} value={p} />
              ))}
            </el-select>
          );
        }
        return row.problem_scene ? (
          <p>{row.problem_scene}</p>
        ) : (
          <p class="text-gray-400">-</p>
        );
      }
    },
    {
      label: "KPI项",
      prop: "kpi_type",
      minWidth: 100,
      width: 100,
      cellRenderer: ({ row, index }) => {
        const editRow = editMap.value[index];
        if (editRow?.editable) {
          return (
            <el-select
              v-model={editRow.kpi_type}
              style={{ minWidth: "150px" }}
              placeholder="请选择或输入KPI项"
              filterable
              clearable
              allow-create
              default-first-option
            >
              {kpiTypeOptions.value.map(k => (
                <el-option key={k} label={k} value={k} />
              ))}
            </el-select>
          );
        }
        return row.kpi_type ? (
          <p>{row.kpi_type}</p>
        ) : (
          <p class="text-gray-400">-</p>
        );
      }
    },
    {
      label: "问题分类",
      prop: "problem_type",
      minWidth: 120,
      cellRenderer: ({ row, index }) => {
        const editRow = editMap.value[index];
        if (editRow?.editable) {
          return (
            <el-select
              style={{ minWidth: "150px" }}
              v-model={editRow.problem_type}
              placeholder="请选择或输入问题分类"
              filterable
              clearable
              allow-create
              default-first-option
            >
              {problemTypeOptions.value.map(p => (
                <el-option key={p} label={p} value={p} />
              ))}
            </el-select>
          );
        }
        return row.problem_type ? (
          <p>{row.problem_type}</p>
        ) : (
          <p class="text-gray-400">-</p>
        );
      }
    },
    {
      label: "分析结果",
      prop: "analyze_result",
      minWidth: 150,
      cellRenderer: ({ row, index }) => {
        const editRow = editMap.value[index];
        if (editRow?.editable) {
          return (
            <el-select
              style={{ minWidth: "180px" }}
              v-model={editRow.analyze_result}
              placeholder="请选择或输入分析结果"
              filterable
              clearable
              allow-create
              default-first-option
            >
              {analyzeResultOptions.value.map(a => (
                <el-option key={a} label={a} value={a} />
              ))}
            </el-select>
          );
        }
        return row.analyze_result ? (
          <p>{row.analyze_result}</p>
        ) : (
          <p class="text-gray-400">-</p>
        );
      }
    },
    {
      label: "Wetrack链接",
      prop: "wetrack_link",
      minWidth: 180,
      cellRenderer: ({ row, index }) => {
        const editRow = editMap.value[index];
        if (editRow?.editable) {
          return (
            <el-input
              style={{ minWidth: "140px" }}
              v-model={editRow.wetrack_link}
              placeholder="请输入Wetrack链接"
            />
          );
        }
        if (row.wetrack_link) {
          return (
            <el-link
              type="primary"
              underline="never"
              href={row.wetrack_link}
              target="_blank"
              class="text-sm"
            >
              {row.wetrack_link}
            </el-link>
          );
        }
        return <p class="text-gray-400">-</p>;
      }
    },
    {
      label: "分析附件",
      prop: "analyze_attach",
      minWidth: 120,
      width: 120,
      slot: "analyze_attach",
      align: "center"
    },
    {
      label: "功能模式",
      prop: "function_mode",
      minWidth: 100,
      cellRenderer: ({ row, index }) => {
        const editRow = editMap.value[index];
        if (editRow?.editable) {
          return (
            <el-select
              style={{ minWidth: "150px" }}
              v-model={editRow.function_mode}
              placeholder="请选择功能模式"
            >
              <el-option label="NAP" value="NAP" />
              <el-option label="CNAP" value="CNAP" />
              <el-option label="ACC/LCC" value="ACC/LCC" />
            </el-select>
          );
        }
        return row.function_mode ? (
          <p>{row.function_mode}</p>
        ) : (
          <p class="text-gray-400">-</p>
        );
      }
    },
    {
      label: "备注",
      prop: "remarks",
      minWidth: 140,
      width: 200,
      cellRenderer: ({ row, index }) => {
        const editRow = editMap.value[index];
        if (editRow?.editable) {
          return (
            <el-select
              style={{ minWidth: "180px" }}
              v-model={editRow.remarks}
              placeholder="请选择或输入备注"
              filterable
              clearable
              allow-create
              default-first-option
            >
              {remarksOptions.value.map(r => (
                <el-option key={r} label={r} value={r} />
              ))}
            </el-select>
          );
        }
        return row.remarks ? (
          <div style=" word-break: break-all; white-space: pre-wrap;">
            {row.remarks}
          </div>
        ) : (
          <p class="text-gray-400">-</p>
        );
      }
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

      const deletePromises = curSelected.map((row: any) =>
        deleteTestRecord(row.id)
      );
      const results = await Promise.all(deletePromises);

      const successCount = results.filter(
        (res: any) => res?.code === 200
      ).length;

      if (successCount > 0) {
        message(`成功删除 ${successCount} 条记录`, { type: "success" });
        tableRef.value.getTableRef().clearSelection();
        onSearch();
      } else {
        message("批量删除失败", { type: "error" });
      }
    } catch (e) {
      if (e !== "cancel") {
        message("批量删除失败", { type: "error" });
      }
    }
  }

  async function onAdd() {
    try {
      const res: any = await createTestRecord({});
      if (res?.code === 200) {
        message("新增成功，已进入编辑状态", {
          type: "success"
        });
        await onSearch();
        // 将新创建的第一行数据设置为编辑状态
        if (dataList.value.length > 0) {
          const newRow = dataList.value[0];
          editMap.value[0] = { ...newRow, editable: true };
        }
      } else {
        message(res?.message || "新增失败", { type: "error" });
      }
    } catch (error) {
      message("新增失败", { type: "error" });
    }
  }

  function onDetail(row) {
    return { mode: "detail" as const, row };
  }

  function onEdit(row, index) {
    // 创建行的深拷贝，避免直接修改原始数据
    editMap.value[index] = { ...row, editable: true };
  }

  async function onSave(index) {
    const editRow = editMap.value[index];
    if (!editRow) return;

    try {
      const { editable, ...dataToSave } = editRow;

      const baseUrl = import.meta.env.VITE_PROXY_DOMAIN_REAL || "";
      if (
        dataToSave.analyze_attach &&
        Array.isArray(dataToSave.analyze_attach)
      ) {
        dataToSave.analyze_attach = dataToSave.analyze_attach.map(
          (url: string) =>
            url.startsWith("http") ? url.replace(baseUrl, "") : url
        );
      }

      const res: any = await updateTestRecord(dataToSave.id, dataToSave);
      if (res?.code === 200) {
        message("保存成功", { type: "success" });
        // 清除编辑状态
        delete editMap.value[index];
        onSearch();
      } else {
        message(res?.message || "保存失败", { type: "error" });
      }
    } catch (error) {
      message("保存失败", { type: "error" });
    }
  }

  function onCancel(index) {
    if (!editMap.value[index]) return;
    delete editMap.value[index];
    onSearch();
  }

  async function onDelete(row) {
    try {
      await ElMessageBox.confirm(`确认要删除该记录吗？`, "系统提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
        draggable: true
      });

      const res: any = await deleteTestRecord(row.id);
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

  async function onSearch() {
    loading.value = true;
    // 清空选中状态
    tableRef.value.getTableRef().clearSelection();
    selectedNum.value = 0;
    try {
      const hasAdvanced = advancedFilters?.value?.length > 0;
      const skip = (pagination.currentPage - 1) * pagination.pageSize;
      const limit = pagination.pageSize;
      let res: any;

      if (hasAdvanced) {
        // 高级查询：转换条件格式
        const conditions = advancedFilters.value
          .filter(f => f.field && f.value)
          .map(f => ({
            advanced_field: f.field,
            advanced_operator: operatorMap[f.operator] || f.operator,
            advanced_value: f.value
          }));

        // 如果过滤后条件为空，走普通搜索
        if (conditions.length === 0) {
          const params: any = { skip, limit };
          if (form.project) params.project = form.project;
          if (form.car_type) params.car_type = form.car_type;
          if (form.function_mode) params.function_mode = form.function_mode;
          if (form.issue_time) params.issue_time = form.issue_time;
          if (form.vin) params.vin = form.vin;
          if (form.evaluation_dimension)
            params.evaluation_dimension = form.evaluation_dimension;
          if (form.software_version)
            params.software_version = form.software_version;
          res = await getTestRecordList(params);
        } else {
          res = await advsearchTestRecord(conditions, { skip, limit });
        }
      } else {
        // 固定字段查询
        const params: any = { skip, limit };
        if (form.project) params.project = form.project;
        if (form.car_type) params.car_type = form.car_type;
        if (form.function_mode) params.function_mode = form.function_mode;
        if (form.issue_time) params.issue_time = form.issue_time;
        if (form.vin) params.vin = form.vin;
        if (form.evaluation_dimension)
          params.evaluation_dimension = form.evaluation_dimension;
        if (form.software_version)
          params.software_version = form.software_version;
        res = await getTestRecordList(params);
      }

      if (res?.code === 200) {
        dataList.value = res.data.items || [];
        pagination.total = res.data.total || 0;
      } else {
        message(res?.message || "获取数据失败", { type: "error" });
      }
    } catch (error) {
      message("获取数据失败", { type: "error" });
    } finally {
      loading.value = false;
    }
  }

  const resetForm = formEl => {
    if (!formEl) return;
    formEl.resetFields();
    onSearch();
  };

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
      const res: any = await batchImportTestRecord(importFile.value);
      if (res?.msg) {
        message(res.msg, { type: "success" });
        importDialogVisible.value = false;
        onSearch();
      } else {
        message(res?.message || "导入失败", { type: "error" });
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

  async function onExport() {
    try {
      const params: any = {};

      // 如果有选中的记录，使用选中的ID进行导出
      const curSelected = tableRef.value.getTableRef().getSelectionRows();
      if (curSelected.length > 0) {
        params.record_ids = curSelected.map((row: any) => row.id).join(",");
      } else {
        // 否则使用筛选条件
        if (form.project) params.project = form.project;
        if (form.car_type) params.car_type = form.car_type;
        if (form.function_mode) params.function_mode = form.function_mode;
        if (form.evaluation_dimension)
          params.problem_category = form.evaluation_dimension;
        if (form.software_version)
          params.software_version = form.software_version;
      }

      const res: any = await batchExportTestRecord(params);

      if (res instanceof Blob) {
        const url = window.URL.createObjectURL(res);
        const link = document.createElement("a");
        link.href = url;
        link.download = `test_records_export_${dayjs().format("YYYYMMDDHHmmss")}.xlsx`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        message("文件已开始导出，请查看浏览器下载栏", { type: "success" });
      } else if (res?.message) {
        message(res.message, { type: "error" });
      } else {
        message("导出失败", { type: "error" });
      }
    } catch (error) {
      message("导出失败", { type: "error" });
    }
  }

  /** 下载导入模板 */
  async function onDownloadTemplate() {
    try {
      const response = await fetch("/NAP测试记录导入模板.xlsx");
      if (!response.ok) {
        throw new Error("模板文件不存在");
      }
      const blob = await response.blob();
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "NAP测试记录导入模板.xlsx";
      link.click();
      URL.revokeObjectURL(link.href);
      message("模板下载成功", { type: "success" });
    } catch (error) {
      message("模板下载失败，请检查文件是否存在", { type: "error" });
      console.error(error);
    }
  }

  onMounted(() => {
    fetchFieldOptions();
    onSearch();
  });

  return {
    form,
    loading,
    columns,
    dataList,
    pagination,
    selectedNum,
    importDialogVisible,
    importLoading,
    importFile,
    editMap,
    projectOptions,
    carTypeOptions,
    softwareVersionOptions,
    onSearch,
    resetForm,
    onbatchDel,
    onDetail,
    onEdit,
    onSave,
    onCancel,
    onDelete,
    onAdd,
    onImport,
    handleFileChange,
    handleFileRemove,
    handleImport,
    onExport,
    onDownloadTemplate,
    handleSizeChange,
    onSelectionCancel,
    handleCurrentChange,
    handleSelectionChange
  };
}

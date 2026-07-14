<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from "vue";
import "plus-pro-components/es/components/dialog-form/style/css";
import {
  type PlusColumn,
  type FieldValues,
  PlusDialogForm
} from "plus-pro-components";
import { message } from "@/utils/message";
import {
  createAnalysis,
  getAnalysisDetail,
  getFieldOptions
} from "@/api/system";

const emit = defineEmits<{
  (e: "save", data: FieldValues): void;
}>();

const visible = ref(false);
const dialogKey = ref(0);
const values = ref<FieldValues>({});
const currentMode = ref<"add" | "edit" | "detail">("add");
const loading = ref(false);
const currentId = ref<number | null>(null);

const isDetail = computed(() => currentMode.value === "detail");

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

const formColumns = computed(
  () =>
    [
      {
        label: "项目",
        prop: "project",
        valueType: "select",
        fieldProps: {
          placeholder: "请选择项目",
          disabled: isDetail.value,
          filterable: true,
          options: projectOptions.value.map(p => ({ label: p, value: p }))
        },
        formItemProps: {
          rules: [{ required: true, message: "请选择项目", trigger: "change" }]
        }
      },
      {
        label: "车型",
        prop: "carModel",
        valueType: "select",
        fieldProps: {
          placeholder: "请选择车型",
          disabled: isDetail.value,
          filterable: true,
          options: carTypeOptions.value.map(c => ({ label: c, value: c }))
        },
        formItemProps: {
          rules: [{ required: true, message: "请选择车型", trigger: "change" }]
        }
      },
      {
        label: "版本",
        prop: "version",
        valueType: "select",
        fieldProps: {
          placeholder: "请选择或输入版本",
          disabled: isDetail.value,
          filterable: true,
          multiple: true,
          allowCreate: true,
          defaultFirstOption: true,
          options: softwareVersionOptions.value.map(s => ({
            label: s,
            value: s
          }))
        },
        formItemProps: {
          rules: [
            { required: true, message: "请选择或输入版本", trigger: "change" }
          ]
        }
      },
      {
        label: "功能模式",
        prop: "funcMode",
        valueType: "select",
        fieldProps: {
          placeholder: "请选择功能模式",
          disabled: isDetail.value,
          options: [
            { label: "NAP", value: "NAP" },
            { label: "CNAP", value: "CNAP" },
            { label: "ACC/LCC", value: "ACC/LCC" }
          ]
        },
        formItemProps: {
          rules: [
            { required: true, message: "请选择功能模式", trigger: "change" }
          ]
        }
      }
    ] as PlusColumn[]
);

const titleMap = {
  add: "新增NAP记录",
  edit: "编辑NAP记录",
  detail: "NAP详情"
};

const dialogTitle = computed(() => titleMap[currentMode.value]);

const open = async (
  mode: "add" | "edit" | "detail",
  data?: Record<string, any>
) => {
  currentMode.value = mode;
  if (mode === "edit" || mode === "detail") {
    currentId.value = data?.id || null;

    if (data?.id) {
      try {
        loading.value = true;
        const res: any = await getAnalysisDetail(data.id);
        if (res?.code === 200 && res.data) {
          const detail = res.data;
          values.value = {
            project: detail.project,
            carModel: detail.carModel,
            version: detail.version,
            funcMode: detail.funcMode
          };
        } else {
          message(res?.message || "获取详情失败", { type: "error" });
        }
      } catch (error) {
        message("获取详情失败", { type: "error" });
      } finally {
        loading.value = false;
      }
    }
  } else {
    currentId.value = null;
    values.value = {};
  }
  nextTick(() => {
    dialogKey.value++;
    visible.value = true;
  });
};

const handleSubmit = async (vals: FieldValues) => {
  loading.value = true;
  try {
    if (currentMode.value === "add") {
      const versionStr = Array.isArray(vals.version)
        ? vals.version.join(",")
        : vals.version;
      const res: any = await createAnalysis({
        project: vals.project,
        model: vals.carModel,
        version: versionStr,
        funcMode: vals.funcMode
      });

      if (res?.code === 200) {
        message("创建成功", { type: "success" });
        emit("save", vals);
        visible.value = false;
      } else {
        message(res?.message || "创建失败", { type: "error" });
      }
    } else if (currentMode.value === "edit") {
      message("更新成功", { type: "success" });
      emit("save", vals);
      visible.value = false;
    }
  } catch (error) {
    message("操作失败", { type: "error" });
  } finally {
    loading.value = false;
  }
};

defineExpose({ open });
</script>

<template>
  <PlusDialogForm
    :key="dialogKey"
    v-model:visible="visible"
    v-model="values"
    :form="{
      columns: formColumns,
      labelPosition: 'right',
      labelWidth: '120px'
    }"
    :title="dialogTitle"
    :show-submit-btn="currentMode !== 'detail'"
    :show-cancel-btn="true"
    confirm-text="保存"
    cancel-text="取消"
    @confirm="handleSubmit"
    :has-footer="currentMode !== 'detail'"
  />
</template>

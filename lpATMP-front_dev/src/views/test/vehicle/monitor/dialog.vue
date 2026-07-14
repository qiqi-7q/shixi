<script setup lang="ts">
import { ref, computed, nextTick } from "vue";
import "plus-pro-components/es/components/dialog-form/style/css";
import {
  type PlusColumn,
  type FieldValues,
  PlusDialogForm
} from "plus-pro-components";
import { getVehicleModels } from "@/api/system";

const emit = defineEmits<{
  (e: "save", data: FieldValues): void;
}>();

const visible = ref(false);
const dialogKey = ref(0);
const values = ref<FieldValues>({});
const currentMode = ref<"add" | "edit" | "detail">("add");
const isDetail = computed(() => currentMode.value === "detail");

const modelOptions = ref<string[]>([]);

async function fetchModels() {
  try {
    const res: any = await getVehicleModels();
    if (res?.code === 200 && Array.isArray(res.data)) {
      modelOptions.value = res.data;
    }
  } catch (e) {}
}

const formColumns = computed<PlusColumn[]>(() => [
  {
    label: "车型",
    prop: "model",
    valueType: "select",
    options: modelOptions.value.map(m => ({ label: m, value: m })),
    fieldProps: {
      placeholder: "请选择车型",
      filterable: true,
      clearable: true,
      disabled: isDetail.value
    },
    formItemProps: {
      rules: [{ required: true, message: "请选择车型", trigger: "change" }]
    }
  },
  {
    label: "组别",
    prop: "group",
    valueType: "select",
    fieldProps: {
      placeholder: "请选择组别",
      clearable: true,
      disabled: isDetail.value
    },
    options: [
      { label: "行车组", value: "行车组" },
      { label: "泊车组", value: "泊车组" },
      { label: "预警组", value: "预警组" }
    ]
  },
  {
    label: "车辆VIN号",
    prop: "vin_code",
    fieldProps: {
      placeholder: "请输入车辆VIN号",
      disabled: isDetail.value,
      maxlength: 17
    },
    formItemProps: {
      rules: [{ required: true, message: "请输入车辆VIN号", trigger: "blur" }]
    }
  },
  {
    label: "日期",
    prop: "monitor_date",
    valueType: "date-picker",
    fieldProps: {
      type: "date",
      valueFormat: "YYYY-MM-DD",
      placeholder: "请选择日期",
      disabled: isDetail.value
    }
  },
  {
    label: "上电时长（小时）",
    prop: "power_duration",
    valueType: "input-number",
    fieldProps: {
      placeholder: "请输入上电时长（小时）",
      disabled: isDetail.value,
      min: 0
    }
  },
  {
    label: "行驶里程（公里）",
    prop: "distance",
    valueType: "input-number",
    fieldProps: {
      placeholder: "请输入行驶里程（公里）",
      precision: 2,
      min: 0,
      disabled: isDetail.value
    }
  },
  {
    label: "使用率（%）",
    prop: "usage",
    valueType: "input-number",
    fieldProps: {
      precision: 2,
      min: 0,
      max: 100,
      placeholder: "请输入使用率（%）",
      disabled: isDetail.value
    }
  }
]);

const titleMap = {
  add: "新增车辆监控",
  edit: "编辑车辆监控",
  detail: "车辆监控详情"
};

const dialogTitle = computed(() => titleMap[currentMode.value]);

const open = (mode?: "add" | "edit" | "detail", data?: Record<string, any>) => {
  if (mode) {
    currentMode.value = mode;
  } else {
    currentMode.value = "add";
  }
  if (data && Object.keys(data).length > 0) {
    values.value = { ...(data || {}) };
  } else {
    values.value = {};
  }
  if (currentMode.value !== "detail") {
    fetchModels();
  }
  nextTick(() => {
    dialogKey.value++;
    visible.value = true;
  });
};

const handleSubmit = (vals: FieldValues) => {
  emit("save", vals);
  visible.value = false;
};

defineExpose({ open });
</script>

<template>
  <PlusDialogForm
    :key="dialogKey"
    v-model:visible="visible"
    v-model:values="values"
    :form="{
      columns: formColumns,
      labelPosition: 'right',
      labelWidth: '130px'
    }"
    :title="dialogTitle"
    :show-submit-btn="currentMode !== 'detail'"
    :show-cancel-btn="true"
    confirm-text="确定"
    cancel-text="取消"
    @confirm="handleSubmit"
    :has-footer="currentMode !== 'detail'"
  />
</template>

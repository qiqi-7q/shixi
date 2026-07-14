<script setup lang="ts">
import { ref, computed, nextTick } from "vue";
import "plus-pro-components/es/components/dialog-form/style/css";
import {
  type PlusColumn,
  type FieldValues,
  PlusDialogForm
} from "plus-pro-components";

const emit = defineEmits<{
  (e: "save", data: FieldValues): void;
}>();

const visible = ref(false);
const dialogKey = ref(0);
const values = ref<FieldValues>({});
const currentMode = ref<"add" | "edit" | "detail">("add");
const isDetail = computed(() => currentMode.value === "detail");

const formColumns = computed<PlusColumn[]>(() => [
  {
    label: "项目",
    prop: "project",
    fieldProps: {
      placeholder: "请输入项目名称",
      disabled: isDetail.value
    },
    formItemProps: {
      rules: [{ required: true, message: "请输入项目名称", trigger: "blur" }]
    }
  },
  {
    label: "测试版本",
    prop: "test_version",
    fieldProps: {
      placeholder: "请输入测试版本",
      disabled: isDetail.value
    }
  },
  {
    label: "测试开始时间",
    prop: "test_start_time",
    valueType: "date-picker",
    fieldProps: {
      type: "datetime",
      valueFormat: "YYYY-MM-DDTHH:mm:ss",
      placeholder: "请选择测试开始时间",
      disabled: isDetail.value
    },
    formItemProps: {
      rules: [
        { required: true, message: "请选择测试开始时间", trigger: "change" }
      ]
    }
  },
  {
    label: "测试结束时间",
    prop: "test_end_time",
    valueType: "date-picker",
    fieldProps: {
      type: "datetime",
      valueFormat: "YYYY-MM-DDTHH:mm:ss",
      placeholder: "请选择测试结束时间",
      disabled: isDetail.value
    },
    formItemProps: {
      rules: [
        { required: true, message: "请选择测试结束时间", trigger: "change" }
      ]
    }
  },
  {
    label: "测试车辆VIN",
    prop: "vin_code",
    fieldProps: {
      placeholder: "请输入VIN码",
      disabled: isDetail.value,
      maxlength: 17
    },
    formItemProps: {
      rules: [{ required: true, message: "请输入VIN码", trigger: "blur" }]
    }
  },
  {
    label: "测试功能",
    prop: "test_function",
    valueType: "select",
    options: [
      { label: "NAP", value: "NAP" },
      { label: "CNAP", value: "CNAP" },
      { label: "LCC/ACC", value: "LCC/ACC" }
    ],
    fieldProps: {
      placeholder: "请选择测试功能",
      disabled: isDetail.value
    },
    formItemProps: {
      rules: [{ required: true, message: "请选择测试功能", trigger: "change" }]
    }
  },
  {
    label: "功能测试里程(km)",
    prop: "mileage",
    valueType: "input-number",
    fieldProps: {
      placeholder: "请输入功能测试里程",
      disabled: isDetail.value,
      min: 0,
      precision: 0
    }
  },
  {
    label: "车辆行驶里程(km)",
    prop: "driving_mileage",
    valueType: "input-number",
    fieldProps: {
      placeholder: "请输入车辆行驶里程",
      disabled: isDetail.value,
      min: 0,
      precision: 0
    }
  },
  {
    label: "是否用于KPI统计",
    prop: "is_kpi",
    valueType: "select",
    options: [
      { label: "是", value: true },
      { label: "否", value: false }
    ],
    fieldProps: {
      placeholder: "请选择",
      disabled: isDetail.value
    }
  },
  {
    label: "备注",
    prop: "remarks",
    valueType: "textarea",
    fieldProps: {
      placeholder: "请输入备注",
      disabled: isDetail.value,
      maxlength: 200,
      showWordLimit: true,
      autosize: { minRows: 2, maxRows: 4 }
    }
  }
]);

const titleMap = {
  add: "新增测试记录",
  edit: "编辑测试记录",
  detail: "测试记录详情"
};

const dialogTitle = computed(() => titleMap[currentMode.value]);

const open = (mode: "add" | "edit" | "detail", data?: Record<string, any>) => {
  currentMode.value = mode;
  if (mode === "edit" || mode === "detail") {
    values.value = { ...(data || {}) };
  } else {
    values.value = {};
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
    v-model="values"
    :form="{
      columns: formColumns,
      labelPosition: 'right',
      labelWidth: '140px'
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

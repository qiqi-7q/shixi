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
    label: "姓名",
    prop: "name",
    fieldProps: {
      placeholder: "请输入姓名",
      disabled: isDetail.value
    },
    formItemProps: {
      rules: [{ required: true, message: "请输入姓名", trigger: "blur" }]
    }
  },
  {
    label: "模块名称",
    prop: "module_name",
    fieldProps: {
      placeholder: "请输入模块名称",
      disabled: isDetail.value
    }
  },
  {
    label: "模块负责人",
    prop: "module_manager",
    fieldProps: {
      placeholder: "请输入模块负责人",
      disabled: isDetail.value
    }
  },
  {
    label: "岗位类型",
    prop: "job_type",
    valueType: "select",
    options: [
      { label: "司机", value: "司机" },
      { label: "外协", value: "外协" }
    ],
    fieldProps: {
      placeholder: "请选择岗位类型",
      disabled: isDetail.value
    }
  },
  {
    label: "负责任务",
    prop: "task",
    fieldProps: {
      placeholder: "请输入负责任务",
      disabled: isDetail.value
    }
  },
  {
    label: "内照有效期",
    prop: "card_validity",
    valueType: "date-picker",
    fieldProps: {
      valueFormat: "YYYY-MM-DD",
      type: "date",
      placeholder: "请选择内照有效期",
      disabled: isDetail.value
    }
  }
]);

const titleMap = {
  add: "新增人员",
  edit: "编辑人员",
  detail: "人员详情"
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

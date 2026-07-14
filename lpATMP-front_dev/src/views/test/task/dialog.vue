<script setup lang="ts">
import { ref, computed, nextTick } from "vue";
import "plus-pro-components/es/components/dialog-form/style/css";
import {
  type PlusColumn,
  type FieldValues,
  PlusDialogForm
} from "plus-pro-components";
import { createTask, updateTask } from "@/api/system";
import { message } from "@/utils/message";

const emit = defineEmits<{
  (e: "save"): void;
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
    label: "测试时间",
    prop: "test_time",
    valueType: "date-picker",
    fieldProps: {
      type: "datetime",
      valueFormat: "YYYY-MM-DDTHH:mm:ss[Z]",
      placeholder: "请选择测试时间",
      disabled: isDetail.value
    },
    formItemProps: {
      rules: [{ required: true, message: "请选择测试时间", trigger: "change" }]
    }
  },
  {
    label: "测试车辆VIN",
    prop: "vin_code",
    fieldProps: {
      placeholder: "请输入测试车辆VIN",
      disabled: isDetail.value
    },
    formItemProps: {
      rules: [{ required: true, message: "请输入测试车辆VIN", trigger: "blur" }]
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
    }
  },
  {
    label: "任务描述",
    prop: "task_desc",
    valueType: "textarea",
    fieldProps: {
      placeholder: "请输入任务描述",
      disabled: isDetail.value,
      maxlength: 200,
      showWordLimit: true,
      autosize: { minRows: 2, maxRows: 4 }
    }
  },
  {
    label: "测试里程(km)",
    prop: "test_mileage",
    valueType: "input-number",
    fieldProps: {
      placeholder: "请输入测试里程",
      disabled: isDetail.value,
      min: 0,
      precision: 1
    }
  },
  {
    label: "任务发布人",
    prop: "task_publisher",
    fieldProps: {
      placeholder: "请输入任务发布人",
      disabled: isDetail.value
    }
  },
  {
    label: "测试人员",
    prop: "test_person",
    fieldProps: {
      placeholder: "请输入测试人员",
      disabled: isDetail.value
    }
  },
  {
    label: "实际完成里程(km)",
    prop: "actual_mileage",
    valueType: "input-number",
    fieldProps: {
      placeholder: "请输入实际完成里程",
      disabled: isDetail.value,
      min: 0,
      precision: 1
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
      placeholder: "请选择是否用于KPI统计",
      disabled: isDetail.value
    }
  },
  {
    label: "任务状态",
    prop: "task_status",
    valueType: "select",
    options: [
      { label: "完成", value: "完成" },
      { label: "进行中", value: "进行中" },
      { label: "未开始", value: "未开始" },
      { label: "未达标", value: "未达标" },
      { label: "挂起", value: "挂起" }
    ],
    fieldProps: {
      placeholder: "请选择任务状态",
      disabled: isDetail.value
    }
  },
  {
    label: "原因说明",
    prop: "reason_desc",
    valueType: "textarea",
    fieldProps: {
      placeholder: "请输入原因说明",
      disabled: isDetail.value,
      maxlength: 200,
      showWordLimit: true,
      autosize: { minRows: 2, maxRows: 4 }
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
  add: "新增任务",
  edit: "编辑任务",
  detail: "任务详情"
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

const handleSubmit = async (vals: FieldValues) => {
  try {
    let res: any;
    if (currentMode.value === "add") {
      res = await createTask(vals);
    } else if (currentMode.value === "edit") {
      const {
        id,
        created_at,
        updated_at,
        task_achievement_rate,
        ...updateData
      } = vals as any;
      res = await updateTask(id, updateData);
    }

    if (res.code === 200) {
      message(currentMode.value === "add" ? "新增成功" : "编辑成功", {
        type: "success"
      });
      emit("save");
      visible.value = false;
    } else {
      message(res.message || "操作失败", { type: "error" });
    }
  } catch (e) {
    message("操作失败", { type: "error" });
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

<script setup lang="ts">
import { ref, computed, nextTick } from "vue";
import "plus-pro-components/es/components/dialog-form/style/css";
import {
  type PlusColumn,
  type FieldValues,
  PlusDialogForm
} from "plus-pro-components";
import { createRoute, updateRoute } from "@/api/system";
import { message } from "@/utils/message";

const emit = defineEmits<{
  (e: "save", data: FieldValues): void;
}>();

const visible = ref(false);
const dialogKey = ref(0);
const values = ref<FieldValues>({});
const currentMode = ref<"add" | "edit" | "detail">("add");
const currentId = ref<number | null>(null);
const isDetail = computed(() => currentMode.value === "detail");

const formColumns = computed<PlusColumn[]>(() => [
  {
    label: "路线名称",
    prop: "routeName",
    fieldProps: {
      placeholder: "请输入路线名称",
      disabled: isDetail.value
    },
    formItemProps: {
      rules: [{ required: true, message: "请输入路线名称", trigger: "blur" }]
    }
  },
  {
    label: "创建人",
    prop: "creator",
    fieldProps: {
      placeholder: "请输入创建人",
      disabled: isDetail.value
    },
    formItemProps: {
      rules: [{ required: true, message: "请输入创建人", trigger: "blur" }]
    }
  },
  {
    label: "测试功能",
    prop: "testFunc",
    fieldProps: {
      placeholder: "请输入测试功能",
      disabled: isDetail.value
    },
    formItemProps: {
      rules: [{ required: true, message: "请输入测试功能", trigger: "blur" }]
    }
  },
  {
    label: "里程(km)",
    prop: "routeLength",
    valueType: "input-number",
    fieldProps: {
      placeholder: "请输入里程",
      disabled: isDetail.value,
      min: 0.1,
      precision: 1
    },
    formItemProps: {
      rules: [{ required: true, message: "请输入里程", trigger: "blur" }]
    }
  },
  {
    label: "难度系数",
    prop: "diff",
    valueType: "input-number",
    fieldProps: {
      placeholder: "请输入难度系数(0-100)",
      disabled: isDetail.value,
      min: 0,
      max: 100,
      precision: 0,
      step: 1
    },
    formItemProps: {
      rules: [{ required: true, message: "请输入难度系数", trigger: "blur" }]
    }
  },
  {
    label: "路线链接",
    prop: "routeLink",
    fieldProps: {
      placeholder: "请输入路线链接",
      disabled: isDetail.value
    }
  },
  {
    label: "城市",
    prop: "location",
    fieldProps: {
      placeholder: "请输入城市",
      disabled: isDetail.value
    }
  },
  {
    label: "路线特征",
    prop: "routeFeature",
    fieldProps: {
      placeholder: "请输入路线特征",
      disabled: isDetail.value
    }
  },
  {
    label: "路线描述",
    prop: "routeDesc",
    valueType: "textarea",
    fieldProps: {
      placeholder: "请输入路线描述",
      disabled: isDetail.value,
      maxlength: 500,
      showWordLimit: true,
      autosize: { minRows: 2, maxRows: 4 }
    }
  },
  {
    label: "备注",
    prop: "remark",
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
  add: "新增路线",
  edit: "编辑路线",
  detail: "路线详情"
};

const dialogTitle = computed(() => titleMap[currentMode.value]);

const open = (mode: "add" | "edit" | "detail", data?: Record<string, any>) => {
  currentMode.value = mode;
  if (mode === "edit" || mode === "detail") {
    currentId.value = data?.id || null;
    values.value = { ...(data || {}) };
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
  try {
    const apiData = {
      location: vals.location || null,
      route_name: vals.routeName,
      route_length: vals.routeLength,
      test_func: vals.testFunc,
      diff: vals.diff,
      creator: vals.creator,
      route_desc: vals.routeDesc || null,
      route_feature: vals.routeFeature || null,
      route_link: vals.routeLink || null,
      remark: vals.remark || null
    };

    if (currentMode.value === "add") {
      const res: any = await createRoute(apiData);
      if (res.code === 200) {
        message("创建成功", { type: "success" });
        emit("save", vals);
        visible.value = false;
      } else {
        message(res.message || "创建失败", { type: "error" });
      }
    } else if (currentMode.value === "edit" && currentId.value) {
      const res: any = await updateRoute(currentId.value, apiData);
      if (res.code === 200) {
        message("更新成功", { type: "success" });
        emit("save", vals);
        visible.value = false;
      } else {
        message(res.message || "更新失败", { type: "error" });
      }
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

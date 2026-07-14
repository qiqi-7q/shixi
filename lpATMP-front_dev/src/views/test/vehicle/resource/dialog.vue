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
const values = ref<FieldValues>({});
const dialogKey = ref(0);
const currentMode = ref<"add" | "edit" | "detail">("add");
const isDetail = computed(() => currentMode.value === "detail");

const formColumns = computed<PlusColumn[]>(() => [
  {
    label: "车型",
    prop: "model",
    fieldProps: {
      placeholder: "请输入车型",
      disabled: isDetail.value
    },
    formItemProps: {
      rules: [{ required: true, message: "请输入车型", trigger: "blur" }]
    }
  },
  {
    label: "组别",
    prop: "group",
    valueType: "select",
    options: [
      { label: "行车组", value: "行车组" },
      { label: "泊车组", value: "泊车组" },
      { label: "预警组", value: "预警组" }
    ],
    fieldProps: {
      placeholder: "请选择组别",
      disabled: isDetail.value
    },
    formItemProps: {
      rules: [{ required: true, message: "请选择组别", trigger: "change" }]
    }
  },
  {
    label: "车辆阶段",
    prop: "vehicle_stage",
    fieldProps: {
      placeholder: "请输入车辆阶段",
      disabled: isDetail.value
    }
  },
  {
    label: "车辆配置",
    prop: "configuration",
    fieldProps: {
      placeholder: "请选择车辆配置",
      disabled: isDetail.value
    }
  },
  {
    label: "车主权限",
    prop: "owner_name",
    fieldProps: {
      placeholder: "请输入车主权限",
      disabled: isDetail.value
    },
    formItemProps: {
      rules: [{ required: true, message: "请输入车主权限", trigger: "blur" }]
    }
  },
  {
    label: "车辆编号",
    prop: "vehicle_code",
    fieldProps: {
      placeholder: "请输入车辆编号",
      disabled: isDetail.value
    },
    formItemProps: {
      rules: [{ required: true, message: "请输入车辆编号", trigger: "blur" }]
    }
  },
  {
    label: "停车地点",
    prop: "parking_location",
    fieldProps: {
      placeholder: "请输入停车地点",
      disabled: isDetail.value
    }
  },
  {
    label: "使用状态",
    prop: "vehicle_status",
    valueType: "select",
    options:
      currentMode.value === "add"
        ? [{ label: "可借用", value: "可借用" }]
        : [
            { label: "维护中", value: "维护中" },
            { label: "已预定", value: "已预定" }
          ],
    fieldProps: {
      placeholder: "请选择使用状态",
      disabled: isDetail.value
    },
    formItemProps: {
      rules: [{ required: true, message: "请选择使用状态", trigger: "change" }]
    }
  },
  {
    label: "车辆状态",
    prop: "test_status",
    valueType: "select",
    options: [
      { label: "支持全部测试", value: "支持全部测试" },
      { label: "不支持泊车测试", value: "不支持泊车测试" },
      { label: "不支持行车测试", value: "不支持行车测试" },
      { label: "不支持后向预警测试", value: "不支持后向预警测试" },
      { label: "不支持全部测试", value: "不支持全部测试" },
      { label: "生产中", value: "生产中" },
      { label: "外借中", value: "外借中" }
    ],
    fieldProps: {
      placeholder: "请选择车辆状态",
      disabled: isDetail.value
    }
  },
  {
    label: "VIN 码",
    prop: "vin_code",
    fieldProps: {
      placeholder: "请输入 VIN 码",
      disabled: isDetail.value,
      maxlength: 17
    },
    formItemProps: {
      rules: [
        { required: true, message: "请输入 VIN 码", trigger: "blur" },
        {
          pattern: /^[A-Za-z0-9]+$/,
          message: "VIN 码只能包含字母和数字，不能包含文字",
          trigger: "blur"
        }
      ]
    }
  },
  {
    label: "车牌号",
    prop: "plate_number",
    fieldProps: {
      placeholder: "请输入车牌号",
      disabled: isDetail.value
    },
    formItemProps: {
      rules: [{ required: true, message: "请输入车牌号", trigger: "blur" }]
    }
  },
  {
    label: "驱动电机号/发动机号",
    prop: "engine_num",
    fieldProps: {
      placeholder: "请输入驱动电机号/发动机号",
      disabled: isDetail.value
    }
  },
  {
    label: "临牌到期时间",
    prop: "temp_plate_expire_date",
    valueType: "date-picker",
    fieldProps: {
      type: "date",
      valueFormat: "YYYY-MM-DD",
      placeholder: "请选择临牌到期时间",
      disabled: isDetail.value
    }
  },
  {
    label: "临牌已办理次数",
    prop: "temp_plate_count",
    valueType: "input-number",
    fieldProps: {
      placeholder: "请输入办理次数",
      disabled: isDetail.value,
      min: 0
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
  add: "新增车辆资源",
  edit: "编辑车辆资源",
  detail: "车辆资源详情"
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
      labelWidth: '160px'
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

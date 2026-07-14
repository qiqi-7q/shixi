<script setup lang="ts">
import { ref, computed, nextTick } from "vue";
import "plus-pro-components/es/components/dialog-form/style/css";
import {
  type PlusColumn,
  type FieldValues,
  PlusDialogForm
} from "plus-pro-components";
import { message } from "@/utils/message";
import { updateSuccessRate } from "@/api/system";

const emit = defineEmits<{
  (e: "save"): void;
}>();

const visible = ref(false);
const dialogKey = ref(0);
const values = ref<FieldValues>({});
const loading = ref(false);

const formColumns = computed(
  () =>
    [
      {
        label: "项目",
        prop: "project",
        fieldProps: {
          placeholder: "请输入项目",
          disabled: true,
          maxlength: 50
        }
      },
      {
        label: "车型",
        prop: "carModel",
        fieldProps: {
          placeholder: "请输入车型",
          disabled: true,
          maxlength: 50
        }
      },
      {
        label: "版本",
        prop: "version",
        fieldProps: {
          placeholder: "请输入版本",
          disabled: true,
          maxlength: 50
        }
      },
      {
        label: "功能模式",
        prop: "funcMode",
        fieldProps: {
          placeholder: "请输入功能模式",
          disabled: true,
          maxlength: 50
        }
      },
      {
        label: "变道成功率(%)",
        prop: "change_lane_success_rate",
        fieldProps: {
          type: "number",
          placeholder: "0-100",
          min: 0,
          max: 100,
          precision: 1,
          controls: false
        },
        formItemProps: {
          rules: [
            { required: true, message: "请输入变道成功率", trigger: "blur" },
            {
              validator: (_rule: any, value: any, callback: any) => {
                if (value === "" || value === undefined || value === null) {
                  callback();
                  return;
                }
                const num = Number(value);
                if (isNaN(num) || num < 0 || num > 100) {
                  callback(new Error("范围 0-100"));
                } else {
                  callback();
                }
              },
              trigger: "blur"
            }
          ]
        }
      },
      {
        label: "汇入成功率(%)",
        prop: "inflow_success_rate",
        fieldProps: {
          type: "number",
          placeholder: "0-100",
          min: 0,
          max: 100,
          precision: 1,
          controls: false
        },
        formItemProps: {
          rules: [
            { required: true, message: "请输入汇入成功率", trigger: "blur" },
            {
              validator: (_rule: any, value: any, callback: any) => {
                if (value === "" || value === undefined || value === null) {
                  callback();
                  return;
                }
                const num = Number(value);
                if (isNaN(num) || num < 0 || num > 100) {
                  callback(new Error("范围 0-100"));
                } else {
                  callback();
                }
              },
              trigger: "blur"
            }
          ]
        }
      },
      {
        label: "汇出成功率(%)",
        prop: "outflow_success_rate",
        fieldProps: {
          type: "number",
          placeholder: "0-100",
          min: 0,
          max: 100,
          precision: 1,
          controls: false
        },
        formItemProps: {
          rules: [
            { required: true, message: "请输入汇出成功率", trigger: "blur" },
            {
              validator: (_rule: any, value: any, callback: any) => {
                if (value === "" || value === undefined || value === null) {
                  callback();
                  return;
                }
                const num = Number(value);
                if (isNaN(num) || num < 0 || num > 100) {
                  callback(new Error("范围 0-100"));
                } else {
                  callback();
                }
              },
              trigger: "blur"
            }
          ]
        }
      },
      {
        label: "分合流成功率(%)",
        prop: "diverge_converge_rate",
        fieldProps: {
          type: "number",
          placeholder: "0-100",
          min: 0,
          max: 100,
          precision: 1,
          controls: false
        },
        formItemProps: {
          rules: [
            { required: true, message: "请输入分合流成功率", trigger: "blur" },
            {
              validator: (_rule: any, value: any, callback: any) => {
                if (value === "" || value === undefined || value === null) {
                  callback();
                  return;
                }
                const num = Number(value);
                if (isNaN(num) || num < 0 || num > 100) {
                  callback(new Error("范围 0-100"));
                } else {
                  callback();
                }
              },
              trigger: "blur"
            }
          ]
        }
      },
      {
        label: "特殊场景成功率(%)",
        prop: "special_rate",
        fieldProps: {
          type: "number",
          placeholder: "0-100",
          min: 0,
          max: 100,
          precision: 1,
          controls: false
        },
        formItemProps: {
          rules: [
            {
              required: true,
              message: "请输入特殊场景成功率",
              trigger: "blur"
            },
            {
              validator: (_rule: any, value: any, callback: any) => {
                if (value === "" || value === undefined || value === null) {
                  callback();
                  return;
                }
                const num = Number(value);
                if (isNaN(num) || num < 0 || num > 100) {
                  callback(new Error("范围 0-100"));
                } else {
                  callback();
                }
              },
              trigger: "blur"
            }
          ]
        }
      },
      {
        label: "限速识别成功率(%)",
        prop: "recog_rate",
        fieldProps: {
          type: "number",
          placeholder: "0-100",
          min: 0,
          max: 100,
          precision: 1,
          controls: false
        },
        formItemProps: {
          rules: [
            {
              required: true,
              message: "请输入限速识别成功率",
              trigger: "blur"
            },
            {
              validator: (_rule: any, value: any, callback: any) => {
                if (value === "" || value === undefined || value === null) {
                  callback();
                  return;
                }
                const num = Number(value);
                if (isNaN(num) || num < 0 || num > 100) {
                  callback(new Error("范围 0-100"));
                } else {
                  callback();
                }
              },
              trigger: "blur"
            }
          ]
        }
      }
    ] as PlusColumn[]
);

const open = (data: Record<string, any>) => {
  values.value = {
    project: data.project,
    carModel: data.carModel,
    version: data.version,
    funcMode: data.funcMode,
    change_lane_success_rate: undefined,
    inflow_success_rate: undefined,
    outflow_success_rate: undefined,
    diverge_converge_rate: undefined,
    special_rate: undefined,
    recog_rate: undefined
  };
  nextTick(() => {
    dialogKey.value++;
    visible.value = true;
  });
};

const handleSubmit = async (vals: FieldValues) => {
  loading.value = true;
  try {
    const res: any = await updateSuccessRate({
      project: vals.project,
      carModel: vals.carModel,
      version: vals.version,
      funcMode: vals.funcMode,
      change_lane_success_rate: vals.change_lane_success_rate,
      inflow_success_rate: vals.inflow_success_rate,
      outflow_success_rate: vals.outflow_success_rate,
      diverge_converge_rate: vals.diverge_converge_rate,
      special_rate: vals.special_rate,
      recog_rate: vals.recog_rate
    });

    if (res?.code === 200) {
      message("更新成功", { type: "success" });
      emit("save");
      visible.value = false;
    } else {
      message(res?.message || "更新失败", { type: "error" });
    }
  } catch (error) {
    message("更新失败", { type: "error" });
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
      labelWidth: '150px'
    }"
    title="更新成功率指标"
    :show-submit-btn="true"
    :show-cancel-btn="true"
    confirm-text="保存"
    cancel-text="取消"
    @confirm="handleSubmit"
  />
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from "vue";
import "plus-pro-components/es/components/dialog-form/style/css";
import {
  type PlusColumn,
  type FieldValues,
  PlusDialogForm
} from "plus-pro-components";
import { createDriverMonitor, updateDriverMonitor } from "@/api/system";
import { message } from "@/utils/message";

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

const formColumns = computed(
  () =>
    [
      {
        label: "测试日期",
        prop: "testDate",
        valueType: "date-picker",
        fieldProps: {
          type: "date",
          placeholder: "请选择测试日期",
          disabled: isDetail.value,
          valueFormat: "YYYY-MM-DD"
        },
        formItemProps: {
          rules: [
            { required: true, message: "请选择测试日期", trigger: "change" }
          ]
        }
      },
      {
        label: "测试开始时间",
        prop: "testStartTime",
        valueType: "time-picker",
        fieldProps: {
          placeholder: "请选择测试开始时间",
          disabled: isDetail.value,
          valueFormat: "HH:mm:ss"
        },
        formItemProps: {
          rules: [
            { required: true, message: "请选择测试开始时间", trigger: "change" }
          ]
        }
      },
      {
        label: "测试结束时间",
        prop: "testEndTime",
        valueType: "time-picker",
        fieldProps: {
          placeholder: "请选择测试结束时间",
          disabled: isDetail.value,
          valueFormat: "HH:mm:ss"
        },
        formItemProps: {
          rules: [
            {
              required: true,
              message: "请选择测试结束时间",
              trigger: "change"
            },
            {
              validator: (rule, value, callback) => {
                if (value && values.value.testStartTime) {
                  if (value < values.value.testStartTime) {
                    callback(new Error("结束时间不能小于开始时间"));
                  } else {
                    callback();
                  }
                } else {
                  callback();
                }
              },
              trigger: "change"
            }
          ]
        }
      },
      {
        label: "测试车辆VIN",
        prop: "vinCode",
        fieldProps: {
          placeholder: "请输入测试车辆VIN号",
          disabled: isDetail.value,
          maxlength: 17
        },
        formItemProps: {
          rules: [
            { required: true, message: "请输入测试车辆VIN号", trigger: "blur" },
            {
              pattern: /^[A-Za-z0-9]+$/,
              message: "VIN 码只能包含字母和数字，不能包含文字",
              trigger: "blur"
            }
          ]
        }
      },
      {
        label: "司机姓名",
        prop: "driverName",
        fieldProps: {
          placeholder: "请输入司机姓名",
          disabled: isDetail.value,
          maxlength: 50
        },
        formItemProps: {
          rules: [
            { required: true, message: "请输入司机姓名", trigger: "blur" }
          ]
        }
      },
      {
        label: "司机状态",
        prop: "driverStatus",
        valueType: "select",
        options: [
          { label: "正常", value: "正常" },
          { label: "轻微疲劳", value: "轻微疲劳" },
          { label: "疲劳", value: "疲劳" },
          { label: "严重疲劳", value: "严重疲劳" }
        ],
        fieldProps: {
          placeholder: "请选择司机状态",
          disabled: isDetail.value
        },
        formItemProps: {
          rules: [
            { required: true, message: "请选择司机状态", trigger: "change" }
          ]
        }
      },
      {
        label: "DMS触发次数",
        prop: "dmsTriggerCount",
        valueType: "input-number",
        fieldProps: {
          placeholder: "请输入DMS触发次数",
          disabled: isDetail.value,
          min: 0,
          precision: 0
        },
        formItemProps: {
          rules: [
            { required: true, message: "请输入DMS触发次数", trigger: "blur" }
          ]
        }
      },
      {
        label: "行驶里程(km)",
        prop: "distance",
        valueType: "input-number",
        fieldProps: {
          placeholder: "请输入行驶里程",
          disabled: isDetail.value,
          min: 0,
          precision: 2
        },
        formItemProps: {
          rules: [
            { required: true, message: "请输入行驶里程", trigger: "blur" }
          ]
        }
      },
      {
        label: "车辆上电开始时间",
        prop: "powerStartDuration",
        valueType: "date-picker",
        fieldProps: {
          type: "datetime",
          placeholder: "请选择车辆上电开始时间",
          disabled: isDetail.value,
          valueFormat: "YYYY-MM-DDTHH:mm:ss"
        },
        formItemProps: {
          rules: [
            {
              required: true,
              message: "请选择车辆上电开始时间",
              trigger: "change"
            }
          ]
        }
      },
      {
        label: "车辆上电结束时间",
        prop: "powerEndDuration",
        valueType: "date-picker",
        fieldProps: {
          type: "datetime",
          placeholder: "请选择车辆上电结束时间",
          disabled: isDetail.value,
          valueFormat: "YYYY-MM-DDTHH:mm:ss"
        },
        formItemProps: {
          rules: [
            {
              required: true,
              message: "请选择车辆上电结束时间",
              trigger: "change"
            }
          ]
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
    ] as PlusColumn[]
);

const titleMap = {
  add: "新增司机监控记录",
  edit: "编辑司机监控记录",
  detail: "司机监控详情"
};

const dialogTitle = computed(() => titleMap[currentMode.value]);

const open = (mode: "add" | "edit" | "detail", data?: Record<string, any>) => {
  currentMode.value = mode;
  if (mode === "edit" || mode === "detail") {
    currentId.value = data?.id || null;
    let testStartTime = data?.test_start_time;
    let testEndTime = data?.test_end_time;

    if (testStartTime && testStartTime.includes("T")) {
      testStartTime = testStartTime.split("T")[1];
    }
    if (testEndTime && testEndTime.includes("T")) {
      testEndTime = testEndTime.split("T")[1];
    }

    values.value = {
      testDate: data?.test_date,
      testStartTime: testStartTime,
      testEndTime: testEndTime,
      vinCode: data?.vin_code,
      driverName: data?.driver_name,
      driverStatus: data?.driver_status,
      dmsTriggerCount: data?.dms_trigger_count,
      distance: data?.distance,
      powerStartDuration: data?.power_start_duration,
      powerEndDuration: data?.power_end_duration,
      remark: data?.remark
    };
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
    const testStartTime = vals.testStartTime
      ? `${vals.testDate}T${vals.testStartTime}`
      : null;
    const testEndTime = vals.testEndTime
      ? `${vals.testDate}T${vals.testEndTime}`
      : null;

    const submitData = {
      test_date: vals.testDate,
      test_start_time: testStartTime,
      test_end_time: testEndTime,
      vin_code: vals.vinCode,
      driver_name: vals.driverName,
      driver_status: vals.driverStatus,
      dms_trigger_count: vals.dmsTriggerCount,
      distance: vals.distance,
      power_start_duration: vals.powerStartDuration,
      power_end_duration: vals.powerEndDuration,
      remark: vals.remark
    };

    if (currentMode.value === "add") {
      const res = (await createDriverMonitor(submitData)) as any;
      if (res.code === 200) {
        message("创建成功", { type: "success" });
        emit("save", vals);
        visible.value = false;
      } else {
        message(res.message || "创建失败", { type: "error" });
      }
    } else if (currentMode.value === "edit" && currentId.value) {
      const res = (await updateDriverMonitor(
        currentId.value,
        submitData
      )) as any;
      if (res.code === 200) {
        message("更新成功", { type: "success" });
        emit("save", vals);
        visible.value = false;
      } else {
        message(res.message || "更新失败", { type: "error" });
      }
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

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
  createTestRecord,
  getTestRecordDetail,
  updateTestRecord,
  uploadTestRecordAttach,
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

const functionModeOptions = [
  { label: "NAP", value: "NAP" },
  { label: "CNAP", value: "CNAP" },
  { label: "ACC/LCC", value: "ACC/LCC" }
];

const problemCategoryOptions = [
  { label: "可靠性", value: "可靠性" },
  { label: "法规/安全性", value: "法规/安全性" },
  { label: "舒适性", value: "舒适性" },
  { label: "可用性", value: "可用性" }
];

const kpiTypeOptions = [
  { label: "异常退出", value: "异常退出" },
  { label: "异常降级", value: "异常降级" },
  { label: "无法激活", value: "无法激活" },
  { label: "系统异常", value: "系统异常" },
  { label: "碰撞风险", value: "碰撞风险" },
  { label: "压实线", value: "压实线" },
  {
    label: "匝道红绿灯严重失效（导致闯红灯）",
    value: "匝道红绿灯严重失效（导致闯红灯）"
  },
  {
    label: "匝道红绿灯一般失效（错误减速/加速）",
    value: "匝道红绿灯一般失效（错误减速/加速）"
  },
  { label: "超速/低速", value: "超速/低速" },
  { label: "横向", value: "横向" },
  { label: "纵向", value: "纵向" },
  { label: "变道成功", value: "变道成功" },
  { label: "变道失败", value: "变道失败" },
  {
    label: "无效变道（如无必要的反复变道）",
    value: "无效变道（如无必要的反复变道）"
  },
  { label: "汇入成功", value: "汇入成功" },
  { label: "汇入失败", value: "汇入失败" },
  { label: "汇出成功", value: "汇出成功" },
  { label: "汇出失败", value: "汇出失败" },
  { label: "分合流成功", value: "分合流成功" },
  { label: "分合流失败", value: "分合流失败" },
  { label: "特殊场景通过成功", value: "特殊场景通过成功" },
  { label: "特殊场景通过失败", value: "特殊场景通过失败" },
  { label: "脱手监测", value: "脱手监测" },
  { label: "限速识别成功", value: "限速识别成功" },
  { label: "限速识别失败", value: "限速识别失败" },
  { label: "人机共驾接管冲突", value: "人机共驾接管冲突" },
  {
    label: "人机共驾车辆失控风险",
    value: "人机共驾车辆失控风险"
  },
  {
    label: "微避障失败（未避让非机动车/行人/静止障碍物）",
    value: "微避障失败（未避让非机动车/行人/静止障碍物）"
  },
  {
    label: "微避障急刹/猛打方向",
    value: "微避障急刹/猛打方向"
  },
  {
    label: "微避障后无回正、压线",
    value: "微避障后无回正、压线"
  }
];

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
        }
      },
      {
        label: "车型",
        prop: "car_type",
        valueType: "select",
        fieldProps: {
          placeholder: "请选择车型",
          disabled: isDetail.value,
          filterable: true,
          options: carTypeOptions.value.map(c => ({ label: c, value: c }))
        }
      },
      {
        label: "功能模式",
        prop: "function_mode",
        valueType: "select",
        fieldProps: {
          placeholder: "请选择功能模式",
          disabled: isDetail.value,
          options: functionModeOptions
        }
      },
      {
        label: "问题描述",
        prop: "problem_desc",
        valueType: "textarea",
        fieldProps: {
          placeholder: "请输入问题描述",
          disabled: isDetail.value,
          rows: 3,
          maxlength: 500
        }
      },
      {
        label: "评价维度",
        prop: "problem_category",
        valueType: "select",
        fieldProps: {
          placeholder: "请选择评价维度",
          disabled: isDetail.value,
          options: problemCategoryOptions
        }
      },
      {
        label: "KPI项",
        prop: "kpi_type",
        valueType: "select",
        fieldProps: {
          placeholder: "请选择KPI项",
          disabled: isDetail.value,
          options: kpiTypeOptions
        }
      },
      {
        label: "问题场景",
        prop: "problem_scene",
        fieldProps: {
          placeholder: "请输入问题场景",
          disabled: isDetail.value,
          maxlength: 100
        }
      },
      {
        label: "问题分类",
        prop: "problem_type",
        fieldProps: {
          placeholder: "请输入问题分类",
          disabled: isDetail.value,
          maxlength: 100
        }
      },
      {
        label: "问题现象",
        prop: "problem_phenomenon",
        valueType: "textarea",
        autoHeight: true,
        fieldProps: {
          autoHeight: true,
          placeholder: "请输入问题现象",
          disabled: isDetail.value,
          rows: 3,
          maxlength: 500
        }
      },
      {
        label: "接管类型",
        prop: "takeover_type",
        fieldProps: {
          placeholder: "请输入接管类型",
          disabled: isDetail.value,
          maxlength: 100
        }
      },
      {
        label: "问题时间",
        prop: "problem_time",
        valueType: "date-picker",
        fieldProps: {
          valueFormat: "YYYY-MM-DDTHH:mm:ss[Z]",
          type: "datetime",
          placeholder: "请选择问题时间",
          disabled: isDetail.value
        }
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
          rules: [
            {
              pattern: /^[A-Za-z0-9]+$/,
              message: "VIN 码只能包含字母和数字，不能包含文字",
              trigger: "blur"
            }
          ]
        }
      },
      {
        label: "数据链接",
        prop: "data_link",
        fieldProps: {
          placeholder: "请输入数据链接",
          disabled: isDetail.value,
          maxlength: 500
        }
      },
      {
        label: "Wetrack链接",
        prop: "wetrack_link",
        fieldProps: {
          placeholder: "请输入Wetrack链接",
          disabled: isDetail.value,
          maxlength: 500
        }
      },
      {
        label: "分析结果",
        prop: "analyze_result",
        valueType: "textarea",
        fieldProps: {
          placeholder: "请输入分析结果",
          disabled: isDetail.value,
          rows: 3,
          maxlength: 500
        }
      },
      {
        label: "分析人员",
        prop: "analyze_user",
        fieldProps: {
          placeholder: "请输入分析人员",
          disabled: isDetail.value,
          maxlength: 50
        }
      },
      {
        label: "分析附件",
        prop: "analyze_attach",
        fieldProps: {
          placeholder: "请输入分析附件",
          disabled: isDetail.value,
          maxlength: 50
        }
      },
      {
        label: "软件版本",
        prop: "software_version",
        valueType: "select",
        fieldProps: {
          placeholder: "请选择软件版本",
          disabled: isDetail.value,
          filterable: true,
          options: softwareVersionOptions.value.map(s => ({
            label: s,
            value: s
          }))
        }
      },
      {
        label: "备注",
        prop: "remarks",
        valueType: "textarea",
        fieldProps: {
          placeholder: "请输入备注",
          disabled: isDetail.value,
          rows: 3,
          maxlength: 500
        }
      }
    ] as PlusColumn[]
);

const titleMap = {
  add: "新增测试记录",
  edit: "编辑测试记录",
  detail: "测试记录详情"
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
        const res: any = await getTestRecordDetail(data.id);
        if (res?.code === 200 && res.data) {
          const detail = res.data;
          values.value = {
            project: detail.project,
            car_type: detail.car_type,
            function_mode: detail.function_mode,
            problem_desc: detail.problem_desc,
            problem_category: detail.problem_category,
            kpi_type: detail.kpi_type,
            problem_scene: detail.problem_scene,
            problem_type: detail.problem_type,
            problem_phenomenon: detail.problem_phenomenon,
            takeover_type: detail.takeover_type,
            problem_time: detail.problem_time,
            vin_code: detail.vin_code,
            data_link: detail.data_link,
            wetrack_link: detail.wetrack_link,
            analyze_result: detail.analyze_result,
            analyze_user: detail.analyze_user,
            analyze_attach: detail.analyze_attach,
            software_version: detail.software_version,
            remarks: detail.remarks
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
      const res: any = await createTestRecord(vals);
      if (res?.code === 200) {
        message("创建成功", { type: "success" });
        emit("save", vals);
        visible.value = false;
      } else {
        message(res?.message || "创建失败", { type: "error" });
      }
    } else if (currentMode.value === "edit") {
      const res: any = await updateTestRecord(currentId.value, vals);
      if (res?.code === 200) {
        message("更新成功", { type: "success" });
        emit("save", vals);
        visible.value = false;
      } else {
        message(res?.message || "更新失败", { type: "error" });
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

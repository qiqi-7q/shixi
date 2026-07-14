<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from "vue";
import "plus-pro-components/es/components/dialog-form/style/css";
import {
  type PlusColumn,
  type FieldValues,
  PlusDialogForm
} from "plus-pro-components";
import { message } from "@/utils/message";
import { getAvailableDrivers } from "@/api/system";

const emit = defineEmits<{
  (e: "save", data: FieldValues): void;
}>();

const visible = ref(false);
const dialogKey = ref(0);
const values = ref<FieldValues>({});
const currentMode = ref<"add" | "edit" | "detail">("add");
const isDetail = computed(() => currentMode.value === "detail");
const borrowedRecords = ref<any[]>([]);
const showBorrowedAlert = ref(false);
const driverOptions = ref<{ label: string; value: string; id: number }[]>([]);

async function fetchDrivers() {
  try {
    const res: any = await getAvailableDrivers();
    if (res?.code === 200 && Array.isArray(res.data)) {
      driverOptions.value = res.data.map((d: any) => ({
        label: d.name + "（内照有效期至" + d.card_validity + "）",
        value: d.name,
        id: d.id
      }));
    }
  } catch (e) {}
}

const borrowedTipText = computed(() => {
  if (!showBorrowedAlert.value || borrowedRecords.value.length === 0) return "";
  return borrowedRecords.value
    .map(r => `${r.borrower} - ${r.borrow_time}`)
    .join("；");
});

// 已借用的日期集合（用于置灰）
const borrowedDates = ref<Set<string>>(new Set());

// 格式化日期为 YYYY-MM-DD
const formatDate = (date: Date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};

// 禁用日期：只允许选择今天和明天，且已借用的日期置灰
const disabledDate = (time: Date) => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const dayAfterTomorrow = new Date(today);
  dayAfterTomorrow.setDate(dayAfterTomorrow.getDate() + 2);

  // 超出今天和明天的范围禁用
  if (
    time.getTime() < today.getTime() ||
    time.getTime() >= dayAfterTomorrow.getTime()
  ) {
    return true;
  }

  // 已借用的日期置灰
  const dateStr = formatDate(time);
  return borrowedDates.value.has(dateStr);
};

const formColumns = computed<PlusColumn[]>(() => {
  const cols: PlusColumn[] = [
    {
      label: "车型",
      prop: "model",
      fieldProps: {
        placeholder: "请输入车型",
        disabled: true
      },
      formItemProps: {
        rules: [{ required: true, message: "请输入车型", trigger: "blur" }]
      }
    },
    {
      label: "VIN码",
      prop: "vin_code",
      fieldProps: {
        placeholder: "请输入VIN码",
        disabled: true,
        maxlength: 17
      },
      formItemProps: {
        rules: [
          { required: true, message: "请输入VIN码", trigger: "blur" },
          {
            pattern: /^[A-Za-z0-9]+$/,
            message: "VIN 码只能包含字母和数字，不能包含文字",
            trigger: "blur"
          }
        ]
      }
    },
    {
      label: "借用人",
      prop: "borrower",
      fieldProps: {
        placeholder: "请输入借用人",
        disabled: isDetail.value
      },
      formItemProps: {
        rules: [{ required: true, message: "请输入借用人", trigger: "blur" }]
      }
    }
  ];

  // 有借用冲突时才插入提示字段
  if (showBorrowedAlert.value && borrowedRecords.value.length > 0) {
    cols.push({
      valueType: "textarea",
      label: "借用提示",
      prop: "borrowed_tip",
      fieldProps: {
        disabled: true,
        readonly: true,
        showWordLimit: true,
        autosize: { minRows: 1, maxRows: 4 },
        class: "text-orange-500 font-medium"
      }
    });
  }

  cols.push(
    {
      label: "借用时间",
      prop: "borrow_time",
      valueType: "date-picker",
      fieldProps: {
        type: "date",
        valueFormat: "YYYY-MM-DD",
        placeholder: "请选择借用时间（只能选择今天和明天）",
        disabled: isDetail.value,
        disabledDate: disabledDate
      },
      formItemProps: {
        rules: [
          { required: true, message: "请选择借用时间", trigger: "change" }
        ]
      }
    },
    {
      label: "司机姓名",
      prop: "driver_name",
      valueType: "select",
      options: driverOptions.value,
      fieldProps: {
        placeholder: "请选择司机（内照有效期内）",
        disabled: isDetail.value,
        clearable: true
      }
    },
    // {
    //   label: "记录创建人",
    //   prop: "record_creator",
    //   fieldProps: {
    //     placeholder: "请输入创建人",
    //     disabled: isDetail.value
    //   }
    // },
    {
      label: "备注",
      prop: "remarks",
      valueType: "textarea",
      fieldProps: {
        placeholder: "请输入备注",
        maxlength: 200,
        showWordLimit: true,
        autosize: { minRows: 2, maxRows: 4 }
      }
    }
  );

  return cols;
});

const titleMap = {
  add: "新增借用记录",
  edit: "编辑借用记录",
  detail: "借用记录详情"
};

const dialogTitle = computed(() => titleMap[currentMode.value]);

const open = (mode: "add" | "edit" | "detail", data?: Record<string, any>) => {
  currentMode.value = mode;
  // 清空已借用日期
  borrowedDates.value.clear();

  if (mode === "edit" || mode === "detail") {
    values.value = { ...(data || {}) };
    borrowedRecords.value = [];
    showBorrowedAlert.value = false;
  } else if (data && Object.keys(data).length > 0) {
    // 收集已借用的日期（今天及之后的借用记录）
    const dataBorrowedRecords = data.borrowedRecords || [];
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    dataBorrowedRecords.forEach((r: any) => {
      const borrowDate = new Date(r.borrow_time);
      borrowDate.setHours(0, 0, 0, 0);
      // 只收集今天及之后的借用日期
      if (borrowDate.getTime() >= today.getTime()) {
        const dateStr = r.borrow_time;
        borrowedDates.value.add(dateStr);
      }
    });

    values.value = { ...(data || {}) };
    borrowedRecords.value = dataBorrowedRecords;
    showBorrowedAlert.value = borrowedRecords.value.length > 0;
    values.value.borrowed_tip = borrowedTipText.value;
  } else {
    values.value = {};
    borrowedRecords.value = [];
    showBorrowedAlert.value = false;
  }
  if (mode !== "detail") {
    fetchDrivers();
  }
  nextTick(() => {
    dialogKey.value++;
    visible.value = true;
  });
};

const handleSubmit = (vals: FieldValues) => {
  const submitData = { ...vals };
  if (vals.driver_name) {
    const selected = driverOptions.value.find(
      d => d.value === vals.driver_name
    );
    if (selected) {
      submitData.driver_id = selected.id;
    }
  } else {
    delete submitData.driver_name;
    delete submitData.driver_id;
  }
  emit("save", submitData);
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
    confirm-text="确定"
    cancel-text="取消"
    @confirm="handleSubmit"
    :has-footer="currentMode !== 'detail'"
  />
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import type { FilterItem, SelectOption } from "../type";
import {
  defaultOperatorOptions,
  dateRangeOperatorOptions,
  numericOperatorOptions
} from "../type";

import Delete from "~icons/ep/delete";
import CirclePlus from "~icons/ep/circle-plus";
import Filter from "~icons/ep/filter";
import Close from "~icons/ep/close";

defineOptions({
  name: "ReAdvancedSearch"
});

const props = withDefaults(
  defineProps<{
    modelValue?: FilterItem[];
    fieldOptions?: SelectOption[];
    operatorOptions?: SelectOption[];
    title?: string;
    triggerText?: string;
    popoverWidth?: number;
  }>(),
  {
    modelValue: () => [],
    fieldOptions: () => [],
    operatorOptions: () => defaultOperatorOptions,
    title: "筛选",
    triggerText: "高级搜索",
    popoverWidth: 650
  }
);

const emit = defineEmits<{
  (e: "update:modelValue", value: FilterItem[]): void;
  (e: "search"): void;
  (e: "reset"): void;
}>();

const popoverVisible = ref(false);

const filters = computed({
  get: () => props.modelValue,
  set: (val: FilterItem[]) => emit("update:modelValue", val)
});

// 监听 popover 打开时自动添加一行
watch(popoverVisible, val => {
  if (val && filters.value.length === 0) {
    addFilter();
  }
});

// 根据字段值获取字段配置（包含 type）
const getFieldOption = (field: string): SelectOption | undefined =>
  props.fieldOptions.find(opt => opt.value === field);

// 判断字段 label 是否包含"时间"或"日期"
const isTimeField = (field: string): boolean => {
  const option = getFieldOption(field);
  if (option?.type === "date" || option?.type === "daterange") return true;
  const label = option?.label || "";
  return label.includes("时间") || label.includes("日期");
};

// 判断字段是否为数值型（上电时长/行驶里程等）
const isNumericField = (field: string): boolean => {
  const label = getFieldOption(field)?.label || "";
  return (
    label.includes("上电时长") ||
    label.includes("行驶里程") ||
    label.includes("使用率") ||
    label.includes("智驾里程") ||
    label.includes("最高车速") ||
    label.includes("剩余电量") ||
    label.includes("充电次数")
  );
};

// 根据字段返回当前操作符选项
const getOperatorOptions = (field: string): SelectOption[] =>
  isTimeField(field)
    ? dateRangeOperatorOptions
    : isNumericField(field)
      ? numericOperatorOptions
      : defaultOperatorOptions;

// 字段切换时重置操作符和值
const handleFieldChange = (field: string) => {
  const idx = filters.value.findIndex(f => f.field === field);
  if (idx === -1) return;
  const filter = filters.value[idx];
  if (isTimeField(field)) {
    filter.operator = "between";
    filter.value = null;
  } else if (isNumericField(field)) {
    filter.operator = "eq";
    filter.value = "";
  } else {
    filter.operator = "icontains";
    filter.value = "";
  }
  emit("update:modelValue", [...filters.value]);
};

const addFilter = () => {
  emit("update:modelValue", [
    ...filters.value,
    { field: "", operator: "icontains", value: "" }
  ]);
};

const removeFilter = (index: number) => {
  emit(
    "update:modelValue",
    filters.value.filter((_, i) => i !== index)
  );
};

const handleSearch = () => {
  emit("search");
};

const handleReset = () => {
  emit("update:modelValue", [{ field: "", operator: "icontains", value: "" }]);
  emit("reset");
};

const clearFilters = () => {
  emit("update:modelValue", []);
};

defineExpose({
  reset: handleReset,
  clearFilters
});
</script>

<template>
  <div class="re-advanced-search">
    <el-popover
      v-model:visible="popoverVisible"
      placement="bottom-start"
      :width="popoverWidth"
      trigger="click"
    >
      <template #reference>
        <el-button type="primary" link>
          <el-icon class="mr-1"><Filter /></el-icon>
          {{ triggerText }}
          <span
            v-if="filters.length > 0"
            class="ml-1 inline-flex items-center justify-center w-4 h-4 text-xs bg-[var(--el-color-primary)] text-white rounded-full"
          >
            {{ filters.length }}
          </span>
        </el-button>
      </template>

      <!-- 筛选面板 -->
      <div class="re-advanced-search__panel">
        <div class="flex items-center justify-between mb-3">
          <div class="text-sm font-medium text-[var(--el-text-color-regular)]">
            {{ title }}
          </div>
          <el-button
            :icon="Close"
            circle
            size="small"
            @click="popoverVisible = false"
          />
        </div>

        <div
          v-for="(filter, index) in filters"
          :key="index"
          class="flex items-center gap-2 mb-2"
        >
          <el-select
            v-model="filter.field"
            placeholder="选择字段"
            class="w-40!"
            clearable
            :teleported="false"
            @update:model-value="handleFieldChange(filter.field)"
          >
            <el-option
              v-for="option in fieldOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>

          <el-select
            v-model="filter.operator"
            placeholder="条件"
            class="w-30!"
            :teleported="false"
            @update:model-value="emit('update:modelValue', [...filters])"
          >
            <el-option
              v-for="option in filter.field
                ? getOperatorOptions(filter.field)
                : operatorOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>

          <!-- 时间字段：显示 el-date-picker(daterange) -->
          <el-date-picker
            v-if="filter.field && isTimeField(filter.field)"
            v-model="filter.value"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            :teleported="false"
            class="flex-1!"
            @update:model-value="emit('update:modelValue', [...filters])"
          />
          <!-- 普通文本/数值字段：显示 el-input -->
          <el-input
            v-else
            :model-value="typeof filter.value === 'string' ? filter.value : ''"
            placeholder="输入内容"
            class="flex-1!"
            clearable
            @update:model-value="
              val => {
                filter.value = val;
                emit('update:modelValue', [...filters]);
              }
            "
          />

          <el-button
            type="danger"
            :icon="Delete"
            circle
            size="small"
            @click="removeFilter(index)"
          />
        </div>

        <div
          class="flex items-center justify-between mt-3 pt-2 border-t border-[var(--el-border-color-lighter)]"
        >
          <el-button type="primary" link @click="addFilter">
            <template #icon>
              <CirclePlus class="w-4 h-4" />
            </template>
            添加筛选条件
          </el-button>
          <div class="flex gap-2">
            <el-button size="small" type="primary" @click="handleSearch"
              >搜索</el-button
            >
            <el-button size="small" @click="handleReset">重置</el-button>
          </div>
        </div>
      </div>
    </el-popover>
  </div>
</template>

<style scoped>
.re-advanced-search {
  display: inline-block;
}

.re-advanced-search__panel {
  padding: 4px 0;
  overflow: visible;
}

:deep(.el-select) {
  overflow: visible;
}

:deep(.el-select .el-select-dropdown) {
  position: absolute !important;
  z-index: 3000 !important;
  background-color: var(--el-bg-color-overlay, #fff) !important;
  border: 1px solid var(--el-border-color-light) !important;
  border-radius: 4px;
  box-shadow: var(--el-box-shadow-light) !important;
}
</style>

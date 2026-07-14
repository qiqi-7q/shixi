/** 筛选条件项 */
export interface FilterItem {
  /** 字段名 */
  field: string;
  /** 操作符 */
  operator: string;
  /** 搜索值 */
  value: string | [string, string] | null;
}

/** 字段类型 */
export type FieldType = "text" | "date" | "daterange";

/** 字段/操作符选项 */
export interface SelectOption {
  label: string;
  value: string;
  /** 字段类型：用于切换操作符与值输入组件，不传默认为 text */
  type?: FieldType;
}

/** 高级搜索组件 Props */
export interface AdvancedSearchProps {
  /** 筛选条件列表（v-model） */
  modelValue?: FilterItem[];
  /** 可筛选字段选项 */
  fieldOptions?: SelectOption[];
  /** 操作符选项 */
  operatorOptions?: SelectOption[];
  /** 筛选区域标题 */
  title?: string;
  /** 触发文字 */
  triggerText?: string;
}

/** 默认（文本）操作符选项 */
export const defaultOperatorOptions: SelectOption[] = [
  { label: "包含", value: "icontains" },
  { label: "等于", value: "eq" },
  { label: "不等于", value: "not_eq" },
  { label: "开头是", value: "startswith" },
  { label: "结尾是", value: "endswith" }
];

/** 日期范围操作符选项 */
export const dateRangeOperatorOptions: SelectOption[] = [
  { label: "在...范围之内", value: "between" },
  { label: "不在...范围之内", value: "not_between" }
];

/** 数值比较操作符选项 */
export const numericOperatorOptions: SelectOption[] = [
  { label: "等于 ", value: "eq" },
  { label: "不等于 ", value: "not_eq" },
  { label: "小于 ", value: "lt" },
  { label: "小于等于 ", value: "lte" },
  { label: "大于 ", value: "gt" },
  { label: "大于等于 ", value: "gte" }
];

/** 根据字段类型返回对应的操作符选项 */
export const getOperatorOptionsByFieldType = (
  fieldType?: FieldType
): SelectOption[] => {
  if (fieldType === "date" || fieldType === "daterange") {
    return dateRangeOperatorOptions;
  }
  return defaultOperatorOptions;
};

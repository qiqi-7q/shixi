import { defineStore } from "pinia";
import { store, storageLocal, responsiveStorageNameSpace } from "../utils";

interface TableColumnConfig {
  order: string[]; // 列顺序（label 数组）
  hidden: string[]; // 隐藏的列（label 数组）
}

interface TableColumnsState {
  [tableKey: string]: TableColumnConfig;
}

export const useTableColumnStore = defineStore("pure-tableColumn", {
  state: (): TableColumnsState => {
    const saved = storageLocal().getItem<TableColumnsState>(
      `${responsiveStorageNameSpace()}table-columns`
    );
    return saved || {};
  },
  actions: {
    /** 保存表格列配置 */
    saveColumnConfig(tableKey: string, config: TableColumnConfig) {
      this.$state[tableKey] = config;
      storageLocal().setItem(
        `${responsiveStorageNameSpace()}table-columns`,
        this.$state
      );
    },
    /** 获取表格列配置 */
    getColumnConfig(tableKey: string): TableColumnConfig | undefined {
      return this.$state[tableKey];
    },
    /** 清除指定表格的列配置 */
    clearColumnConfig(tableKey: string) {
      delete this.$state[tableKey];
      storageLocal().setItem(
        `${responsiveStorageNameSpace()}table-columns`,
        this.$state
      );
    },
    /** 清除所有表格的列配置 */
    clearAllColumnConfig() {
      this.$state = {};
      storageLocal().setItem(
        `${responsiveStorageNameSpace()}table-columns`,
        this.$state
      );
    }
  }
});

export function useTableColumnStoreHook() {
  return useTableColumnStore(store);
}

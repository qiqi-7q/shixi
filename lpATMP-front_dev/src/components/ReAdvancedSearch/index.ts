import reAdvancedSearch from "./src/index.vue";
import { withInstall } from "@pureadmin/utils";

/** 高级搜索组件 */
export const ReAdvancedSearch = withInstall(reAdvancedSearch);

export default ReAdvancedSearch;
export type {
  FilterItem,
  SelectOption,
  AdvancedSearchProps
} from "./type";
export { defaultOperatorOptions } from "./type";

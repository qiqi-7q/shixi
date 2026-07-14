import Sortable from "sortablejs";
import { useEpThemeStoreHook } from "@/store/modules/epTheme";
import { useTableColumnStoreHook } from "@/store/modules/tableColumn";
import {
  type PropType,
  ref,
  unref,
  computed,
  nextTick,
  defineComponent,
  getCurrentInstance,
  onMounted,
  watch
} from "vue";
import {
  delay,
  cloneDeep,
  isBoolean,
  isFunction,
  getKeyList
} from "@pureadmin/utils";

import Fullscreen from "~icons/ri/fullscreen-fill";
import ExitFullscreen from "~icons/ri/fullscreen-exit-fill";
import DragIcon from "@/assets/table-bar/drag.svg?component";
import ExpandIcon from "@/assets/table-bar/expand.svg?component";
import RefreshIcon from "@/assets/table-bar/refresh.svg?component";
import SettingIcon from "@/assets/table-bar/settings.svg?component";
import CollapseIcon from "@/assets/table-bar/collapse.svg?component";

const props = {
  /** 头部最左边的标题 */
  title: {
    type: String,
    default: "列表"
  },
  /** 对于树形表格，如果想启用展开和折叠功能，传入当前表格的ref即可 */
  tableRef: {
    type: Object as PropType<any>
  },
  /** 需要展示的列 */
  columns: {
    type: Array as PropType<TableColumnList>,
    default: () => []
  },
  isExpandAll: {
    type: Boolean,
    default: true
  },
  tableKey: {
    type: [String, Number] as PropType<string | number>,
    default: "0"
  }
};

export default defineComponent({
  name: "PureTableBar",
  props,
  emits: ["refresh", "fullscreen"],
  setup(props, { emit, slots, attrs }) {
    const size = ref("default");
    const loading = ref(false);
    const checkAll = ref(true);
    const isFullscreen = ref(false);
    const isIndeterminate = ref(false);
    const instance = getCurrentInstance()!;
    const isExpandAll = ref(props.isExpandAll);
    const tableColumnStore = useTableColumnStoreHook();

    // 原始列配置（用于重置），使用 ref 确保每个实例独立
    const originalColumns = ref<TableColumnList>(cloneDeep(props?.columns));
    const filterColumns = cloneDeep(props?.columns).filter(column =>
      isBoolean(column?.hide)
        ? !column.hide
        : !(isFunction(column?.hide) && column?.hide())
    );
    let checkColumnList = getKeyList(cloneDeep(props?.columns), "label");
    const checkedColumns = ref(getKeyList(cloneDeep(filterColumns), "label"));
    const dynamicColumns = ref(cloneDeep(props?.columns));

    /** 保存当前列配置到本地存储 */
    function saveColumnConfig() {
      const tableKey = String(props.tableKey);
      const order = dynamicColumns.value.map(col => col.label);
      const hidden = dynamicColumns.value
        .filter(col => col.hide)
        .map(col => col.label);
      tableColumnStore.saveColumnConfig(tableKey, { order, hidden });
    }

    /** 从本地存储恢复列配置 */
    function restoreColumnConfig() {
      const tableKey = String(props.tableKey);
      const config = tableColumnStore.getColumnConfig(tableKey);
      if (!config || !config.order || config.order.length === 0) return false;

      // 根据保存的顺序重新排列列
      const orderedColumns: TableColumnList = [];
      const orderMap = new Map<string, number>();
      config.order.forEach((label, index) => orderMap.set(label, index));

      // 先按保存的顺序排列
      const columnsMap = new Map<string, TableColumnItem>();
      originalColumns.value.forEach(col => columnsMap.set(col.label, col));

      config.order.forEach(label => {
        const col = columnsMap.get(label);
        if (col) {
          const cloned = cloneDeep(col);
          // 恢复隐藏状态
          cloned.hide = config.hidden?.includes(label) ?? false;
          orderedColumns.push(cloned);
        }
      });

      // 添加新增的列（后端可能新增了字段）
      originalColumns.value.forEach(col => {
        if (!config.order.includes(col.label)) {
          orderedColumns.push(cloneDeep(col));
        }
      });

      dynamicColumns.value = orderedColumns;
      checkedColumns.value = orderedColumns
        .filter(col => !col.hide)
        .map(col => col.label);
      checkColumnList = orderedColumns.map(col => col.label);

      // 更新全选状态
      const checkedCount = checkedColumns.value.length;
      checkAll.value = checkedCount === checkColumnList.length;
      isIndeterminate.value =
        checkedCount > 0 && checkedCount < checkColumnList.length;

      return true;
    }

    onMounted(() => {
      restoreColumnConfig();
    });

    // 监听 columns 变化，重新恢复配置（解决 keep-alive 缓存问题）
    watch(
      () => props.columns,
      () => {
        // 更新原始列备份
        originalColumns.value.splice(
          0,
          originalColumns.value.length,
          ...cloneDeep(props.columns)
        );
        restoreColumnConfig();
      },
      { deep: true }
    );

    const getDropdownItemStyle = computed(() => {
      return s => {
        return {
          background:
            s === size.value ? useEpThemeStoreHook().epThemeColor : "",
          color: s === size.value ? "#fff" : "var(--el-text-color-primary)"
        };
      };
    });

    const iconClass = computed(() => {
      return [
        "text-black",
        "dark:text-white",
        "duration-100",
        "hover:text-primary!",
        "cursor-pointer",
        "outline-hidden"
      ];
    });

    const topClass = computed(() => {
      return [
        "flex",
        "justify-between",
        "pt-[3px]",
        "px-[11px]",
        "border-b-[1px]",
        "border-solid",
        "border-[#dcdfe6]",
        "dark:border-[#303030]"
      ];
    });

    function onReFresh() {
      loading.value = true;
      emit("refresh");
      delay(500).then(() => (loading.value = false));
    }

    function onExpand() {
      isExpandAll.value = !isExpandAll.value;
      toggleRowExpansionAll(props.tableRef.data, isExpandAll.value);
    }

    function onFullscreen() {
      isFullscreen.value = !isFullscreen.value;
      emit("fullscreen", isFullscreen.value);
    }

    function toggleRowExpansionAll(data, isExpansion) {
      data.forEach(item => {
        props.tableRef.toggleRowExpansion(item, isExpansion);
        if (item.children !== undefined && item.children !== null) {
          toggleRowExpansionAll(item.children, isExpansion);
        }
      });
    }

    function handleCheckAllChange(val: boolean) {
      checkedColumns.value = val ? checkColumnList : [];
      isIndeterminate.value = false;
      dynamicColumns.value.map(column =>
        val ? (column.hide = false) : (column.hide = true)
      );
      saveColumnConfig();
    }

    function handleCheckedColumnsChange(value: string[]) {
      checkedColumns.value = value;
      const checkedCount = value.length;
      checkAll.value = checkedCount === checkColumnList.length;
      isIndeterminate.value =
        checkedCount > 0 && checkedCount < checkColumnList.length;
      saveColumnConfig();
    }

    function handleCheckColumnListChange(val: boolean, label: string) {
      dynamicColumns.value.filter(item => item.label === label)[0].hide = !val;
      saveColumnConfig();
    }

    async function onReset() {
      checkAll.value = true;
      isIndeterminate.value = false;
      dynamicColumns.value = cloneDeep(originalColumns.value);
      checkColumnList = [];
      checkColumnList = await getKeyList(
        cloneDeep(originalColumns.value),
        "label"
      );
      checkedColumns.value = getKeyList(
        cloneDeep(originalColumns.value).filter(column =>
          isBoolean(column?.hide)
            ? !column.hide
            : !(isFunction(column?.hide) && column?.hide())
        ),
        "label"
      );
      // 清除本地存储
      tableColumnStore.clearColumnConfig(String(props.tableKey));
    }

    const dropdown = {
      dropdown: () => (
        <el-dropdown-menu class="translation">
          <el-dropdown-item
            style={getDropdownItemStyle.value("large")}
            onClick={() => (size.value = "large")}
          >
            宽松
          </el-dropdown-item>
          <el-dropdown-item
            style={getDropdownItemStyle.value("default")}
            onClick={() => (size.value = "default")}
          >
            默认
          </el-dropdown-item>
          <el-dropdown-item
            style={getDropdownItemStyle.value("small")}
            onClick={() => (size.value = "small")}
          >
            紧凑
          </el-dropdown-item>
        </el-dropdown-menu>
      )
    };

    /** 列展示拖拽排序 */
    const rowDrop = (event: { preventDefault: () => void }) => {
      event.preventDefault();
      nextTick(() => {
        const wrapper: HTMLElement = (
          instance?.proxy?.$refs[`GroupRef${unref(props.tableKey)}`] as any
        ).$el.firstElementChild;
        Sortable.create(wrapper, {
          animation: 300,
          handle: ".drag-btn",
          onEnd: ({ newIndex, oldIndex, item }) => {
            const targetThElem = item;
            const wrapperElem = targetThElem.parentNode as HTMLElement;
            const oldColumn = dynamicColumns.value[oldIndex];
            const newColumn = dynamicColumns.value[newIndex];
            if (
              oldColumn?.fixed ||
              newColumn?.fixed ||
              oldColumn?.label == "序号" ||
              newColumn?.label == "序号"
            ) {
              // 当前列存在fixed属性 则不可拖拽
              const oldThElem = wrapperElem.children[oldIndex] as HTMLElement;
              if (newIndex > oldIndex) {
                wrapperElem.insertBefore(targetThElem, oldThElem);
              } else {
                wrapperElem.insertBefore(
                  targetThElem,
                  oldThElem ? oldThElem.nextElementSibling : oldThElem
                );
              }
              return;
            }
            const currentRow = dynamicColumns.value.splice(oldIndex, 1)[0];
            dynamicColumns.value.splice(newIndex, 0, currentRow);
            // 拖拽结束后保存配置
            saveColumnConfig();
          }
        });
      });
    };

    const isFixedColumn = (label: string) => {
      const col = dynamicColumns.value.find(item => item.label === label);
      return col?.fixed || label === "序号" ? true : false;
    };

    const rendTippyProps = (content: string) => {
      // https://vue-tippy.netlify.app/props
      return {
        content,
        offset: [0, 18],
        duration: [300, 0],
        followCursor: true,
        hideOnClick: "toggle"
      };
    };

    const reference = {
      reference: () => (
        <SettingIcon
          class={["w-[16px]", iconClass.value]}
          v-tippy={rendTippyProps("列设置")}
        />
      )
    };

    return () => (
      <>
        <div
          {...attrs}
          class={[
            "w-full",
            "px-2",
            "pb-2",
            "bg-bg_color",
            isFullscreen.value
              ? ["h-full!", "z-2002", "fixed", "inset-0"]
              : "mt-2"
          ]}
        >
          <div class="flex justify-between w-full h-[60px] p-4">
            {slots?.title ? (
              slots.title()
            ) : (
              <p class="font-bold truncate">{props.title}</p>
            )}
            <div class="flex items-center justify-around">
              {slots?.buttons ? (
                <div class="flex mr-4">{slots.buttons()}</div>
              ) : null}
              {props.tableRef?.size ? (
                <>
                  <ExpandIcon
                    class={["w-[16px]", iconClass.value]}
                    style={{
                      transform: isExpandAll.value ? "none" : "rotate(-90deg)"
                    }}
                    v-tippy={rendTippyProps(
                      isExpandAll.value ? "折叠" : "展开"
                    )}
                    onClick={() => onExpand()}
                  />
                  <el-divider direction="vertical" />
                </>
              ) : null}
              <RefreshIcon
                class={[
                  "w-[16px]",
                  iconClass.value,
                  loading.value ? "animate-spin" : ""
                ]}
                v-tippy={rendTippyProps("刷新")}
                onClick={() => onReFresh()}
              />
              <el-divider direction="vertical" />
              <el-dropdown
                v-slots={dropdown}
                trigger="click"
                v-tippy={rendTippyProps("密度")}
              >
                <CollapseIcon class={["w-[16px]", iconClass.value]} />
              </el-dropdown>
              <el-divider direction="vertical" />

              <el-popover
                v-slots={reference}
                placement="bottom-start"
                popper-style={{ padding: 0 }}
                width="200"
                trigger="click"
              >
                <div class={[topClass.value]}>
                  <el-checkbox
                    class="-mr-1!"
                    label="列展示"
                    v-model={checkAll.value}
                    indeterminate={isIndeterminate.value}
                    onChange={value => handleCheckAllChange(value)}
                  />
                  <el-button type="primary" link onClick={() => onReset()}>
                    重置
                  </el-button>
                </div>

                <div class="pt-[6px] pl-[11px]">
                  <el-scrollbar max-height="36vh">
                    <el-checkbox-group
                      ref={`GroupRef${unref(props.tableKey)}`}
                      modelValue={checkedColumns.value}
                      onChange={value => handleCheckedColumnsChange(value)}
                    >
                      <el-space
                        direction="vertical"
                        alignment="flex-start"
                        size={0}
                      >
                        {checkColumnList.map((item, index) => {
                          return (
                            <div class="flex items-center">
                              <DragIcon
                                class={[
                                  "drag-btn w-[16px] mr-2",
                                  isFixedColumn(item)
                                    ? "cursor-no-drop!"
                                    : "cursor-grab!"
                                ]}
                                onMouseenter={(event: {
                                  preventDefault: () => void;
                                }) => rowDrop(event)}
                              />
                              <el-checkbox
                                key={index}
                                label={item}
                                value={item}
                                onChange={value =>
                                  handleCheckColumnListChange(value, item)
                                }
                              >
                                <span
                                  title={item}
                                  class="inline-block w-[120px] truncate hover:text-text_color_primary"
                                >
                                  {item}
                                </span>
                              </el-checkbox>
                            </div>
                          );
                        })}
                      </el-space>
                    </el-checkbox-group>
                  </el-scrollbar>
                </div>
              </el-popover>
              <el-divider direction="vertical" />

              <iconifyIconOffline
                class={["w-[16px]", iconClass.value]}
                icon={isFullscreen.value ? ExitFullscreen : Fullscreen}
                v-tippy={isFullscreen.value ? "退出全屏" : "全屏"}
                onClick={() => onFullscreen()}
              />
            </div>
          </div>
          {slots.default({
            size: size.value,
            dynamicColumns: dynamicColumns.value
          })}
        </div>
      </>
    );
  }
});

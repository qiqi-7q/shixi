<script setup lang="ts">
/**
 * ============================================
 * 项目计划甘特图页面
 * ============================================
 * 功能：展示项目发版计划的甘特图，按月份和周次显示 SOP/OTA 节点
 * 数据来源：后端读取 Excel 文件返回的项目进度数据
 */

import { ref, computed, onMounted, onBeforeUnmount, nextTick } from "vue";
import { createProjectPlan, uploadPlanFile } from "@/api/system";
import { message } from "@/utils/message";
import { useRenderIcon } from "@/components/ReIcon/src/hooks";
import type { TableColumnCtx } from "element-plus";
import Upload from "~icons/ep/upload";
import Refresh from "~icons/ep/refresh";
defineOptions({ name: "TestProjectPlan" });

// ==================== 响应式数据 ====================

/** 加载状态 */
const loading = ref(false);

/** 全部项目数据（从后端获取） */
const allData = ref<any[]>([]);

/** 未来三个月的整车发测任务（从后端获取） */
const upcomingTasks = ref<any[]>([]);

/** 默认读取的 Excel 文件路径 */
const defaultFilePath = "项目进度表.xlsx";

/** 全部项目表格的引用 */
const allTableRef = ref<InstanceType<any>>();

/** 全部项目表格的最大高度 */
const allTableMaxHeight = ref(0);

/** 发版计划类别：电子内部发测、整车发测 */
const categories = ["电子内部发测", "整车发测"];

// ==================== 文件上传相关 ====================

/** 上传弹窗显示状态 */
const uploadDialogVisible = ref(false);

/** 上传加载状态 */
const uploadLoading = ref(false);

/** 上传进度 */
const uploadProgress = ref(0);

/** 当前选择的文件 */
const uploadFile = ref<File | null>(null);

/** 分片大小：2MB */
const CHUNK_SIZE = 2 * 1024 * 1024;

/**
 * 计算文件 MD5（使用简单的哈希算法，实际项目建议使用 spark-md5）
 * 这里使用文件名+大小+修改时间作为简易标识
 */
function calculateFileMd5(file: File): Promise<string> {
  return new Promise(resolve => {
    // 使用文件名+大小+修改时间作为简易标识
    // 实际项目中建议使用 spark-md5 库计算真实 MD5
    const content = `${file.name}_${file.size}_${file.lastModified}`;
    let hash = 0;
    for (let i = 0; i < content.length; i++) {
      const char = content.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash = hash & hash; // 转为 32 位整数
    }
    resolve(Math.abs(hash).toString(16).padStart(8, "0"));
  });
}

/**
 * 打开上传弹窗
 */
function onUpload() {
  uploadDialogVisible.value = true;
  uploadFile.value = null;
  uploadProgress.value = 0;
}

/**
 * 处理文件选择
 */
function handleUploadFileChange(file: any) {
  uploadFile.value = file.raw;
}

/**
 * 移除已选文件
 */
function handleUploadFileRemove() {
  uploadFile.value = null;
  uploadProgress.value = 0;
}

/**
 * 分片上传文件
 */
async function handleUpload() {
  if (!uploadFile.value) {
    message("请先选择文件", { type: "warning" });
    return;
  }

  try {
    uploadLoading.value = true;
    uploadProgress.value = 0;

    const file = uploadFile.value;
    const totalSize = file.size;
    const totalChunks = Math.ceil(totalSize / CHUNK_SIZE);

    // 计算文件 MD5
    const fileMd5 = await calculateFileMd5(file);

    // 如果文件小于等于 2MB，直接上传不分片
    if (totalSize <= CHUNK_SIZE) {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("fileMd5", fileMd5);
      formData.append("chunkIndex", "0");
      formData.append("totalChunk", "1");
      formData.append("totalSize", String(totalSize));

      uploadProgress.value = 50;
      const res: any = await uploadPlanFile(formData);
      uploadProgress.value = 100;

      if (res?.code === 200) {
        message("文件上传成功", { type: "success" });
        uploadDialogVisible.value = false;
        await loadData();
      } else {
        message(res?.message || "文件上传失败", { type: "error" });
      }
    } else {
      // 大文件分片上传
      for (let i = 0; i < totalChunks; i++) {
        const start = i * CHUNK_SIZE;
        const end = Math.min(start + CHUNK_SIZE, totalSize);
        const chunk = file.slice(start, end);

        const formData = new FormData();
        formData.append("file", chunk);
        formData.append("fileMd5", fileMd5);
        formData.append("chunkIndex", String(i));
        formData.append("totalChunk", String(totalChunks));
        formData.append("totalSize", String(totalSize));

        const res: any = await uploadPlanFile(formData);

        // 更新进度
        uploadProgress.value = Math.round(((i + 1) / totalChunks) * 100);

        // 如果已合并完成，跳出循环
        if (res?.merged) {
          break;
        }
      }

      message("文件上传成功", { type: "success" });
      uploadDialogVisible.value = false;
      await loadData();
    }
  } catch (error) {
    message("文件上传失败", { type: "error" });
    console.error("上传错误:", error);
  } finally {
    uploadLoading.value = false;
  }
}

// ==================== 工具函数 ====================

/**
 * 解析周次字符串
 * @param week 周次字符串，格式："2026.1.W1"
 * @returns [年份, 月份, 周数]，例如：[2026, 1, 1]
 */
function parseWeek(week: string): [number, number, number] {
  const p = week.split("."); // ["2026", "1", "W1"]
  return [parseInt(p[0]), parseInt(p[1]), parseInt(p[2].replace("W", ""))];
}

/**
 * 从数据值中提取纯周次
 * @param value 数据值，格式："2026.5.W4: 5/25"
 * @returns 纯周次字符串，例如："2026.5.W4"
 */
function extractWeekFromValue(value: string): string {
  return value.split(":")[0].trim(); // 按冒号分割，取前半部分
}

/**
 * 比较两个周次的大小（用于排序）
 * @param a 周次A，例如："2026.1.W1"
 * @param b 周次B，例如："2026.2.W3"
 * @returns 负数表示 a < b，正数表示 a > b，0 表示相等
 */
function compareWeek(a: string, b: string): number {
  const pa = parseWeek(a); // [2026, 1, 1]
  const pb = parseWeek(b); // [2026, 2, 3]

  // 依次比较年、月、周
  for (let i = 0; i < 3; i++) {
    if (pa[i] !== pb[i]) return pa[i] - pb[i];
  }
  return 0;
}

/**
 * 从数据中提取所有唯一的周次，并按时间排序
 * @param data 项目数据数组
 * @returns 排序后的周次数组，例如：["2026.1.W1", "2026.1.W2", "2026.2.W1"]
 */
function extractAllWeeks(data: any[]): string[] {
  const s = new Set<string>(); // 用 Set 去重

  // 遍历每条项目数据
  data.forEach(row => {
    // 遍历每个发版类别（电子内部发测、整车发测）
    categories.forEach(cat => {
      // 遍历每种类型（SOP、OTA）
      ["SOP", "OTA"].forEach(type => {
        const arr = row[cat]?.[type]; // 获取该类别该类型的周次数组
        if (Array.isArray(arr)) {
          arr.forEach((w: string) => {
            // 提取纯周次格式 "2026.5.W4: 5/25" → "2026.5.W4"
            const pureWeek = extractWeekFromValue(w);
            s.add(pureWeek); // 添加到 Set 中（自动去重）
          });
        }
      });
    });
  });

  // 转成数组并排序
  return Array.from(s).sort(compareWeek);
}

// ==================== 计算属性 ====================

/**
 * 所有唯一的周次（合并全部数据和未来任务数据）
 * 用于生成"全部项目数据"表格的表头
 */
const allWeeks = computed(() =>
  extractAllWeeks([...allData.value, ...upcomingTasks.value])
);

/**
 * 按月份分组所有周次
 * 用于"全部项目数据"表格的多级表头
 *
 * 输入：["2026.1.W1", "2026.1.W2", "2026.2.W1"]
 * 输出：[
 *   { label: "2026年1月", weeks: ["2026.1.W1", "2026.1.W2"] },
 *   { label: "2026年2月", weeks: ["2026.2.W1"] }
 * ]
 */
const monthGroups = computed(() => {
  const map = new Map<string, string[]>(); // key: 月份标签, value: 该月的周次数组

  // 遍历所有周次，按月份分组
  allWeeks.value.forEach(week => {
    const [year, month] = parseWeek(week); // 解析出年和月
    const label = `${year}年${month}月`; // 生成月份标签，如 "2026年1月"

    if (!map.has(label)) map.set(label, []); // 如果这个月份还没创建，就初始化
    map.get(label)!.push(week); // 把当前周次添加到对应月份
  });
  // 将 Map 转换成数组格式返回
  return Array.from(map.entries()).map(([label, weeks]) => ({ label, weeks }));
});

/**
 * 生成未来任务的完整连续月份分组
 * 与 monthGroups 不同，这个会补齐中间没有数据的月份，并标记哪些周次有数据
 *
 * 输入：["2026.5.W4", "2026.7.W1"]（只有5月和7月有数据）
 * 输出：[
 *   { label: "2026年5月", weeks: [{ key: "2026.5.W1", hasData: false }, ...] },
 *   { label: "2026年6月", weeks: [{ key: "2026.6.W1", hasData: false }, ...] },  // 6月也会显示
 *   { label: "2026年7月", weeks: [{ key: "2026.7.W1", hasData: true }, ...] }
 * ]
 */
const upcomingMonthGroups = computed(() => {
  const weeks = extractAllWeeks(upcomingTasks.value); // 提取未来任务的所有周次
  if (weeks.length === 0) return []; // 没有数据就返回空数组

  // 找到最早和最晚的周次
  const minWeek = parseWeek(weeks[0]); // 最早周次，如 [2026, 5, 4]
  const maxWeek = parseWeek(weeks[weeks.length - 1]); // 最晚周次，如 [2026, 7, 1]

  // 生成从最早月到最晚月的所有月份（包括中间没有数据的月份）
  const months: { year: number; month: number }[] = [];
  let y = minWeek[0],
    m = minWeek[1];
  while (y < maxWeek[0] || (y === maxWeek[0] && m <= maxWeek[1])) {
    months.push({ year: y, month: m });
    m++;
    if (m > 12) {
      // 跨年处理
      m = 1;
      y++;
    }
  }

  // 收集数据中实际出现的周次（用于标记 hasData）
  const existingWeeks = new Set(weeks);

  // 为每个月生成 W1~W4，标记是否有数据
  return months.map(({ year, month }) => ({
    label: `${year}年${month}月`,
    weeks: [1, 2, 3, 4].map(w => ({
      key: `${year}.${month}.W${w}`, // 周次 key，如 "2026.5.W1"
      label: `W${w}`, // 表头显示，如 "W1"
      hasData: existingWeeks.has(`${year}.${month}.W${w}`) // 这个周次是否有数据
    }))
  }));
});

/**
 * 获取某个单元格应该显示的标签（SOP/OTA）
 * @param row 当前行数据
 * @param category 发版类别（电子内部发测/整车发测）
 * @param week 当前列的周次，如 "2026.5.W4"
 * @returns 标签数组，如 [{ label: "SOP 5/25", type: "danger" }]
 */
function getCellTags(
  row: any,
  category: string,
  week: string
): { label: string; type: string }[] {
  const tags: { label: string; type: string }[] = [];
  const sop: string[] = row[category]?.SOP || []; // 获取该类别的 SOP 周次
  const ota: string[] = row[category]?.OTA || []; // 获取该类别的 OTA 周次

  // 查找当前周次是否有 SOP
  const sopMatch = sop.find((w: string) => extractWeekFromValue(w) === week);
  if (sopMatch) {
    const date = sopMatch.split(":")[1]?.trim() || ""; // 提取日期，如 "5/25"
    tags.push({ label: date ? `SOP ${date}` : "SOP", type: "danger" });
  }

  // 查找当前周次是否有 OTA
  const otaMatch = ota.find((w: string) => extractWeekFromValue(w) === week);
  if (otaMatch) {
    const date = otaMatch.split(":")[1]?.trim() || ""; // 提取日期，如 "6/19"
    tags.push({ label: date ? `OTA ${date}` : "OTA", type: "success" });
  }

  return tags;
}

// ==================== 数据加载 ====================

/**
 * 加载项目计划数据
 * 调用后端接口读取 Excel 文件，获取项目进度数据
 */
const loadData = async () => {
  try {
    loading.value = true;
    const res = (await createProjectPlan({
      file_path: defaultFilePath
    })) as any;

    if (res?.code === 200) {
      allData.value = res.data?.all_data || []; // 全部项目数据
      upcomingTasks.value = res.data?.upcoming_vehicle_tasks || []; // 未来任务数据
      message(res?.message || "加载成功", { type: "success" });
      calcTableHeight(); // 计算表格高度
    } else {
      message(res?.message || "加载失败", { type: "error" });
    }
  } catch (error) {
    message("加载项目计划失败", { type: "error" });
  } finally {
    loading.value = false;
  }
};

/**
 * 计算表格最大高度
 * 让表格高度自适应窗口大小
 */
function calcTableHeight() {
  nextTick(() => {
    const el = allTableRef.value?.$el as HTMLElement | undefined;
    if (el) {
      const top = el.getBoundingClientRect().top; // 表格距离顶部的距离
      allTableMaxHeight.value = window.innerHeight - 240; // 窗口高度减去固定部分
    }
  });
}

// ==================== 生命周期 ====================

/**
 * 组件挂载时执行
 * 1. 加载数据
 * 2. 计算表格高度
 * 3. 监听窗口大小变化
 */
onMounted(() => {
  loadData();
  calcTableHeight();
  window.addEventListener("resize", calcTableHeight);
});

/**
 * 组件卸载前执行
 * 移除窗口大小变化监听器（防止内存泄漏）
 */
onBeforeUnmount(() => {
  window.removeEventListener("resize", calcTableHeight);
});

// ==================== 数据处理 ====================

/**
 * 将未来任务数据转换为扁平结构
 * 每个项目拆成两行：一行电子内部发测，一行整车发测
 *
 * 输入：[{ "项目": "A10", "电子内部发测": {...}, "整车发测": {...} }]
 * 输出：[
 *   { _project: "A10", _category: "电子内部发测", ... },
 *   { _project: "A10", _category: "整车发测", ... }
 * ]
 */
const flattenUpcomingData = computed(() => {
  const result: any[] = [];

  upcomingTasks.value.forEach((row, idx) => {
    categories.forEach((cat, catIdx) => {
      result.push({
        _project: row["项目"], // 项目名称
        _category: cat, // 发版类别
        _rowIndex: idx, // 原始行索引
        _catIndex: catIdx, // 类别索引
        ...row // 展开原始数据
      });
    });
  });

  return result;
});

/**
 * 将全部项目数据转换为扁平结构
 * 逻辑同上
 */
const flattenAllData = computed(() => {
  const result: any[] = [];

  allData.value.forEach((row, idx) => {
    categories.forEach((cat, catIdx) => {
      result.push({
        _project: row["项目"],
        _category: cat,
        _rowIndex: idx,
        _catIndex: catIdx,
        ...row
      });
    });
  });

  return result;
});

/**
 * 合并单元格方法
 * 用于将同一项目的两行（电子内部发测、整车发测）的项目列合并
 *
 * @param rowIndex 行索引
 * @param columnIndex 列索引
 * @returns { rowspan, colspan } 合并规则
 */
const spanMethod = ({
  rowIndex,
  columnIndex
}: {
  rowIndex: number;
  columnIndex: number;
}) => {
  // 只处理第一列（项目列）
  if (columnIndex === 0) {
    // 偶数行：合并当前行和下一行（rowspan: 2）
    if (rowIndex % 2 === 0) {
      return { rowspan: 2, colspan: 1 };
    } else {
      // 奇数行：被合并，不显示（rowspan: 0, colspan: 0）
      return { rowspan: 0, colspan: 0 };
    }
  }
};
</script>

<template>
  <div class="p-4">
    <el-card shadow="never">
      <template #header>
        <div class="flex items-center justify-between">
          <span class="text-lg font-medium">项目计划</span>
          <div class="flex gap-2">
            <el-button
              type="success"
              :icon="useRenderIcon(Upload)"
              @click="onUpload"
            >
              上传文件
            </el-button>
            <el-button :loading="loading" @click="loadData">
              <el-icon><component :is="useRenderIcon(Refresh)" /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <!-- 未来三个月整车发测任务 -->
      <div class="mb-6">
        <div class="text-base font-medium mb-4">
          未来三个月整车发测任务
          <el-tag type="danger" class="ml-2">
            {{ upcomingTasks.length }} 个项目
          </el-tag>
        </div>
        <el-table
          v-loading="loading"
          :data="flattenUpcomingData"
          border
          :span-method="spanMethod"
          stripe
          class="gantt-table mb-6"
        >
          <!-- 项目列（合并单元格） -->
          <el-table-column
            prop="_project"
            label="项目"
            min-width="180"
            fixed="left"
            align="center"
          />
          <!-- 发版计划列 -->
          <el-table-column
            prop="_category"
            label="发版计划"
            width="140"
            align="center"
          />
          <!-- 周次列 -->
          <el-table-column
            v-for="month in upcomingMonthGroups"
            :key="month.label"
            :label="month.label"
            align="center"
          >
            <el-table-column
              v-for="week in month.weeks"
              :key="week.key"
              :label="week.label"
              :width="80"
              align="center"
              :class-name="!week.hasData ? 'empty-week' : ''"
            >
              <template #default="{ row }">
                <template v-if="week.hasData">
                  <el-tag
                    v-for="tag in getCellTags(row, row._category, week.key)"
                    :key="tag.label"
                    :type="tag.type as any"
                    size="small"
                    class="cell-tag"
                  >
                    {{ tag.label }}
                  </el-tag>
                </template>
              </template>
            </el-table-column>
          </el-table-column>
        </el-table>
      </div>

      <!-- 全部项目数据 -->
      <div>
        <div class="text-base font-medium mb-4">
          全部项目数据
          <el-tag type="primary" class="ml-2">
            {{ allData.length }} 个项目
          </el-tag>
        </div>
        <el-table
          ref="allTableRef"
          v-loading="loading"
          :data="flattenAllData"
          :max-height="allTableMaxHeight"
          border
          :span-method="spanMethod"
          stripe
          class="gantt-table"
        >
          <!-- 项目列（合并单元格） -->
          <el-table-column
            prop="_project"
            label="项目"
            min-width="180"
            fixed="left"
            align="center"
          />
          <!-- 发版计划列 -->
          <el-table-column
            prop="_category"
            label="发版计划"
            width="140"
            align="center"
          />
          <!-- 周次列 -->
          <el-table-column
            v-for="month in monthGroups"
            :key="month.label"
            :label="month.label"
            align="center"
          >
            <el-table-column
              v-for="week in month.weeks"
              :key="week"
              :label="'W' + parseWeek(week)[2]"
              width="80"
              align="center"
            >
              <template #default="{ row }">
                <el-tag
                  v-for="tag in getCellTags(row, row._category, week)"
                  :key="tag.label"
                  :type="tag.type as any"
                  size="small"
                  class="cell-tag"
                >
                  {{ tag.label }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 文件上传弹窗 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传项目计划文件"
      width="500px"
      top="25vh"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <div class="px-2">
        <el-upload
          v-if="!uploadFile"
          drag
          :auto-upload="false"
          :limit="1"
          :multiple="false"
          accept=".xlsx,.xls"
          :on-change="handleUploadFileChange"
          :on-remove="handleUploadFileRemove"
        >
          <div class="el-upload__text">
            将Excel文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              仅支持 .xlsx / .xls 格式的Excel文件
            </div>
          </template>
        </el-upload>
        <div v-else class="flex items-center gap-2 p-3 bg-gray-50 rounded">
          <el-icon class="text-green-500">
            <component :is="useRenderIcon('ep/document')" />
          </el-icon>
          <span class="flex-1 truncate">{{ uploadFile.name }}</span>
          <el-button
            type="danger"
            text
            size="small"
            @click="handleUploadFileRemove"
          >
            移除
          </el-button>
        </div>

        <!-- 上传进度条 -->
        <el-progress
          v-if="uploadLoading"
          :percentage="uploadProgress"
          :stroke-width="12"
          class="mt-4"
        />

        <el-alert
          class="mt-4"
          title="说明：上传Excel文件后，系统将自动解析并更新项目计划数据。"
          type="info"
          :closable="false"
          show-icon
        />
      </div>

      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="uploadLoading"
          :disabled="!uploadFile"
          @click="handleUpload"
        >
          {{ uploadLoading ? `上传中 ${uploadProgress}%` : "上传" }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.gantt-table :deep(.cell) {
  padding: 2px 4px;
}

.gantt-table :deep(.cell .cell-tag) {
  margin: 0;
}

.gantt-table :deep(.el-tag--danger) {
  font-weight: bold;
}

.gantt-table :deep(.el-tag--success) {
  font-weight: bold;
}

.gantt-table :deep(.empty-week) {
  background-color: #fafafa;
}

.gantt-table :deep(.empty-week .cell) {
  padding: 0;
}
</style>

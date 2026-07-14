<script setup lang="ts">
import ReCol from "@/components/ReCol";
import { useDark } from "./utils";
import { useDashboard } from "./hook";
import { useRenderIcon } from "@/components/ReIcon/src/hooks";

defineOptions({
  name: "Welcome"
});

const { isDark } = useDark();
const {
  statistics,
  loading,
  projectOptions,
  selectedProject,
  modelOptions,
  versionChartRef,
  dailyMileageChartRef,
  ladderChartRef,
  distanceLadderChartRef,
  groupsChartRef,
  ladderDate,
  distanceLadderDate,
  ladderModel,
  distanceLadderModel,
  chartModel,
  loadLadderChart,
  loadDistanceLadderChart,
  loadGroupsChart,
  loadMileageCharts
} = useDashboard();
</script>

<template>
  <div v-loading="loading">
    <!-- 统计卡片 -->
    <div class="mt-4 grid grid-cols-5 gap-4">
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          车辆总数
        </div>
        <div class="text-2xl font-bold">{{ statistics.vehicleTotal }}</div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          当前可用
        </div>
        <div class="text-2xl font-bold text-[#67C23A]">
          {{ statistics.vehicleAvailable }}
        </div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          已借出
        </div>
        <div class="text-2xl font-bold text-[#409EFF]">
          {{ statistics.vehicleBorrowed }}
        </div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          维护中
        </div>
        <div class="text-2xl font-bold text-[#E6A23C]">
          {{ statistics.vehicleMaintenance }}
        </div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          已预定
        </div>
        <div class="text-2xl font-bold text-[#909399]">
          {{ statistics.vehicleReserved }}
        </div>
      </div>
    </div>
    <!-- 图表区域 -->
    <!-- 车辆使用率天梯图 & 行驶里程排行 -->
    <el-row :gutter="24" class="mt-4">
      <re-col
        v-motion
        class="mb-4.5"
        :value="12"
        :xs="24"
        :initial="{ opacity: 0, y: 100 }"
        :enter="{ opacity: 1, y: 0, transition: { delay: 720 } }"
      >
        <el-card shadow="never">
          <div class="flex items-center justify-between mb-4">
            <div class="text-base font-medium flex items-center gap-2">
              <el-icon class="text-purple-500" size="18"
                ><component :is="useRenderIcon('ep/rank')"
              /></el-icon>
              车辆使用率排行
            </div>
            <div class="flex items-center gap-2">
              <el-select
                v-model="ladderModel"
                placeholder="选择车型"
                multiple
                collapse-tags
                collapse-tags-tooltip
                :max-collapse-tags="1"
                filterable
                clearable
                style="width: 200px"
                @change="loadLadderChart"
              >
                <el-option
                  v-for="m in modelOptions"
                  :key="m"
                  :label="m"
                  :value="m"
                />
              </el-select>
              <el-date-picker
                v-model="ladderDate"
                type="daterange"
                range-separator="~"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 260px"
                @change="loadLadderChart"
              />
            </div>
          </div>
          <div ref="ladderChartRef" style="height: 380px; width: 100%"></div>
        </el-card>
      </re-col>

      <re-col
        v-motion
        class="mb-4.5"
        :value="12"
        :xs="24"
        :initial="{ opacity: 0, y: 100 }"
        :enter="{ opacity: 1, y: 0, transition: { delay: 800 } }"
      >
        <el-card shadow="never">
          <div class="flex items-center justify-between mb-4">
            <div class="text-base font-medium flex items-center gap-2">
              <el-icon class="text-green-500" size="18"
                ><component :is="useRenderIcon('ep/histogram')"
              /></el-icon>
              组别使用率统计
            </div>
            <el-select
              v-model="chartModel"
              placeholder="选择车型"
              filterable
              clearable
              style="width: 150px"
              @change="loadGroupsChart"
            >
              <el-option
                v-for="m in modelOptions"
                :key="m"
                :label="m"
                :value="m"
              />
            </el-select>
          </div>
          <div ref="groupsChartRef" style="height: 380px; width: 100%"></div>
        </el-card>
      </re-col>
    </el-row>

    <el-row :gutter="24" class="mt-4">
      <re-col
        v-motion
        class="mb-4.5"
        :value="12"
        :xs="24"
        :initial="{ opacity: 0, y: 100 }"
        :enter="{ opacity: 1, y: 0, transition: { delay: 560 } }"
      >
        <el-card shadow="never">
          <div class="flex items-center justify-between mb-4">
            <div class="text-base font-medium">版本里程</div>
            <el-select
              v-model="selectedProject"
              placeholder="全部项目"
              clearable
              style="width: 150px"
            >
              <el-option
                v-for="item in projectOptions"
                :key="item"
                :label="item"
                :value="item"
              />
            </el-select>
          </div>
          <div ref="versionChartRef" class="h-72" />
        </el-card>
      </re-col>

      <re-col
        v-motion
        class="mb-4.5"
        :value="12"
        :xs="24"
        :initial="{ opacity: 0, y: 100 }"
        :enter="{ opacity: 1, y: 0, transition: { delay: 640 } }"
      >
        <el-card shadow="never">
          <div class="flex items-center justify-between mb-4">
            <div class="text-base font-medium">每日测试里程</div>
            <el-select
              v-model="selectedProject"
              placeholder="全部项目"
              clearable
              style="width: 150px"
            >
              <el-option
                v-for="item in projectOptions"
                :key="item"
                :label="item"
                :value="item"
              />
            </el-select>
          </div>
          <div ref="dailyMileageChartRef" class="h-72" />
        </el-card>
      </re-col>
    </el-row>
  </div>
</template>

<style lang="scss" scoped>
:deep(.el-card) {
  --el-card-border-color: none;

  .el-scrollbar__bar {
    display: none;
  }

  .el-timeline-item {
    margin: 0 6px;
  }
}

:deep(.el-timeline.is-start) {
  padding-left: 0;
}

.main-content {
  margin: 20px 20px 0 !important;
}
</style>

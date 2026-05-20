<template>
  <div class="statistics-chart" v-if="hasData">
    <div class="chart-header">
      <h3>{{ title }}</h3>
      <button class="btn-refresh" @click="emit('refresh')">
        <i class="fas fa-sync-alt"></i>
      </button>
    </div>
    
    <div class="chart-container">
      <div class="stats-cards">
        <div class="stat-card total">
          <div class="stat-value">{{ data.total }}</div>
          <div class="stat-label">总计</div>
        </div>
        <div 
          v-for="item in chartData" 
          :key="item.name"
          class="stat-card"
          :style="{ borderColor: item.color }"
        >
          <div class="stat-value" :style="{ color: item.color }">
            {{ item.value }}
          </div>
          <div class="stat-label">{{ item.label }}</div>
        </div>
      </div>
      
      <div class="chart-wrapper" ref="chartRef">
        <VChart 
          v-if="chartRef"
          :option="chartOption" 
          :style="{ height: '300px', width: '100%' }"
          autoresize
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent
} from 'echarts/components'

use([
  CanvasRenderer,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent
])

const props = defineProps({
  data: {
    type: Object,
    required: true
  },
  type: {
    type: String,
    default: 'vehicle'
  }
})

const emit = defineEmits(['refresh'])

const chartRef = ref(null)

const hasData = computed(() => {
  return props.data.total > 0
})

const title = computed(() => {
  return props.type === 'vehicle' ? '车辆状态统计' : '借用记录统计'
})

const chartData = computed(() => {
  if (props.type === 'vehicle') {
    return [
      { name: 'available', label: '可用', value: props.data.available || 0, color: '#10B981' },
      { name: 'borrowed', label: '已借用', value: props.data.borrowed || 0, color: '#F59E0B' },
      { name: 'maintenance', label: '维修中', value: props.data.maintenance || 0, color: '#EF4444' }
    ]
  } else {
    return [
      { name: 'active', label: '进行中', value: props.data.active || 0, color: '#10B981' },
      { name: 'returned', label: '已归还', value: props.data.returned || 0, color: '#4F46E5' },
      { name: 'cancelled', label: '已取消', value: props.data.cancelled || 0, color: '#EF4444' }
    ]
  }
})

const chartOption = computed(() => {
  const data = chartData.value.filter(item => item.value > 0)
  
  // 如果没有数据，返回空配置
  if (data.length === 0) {
    return {
      title: {
        text: '暂无数据',
        left: 'center',
        top: 'center'
      }
    }
  }
  
  return {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'horizontal',
      bottom: 0,
      left: 'center'
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{d}%'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold'
          }
        },
        data: data.map(item => ({
          name: item.label,
          value: item.value,
          itemStyle: { color: item.color }
        }))
      }
    ]
  }
})

onMounted(() => {
  chartRef.value = true
})
</script>

<style scoped>
.statistics-chart {
  background: white;
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.chart-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.btn-refresh {
  width: 2rem;
  height: 2rem;
  border: none;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.btn-refresh:hover {
  background: var(--primary-color);
  color: white;
}

.chart-container {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 2rem;
}

.stats-cards {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.stat-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  padding: 1rem;
  text-align: center;
  border-left: 4px solid transparent;
}

.stat-card.total {
  border-left-color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.chart-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

@media (max-width: 768px) {
  .chart-container {
    grid-template-columns: 1fr;
  }
}
</style>
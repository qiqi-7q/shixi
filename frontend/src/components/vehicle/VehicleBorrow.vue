<template>
  <div class="vehicle-borrow">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>车辆借用记录管理</h2>
      <button class="btn-primary" @click="handleAdd">
        <i class="fas fa-plus"></i>
        新增借用
      </button>
    </div>
    
    <!-- 统计图表 -->
    <div class="stats-section">
      <StatisticsChart 
        :data="borrowStore.stats" 
        type="borrow"
        @refresh="refreshStats"
      />
    </div>
    
    <!-- 搜索栏 -->
    <div class="search-section">
      <SearchBar 
        :fields="searchFields"
        @search="handleSearch"
        @reset="handleReset"
      />
    </div>
    
    <!-- 借用记录列表 -->
    <div class="table-section">
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>车辆编号</th>
              <th>车型</th>
              <th>VIN号</th>
              <th>借用时间</th>
              <th>归还时间</th>
              <th>借用人</th>
              <th>司机姓名</th>
              <th>任务内容</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in borrowStore.records" :key="record.id">
              <td>{{ record.vehicle_code }}</td>
              <td>{{ record.model }}</td>
              <td>{{ record.vin }}</td>
              <td>{{ formatDateTime(record.borrow_time) }}</td>
              <td>{{ formatDateTime(record.return_time) }}</td>
              <td>{{ record.borrower }}</td>
              <td>{{ record.driver_name || '-' }}</td>
              <td>{{ record.task_content || '-' }}</td>
              <td>
                <span :class="['status-badge', record.status]">
                  {{ getStatusText(record.status) }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button 
                    v-if="record.status === 'active'"
                    class="btn-icon success" 
                    @click="handleReturn(record)" 
                    title="归还"
                  >
                    <i class="fas fa-undo-alt"></i>
                  </button>
                  <button 
                    v-if="record.status === 'active'"
                    class="btn-icon warning" 
                    @click="handleCancel(record)" 
                    title="取消"
                  >
                    <i class="fas fa-ban"></i>
                  </button>
                  <button class="btn-icon" @click="handleView(record)" title="查看">
                    <i class="fas fa-eye"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- 表单对话框 -->
    <BorrowFormDialog
      v-model:visible="dialogVisible"
      :record="currentRecord"
      :mode="dialogMode"
      @success="handleSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useBorrowStore } from '../../stores/borrow'
import { useToast } from '../../composables/useToast'
import StatisticsChart from './StatisticsChart.vue'
import SearchBar from '../common/SearchBar.vue'
import BorrowFormDialog from './BorrowFormDialog.vue'
import dayjs from 'dayjs'

const borrowStore = useBorrowStore()
const toast = useToast()

const dialogVisible = ref(false)
const dialogMode = ref('add')
const currentRecord = ref(null)

const searchFields = [
  { name: 'vehicle_code', label: '车辆编号', type: 'text' },
  { name: 'borrower', label: '借用人', type: 'text' },
  { 
    name: 'status', 
    label: '状态', 
    type: 'select',
    options: [
      { value: '', label: '全部' },
      { value: 'active', label: '进行中' },
      { value: 'returned', label: '已归还' },
      { value: 'cancelled', label: '已取消' }
    ]
  }
]

const searchParams = ref({})

const getStatusText = (status) => {
  const map = {
    active: '进行中',
    returned: '已归还',
    cancelled: '已取消'
  }
  return map[status] || status
}

const formatDateTime = (date) => {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm') : '-'
}

const handleAdd = () => {
  dialogMode.value = 'add'
  currentRecord.value = null
  dialogVisible.value = true
}

const handleView = (record) => {
  dialogMode.value = 'view'
  currentRecord.value = record
  dialogVisible.value = true
}

const handleReturn = async (record) => {
  if (confirm(`确定要归还车辆 ${record.vehicle_code} 吗？`)) {
    try {
      await borrowStore.returnVehicle(record.id)
      toast.success('归还成功')
    } catch (error) {
      toast.error('归还失败：' + error.message)
    }
  }
}

const handleCancel = async (record) => {
  if (confirm(`确定要取消借用记录吗？`)) {
    try {
      await borrowStore.cancelBorrow(record.id)
      toast.success('取消成功')
    } catch (error) {
      toast.error('取消失败：' + error.message)
    }
  }
}

const handleSearch = (params) => {
  searchParams.value = params
  borrowStore.fetchBorrowRecords(params)
}

const handleReset = () => {
  searchParams.value = {}
  borrowStore.fetchBorrowRecords()
}

const handleSuccess = () => {
  dialogVisible.value = false
  borrowStore.fetchBorrowRecords(searchParams.value)
}

const refreshStats = () => {
  borrowStore.fetchStats()
}

onMounted(() => {
  borrowStore.fetchBorrowRecords()
})
</script>

<style scoped>
.vehicle-borrow {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.page-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
}

.btn-primary {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 0.625rem 1.25rem;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s;
}

.btn-primary:hover {
  background: var(--primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.stats-section {
  margin-bottom: 1.5rem;
}

.search-section {
  background: white;
  padding: 1.5rem;
  border-radius: var(--radius-lg);
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow-sm);
}

.table-section {
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table thead {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.data-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--text-secondary);
  white-space: nowrap;
}

.data-table td {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  font-size: 0.875rem;
}

.data-table tbody tr:hover {
  background: var(--bg-secondary);
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.active {
  background: #D1FAE5;
  color: #065F46;
}

.status-badge.returned {
  background: #DBEAFE;
  color: #1E40AF;
}

.status-badge.cancelled {
  background: #FEE2E2;
  color: #991B1B;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  width: 2rem;
  height: 2rem;
  border: none;
  background: none;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.btn-icon:hover {
  background: var(--bg-secondary);
  color: var(--primary-color);
}

.btn-icon.success:hover {
  background: #D1FAE5;
  color: var(--secondary-color);
}

.btn-icon.warning:hover {
  background: #FEF3C7;
  color: var(--warning-color);
}
</style>
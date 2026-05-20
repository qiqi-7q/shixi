<template>
  <div class="vehicle-resource">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>车辆资源管理</h2>
      <button class="btn-primary" @click="handleAdd">
        <i class="fas fa-plus"></i>
        新增车辆
      </button>
    </div>
    
    <!-- 统计图表 -->
    <div class="stats-section">
      <StatisticsChart 
        :data="vehicleStore.stats" 
        type="vehicle"
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
    
    <!-- 车辆列表 -->
    <div class="table-section">
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>车辆编号</th>
              <th>VIN号</th>
              <th>车型</th>
              <th>车牌号</th>
              <th>车主姓名</th>
              <th>停放位置</th>
              <th>状态</th>
              <th>临牌到期</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="vehicle in vehicleStore.vehicles" :key="vehicle.id">
              <td>{{ vehicle.vehicle_code }}</td>
              <td>{{ vehicle.vin }}</td>
              <td>{{ vehicle.model }}</td>
              <td>{{ vehicle.plate_number || '-' }}</td>
              <td>{{ vehicle.owner_name || '-' }}</td>
              <td>{{ vehicle.parking_location || '-' }}</td>
              <td>
                <span :class="['status-badge', vehicle.status]">
                  {{ getStatusText(vehicle.status) }}
                </span>
              </td>
              <td>{{ formatDate(vehicle.temp_plate_expire_date) }}</td>
              <td>
                <div class="action-buttons">
                  <button class="btn-icon" @click="handleView(vehicle)" title="查看">
                    <i class="fas fa-eye"></i>
                  </button>
                  <button class="btn-icon" @click="handleEdit(vehicle)" title="编辑">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button class="btn-icon danger" @click="handleDelete(vehicle)" title="删除">
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- 表单对话框 -->
    <VehicleFormDialog
      v-model:visible="dialogVisible"
      :vehicle="currentVehicle"
      :mode="dialogMode"
      @success="handleSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useVehicleStore } from '../../stores/vehicle'
import { useToast } from '../../composables/useToast'
import StatisticsChart from './StatisticsChart.vue'
import SearchBar from '../common/SearchBar.vue'
import VehicleFormDialog from './VehicleFormDialog.vue'
import dayjs from 'dayjs'

const vehicleStore = useVehicleStore()
const toast = useToast()

const dialogVisible = ref(false)
const dialogMode = ref('add')
const currentVehicle = ref(null)

const searchFields = [
  { name: 'vehicle_code', label: '车辆编号', type: 'text' },
  { name: 'vin', label: 'VIN号', type: 'text' },
  { name: 'model', label: '车型', type: 'text' },
  { 
    name: 'status', 
    label: '状态', 
    type: 'select',
    options: [
      { value: '', label: '全部' },
      { value: 'available', label: '可用' },
      { value: 'borrowed', label: '已借用' },
      { value: 'maintenance', label: '维修中' }
    ]
  }
]

const searchParams = ref({})

const getStatusText = (status) => {
  const map = {
    available: '可用',
    borrowed: '已借用',
    maintenance: '维修中'
  }
  return map[status] || status
}

const formatDate = (date) => {
  return date ? dayjs(date).format('YYYY-MM-DD') : '-'
}

const handleAdd = () => {
  dialogMode.value = 'add'
  currentVehicle.value = null
  dialogVisible.value = true
}

const handleView = (vehicle) => {
  dialogMode.value = 'view'
  currentVehicle.value = vehicle
  dialogVisible.value = true
}

const handleEdit = (vehicle) => {
  dialogMode.value = 'edit'
  currentVehicle.value = vehicle
  dialogVisible.value = true
}

const handleDelete = async (vehicle) => {
  if (confirm(`确定要删除车辆 ${vehicle.vehicle_code} 吗？`)) {
    try {
      await vehicleStore.deleteVehicle(vehicle.id)
      toast.success('删除成功')
    } catch (error) {
      toast.error('删除失败：' + error.message)
    }
  }
}

const handleSearch = (params) => {
  searchParams.value = params
  vehicleStore.fetchVehicles(params)
}

const handleReset = () => {
  searchParams.value = {}
  vehicleStore.fetchVehicles()
}

const handleSuccess = () => {
  dialogVisible.value = false
  vehicleStore.fetchVehicles(searchParams.value)
}

const refreshStats = () => {
  vehicleStore.fetchStats()
}

onMounted(() => {
  vehicleStore.fetchVehicles()
})
</script>

<style scoped>
.vehicle-resource {
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

.status-badge.available {
  background: #D1FAE5;
  color: #065F46;
}

.status-badge.borrowed {
  background: #FEF3C7;
  color: #92400E;
}

.status-badge.maintenance {
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

.btn-icon.danger:hover {
  background: #FEE2E2;
  color: var(--danger-color);
}
</style>
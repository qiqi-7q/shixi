<template>
  <div v-if="visible" class="dialog-overlay" @click="handleClose">
    <div class="dialog" @click.stop>
      <div class="dialog-header">
        <h3>{{ title }}</h3>
        <button class="btn-close" @click="handleClose">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <div class="dialog-body">
        <form @submit.prevent="handleSubmit">
          <div class="form-grid">
            <div class="form-group">
              <label>车辆 <span class="required">*</span></label>
              <select 
                v-model="form.vehicle_id"
                :disabled="mode === 'view'"
                required
              >
                <option value="">请选择车辆</option>
                <option 
                  v-for="vehicle in availableVehicles" 
                  :key="vehicle.id"
                  :value="vehicle.id"
                >
                  {{ vehicle.vehicle_code }} - {{ vehicle.model }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label>借用时间 <span class="required">*</span></label>
              <input 
                v-model="form.borrow_time"
                type="datetime-local"
                :disabled="mode === 'view'"
                required
              />
            </div>
            
            <div class="form-group">
              <label>预计归还时间</label>
              <input 
                v-model="form.return_time"
                type="datetime-local"
                :disabled="mode === 'view'"
              />
            </div>
            
            <div class="form-group">
              <label>借用人 <span class="required">*</span></label>
              <input 
                v-model="form.borrower"
                type="text"
                :disabled="mode === 'view'"
                required
              />
            </div>
            
            <div class="form-group">
              <label>司机姓名</label>
              <input 
                v-model="form.driver_name"
                type="text"
                :disabled="mode === 'view'"
              />
            </div>
            
            <div class="form-group full-width">
              <label>任务内容</label>
              <textarea 
                v-model="form.task_content"
                :disabled="mode === 'view'"
                rows="3"
              ></textarea>
            </div>
            
            <div class="form-group full-width">
              <label>备注</label>
              <textarea 
                v-model="form.remarks"
                :disabled="mode === 'view'"
                rows="2"
              ></textarea>
            </div>
          </div>
        </form>
      </div>
      
      <div class="dialog-footer">
        <button class="btn-cancel" @click="handleClose">
          {{ mode === 'view' ? '关闭' : '取消' }}
        </button>
        <button 
          v-if="mode !== 'view'"
          class="btn-submit" 
          @click="handleSubmit"
          :disabled="loading"
        >
          {{ loading ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useBorrowStore } from '../../stores/borrow'
import { useVehicleStore } from '../../stores/vehicle'
import { useToast } from '../../composables/useToast'
import dayjs from 'dayjs'

// 定义 props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  record: {
    type: Object,
    default: null
  },
  mode: {
    type: String,
    default: 'add'
  }
})

// 定义 emits
const emit = defineEmits(['update:visible', 'success'])

const borrowStore = useBorrowStore()
const vehicleStore = useVehicleStore()
const toast = useToast()

const loading = ref(false)

// 初始化表单数据
const initFormData = () => ({
  vehicle_id: '',
  borrow_time: dayjs().format('YYYY-MM-DDTHH:mm'),
  return_time: '',
  borrower: '',
  driver_name: '',
  task_content: '',
  remarks: ''
})

const form = ref(initFormData())

const availableVehicles = computed(() => {
  return vehicleStore.vehicles.filter(v => v.status === 'available')
})

const title = computed(() => {
  const map = {
    add: '新增借用记录',
    view: '查看借用记录'
  }
  return map[props.mode] || '借用记录'
})

// 定义 resetForm 函数
const resetForm = () => {
  form.value = initFormData()
}

// 监听 record 变化
watch(() => props.record, (newVal) => {
  if (newVal) {
    form.value = { 
      ...initFormData(),
      ...newVal 
    }
    if (form.value.borrow_time) {
      form.value.borrow_time = dayjs(form.value.borrow_time).format('YYYY-MM-DDTHH:mm')
    }
    if (form.value.return_time) {
      form.value.return_time = dayjs(form.value.return_time).format('YYYY-MM-DDTHH:mm')
    }
  } else {
    resetForm()
  }
}, { immediate: true })

const handleClose = () => {
  emit('update:visible', false)
  resetForm()
}

const handleSubmit = async () => {
  if (!form.value.vehicle_id) {
    toast.error('请选择车辆')
    return
  }
  if (!form.value.borrow_time) {
    toast.error('请选择借用时间')
    return
  }
  if (!form.value.borrower) {
    toast.error('请输入借用人')
    return
  }
  
  loading.value = true
  
  try {
    await borrowStore.createBorrowRecord(form.value)
    toast.success('创建成功')
    emit('success')
    handleClose()
  } catch (error) {
    toast.error('操作失败：' + error.message)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (vehicleStore.vehicles.length === 0) {
    vehicleStore.fetchVehicles()
  }
})
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.dialog {
  background: white;
  border-radius: var(--radius-lg);
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-xl);
}

.dialog-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.dialog-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.btn-close {
  width: 2rem;
  height: 2rem;
  border: none;
  background: none;
  border-radius: var(--radius-md);
  color: var(--text-light);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.btn-close:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.dialog-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.form-group.full-width {
  grid-column: span 2;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
}

.required {
  color: var(--danger-color);
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.625rem 0.875rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  transition: all 0.3s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1);
}

.form-group input:disabled,
.form-group select:disabled,
.form-group textarea:disabled {
  background: var(--bg-secondary);
  color: var(--text-secondary);
  cursor: not-allowed;
}

.dialog-footer {
  padding: 1.5rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-cancel,
.btn-submit {
  padding: 0.625rem 1.5rem;
  border: none;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-cancel {
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.btn-cancel:hover {
  background: var(--border-color);
}

.btn-submit {
  background: var(--primary-color);
  color: white;
}

.btn-submit:hover:not(:disabled) {
  background: var(--primary-dark);
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>
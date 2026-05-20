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
              <label>车辆编号 <span class="required">*</span></label>
              <input 
                v-model="form.vehicle_code"
                type="text"
                :disabled="mode === 'view'"
                required
                maxlength="50"
              />
            </div>
            
            <div class="form-group">
              <label>VIN号 <span class="required">*</span></label>
              <input 
                v-model="form.vin"
                type="text"
                :disabled="mode === 'view'"
                required
                maxlength="17"
              />
            </div>
            
            <div class="form-group">
              <label>车型 <span class="required">*</span></label>
              <input 
                v-model="form.model"
                type="text"
                :disabled="mode === 'view'"
                required
              />
            </div>
            
            <div class="form-group">
              <label>车辆配置</label>
              <input 
                v-model="form.configuration"
                type="text"
                :disabled="mode === 'view'"
              />
            </div>
            
            <div class="form-group">
              <label>车牌号</label>
              <input 
                v-model="form.plate_number"
                type="text"
                :disabled="mode === 'view'"
              />
            </div>
            
            <div class="form-group">
              <label>临牌到期时间</label>
              <input 
                v-model="form.temp_plate_expire_date"
                type="date"
                :disabled="mode === 'view'"
              />
            </div>
            
            <div class="form-group">
              <label>车主姓名</label>
              <input 
                v-model="form.owner_name"
                type="text"
                :disabled="mode === 'view'"
              />
            </div>
            
            <div class="form-group">
              <label>停放位置</label>
              <input 
                v-model="form.parking_location"
                type="text"
                :disabled="mode === 'view'"
              />
            </div>
            
            <div class="form-group">
              <label>临牌办理次数</label>
              <input 
                v-model.number="form.temp_plate_count"
                type="number"
                :disabled="mode === 'view'"
                min="0"
              />
            </div>
            
            <div class="form-group">
              <label>状态</label>
              <select v-model="form.status" :disabled="mode === 'view'">
                <option value="available">可用</option>
                <option value="borrowed">已借用</option>
                <option value="maintenance">维修中</option>
              </select>
            </div>
            
            <div class="form-group full-width">
              <label>备注</label>
              <textarea 
                v-model="form.remarks"
                :disabled="mode === 'view'"
                rows="3"
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
import { ref, computed, watch } from 'vue'
import { useVehicleStore } from '../../stores/vehicle'
import { useToast } from '../../composables/useToast'

// 定义 props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  vehicle: {
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

const vehicleStore = useVehicleStore()
const toast = useToast()

const loading = ref(false)

// 初始化表单数据
const initFormData = () => ({
  vehicle_code: '',
  vin: '',
  model: '',
  configuration: '',
  plate_number: '',
  temp_plate_expire_date: '',
  owner_name: '',
  parking_location: '',
  temp_plate_count: 0,
  status: 'available',
  remarks: ''
})

const form = ref(initFormData())

const title = computed(() => {
  const map = {
    add: '新增车辆',
    edit: '编辑车辆',
    view: '查看车辆'
  }
  return map[props.mode] || '车辆信息'
})

// 定义 resetForm 函数
const resetForm = () => {
  form.value = initFormData()
}

// 监听 vehicle 变化
watch(() => props.vehicle, (newVal) => {
  if (newVal) {
    form.value = { 
      ...initFormData(),
      ...newVal 
    }
    if (form.value.temp_plate_expire_date) {
      form.value.temp_plate_expire_date = form.value.temp_plate_expire_date.split('T')[0]
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
  // 表单验证
  if (!form.value.vehicle_code) {
    toast.error('请输入车辆编号')
    return
  }
  if (!form.value.vin) {
    toast.error('请输入VIN号')
    return
  }
  if (!form.value.model) {
    toast.error('请输入车型')
    return
  }

  loading.value = true
  
  try {
    if (props.mode === 'add') {
      await vehicleStore.createVehicle(form.value)
      toast.success('创建成功')
    } else if (props.mode === 'edit') {
      await vehicleStore.updateVehicle(props.vehicle.id, form.value)
      toast.success('更新成功')
    }
    
    emit('success')
    handleClose()
  } catch (error) {
    toast.error('操作失败：' + error.message)
  } finally {
    loading.value = false
  }
}
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
  max-width: 700px;
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
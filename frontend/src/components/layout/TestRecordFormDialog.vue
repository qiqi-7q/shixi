<template>
  <div class="test_record-form-dialog">
    <h3 class="dialog-title">{{ isEdit ? '编辑测试记录' : '新增测试记录' }}</h3>

    <form @submit.prevent="handleSubmit">
      <!-- 基础字段 -->
      <div class="form-grid">
        <div class="form-item">
          <label>项目 <span class="required">*</span></label>
          <input
            v-model="form.project"
            type="text"
            placeholder="请输入项目名称"
            required
          >
        </div>
        <div class="form-item">
          <label>车型 <span class="required">*</span></label>
          <input
            v-model="form.car_model"
            type="text"
            placeholder="请输入车型"
            required
          >
        </div>
        <div class="form-item">
          <label>功能模式</label>
          <input v-model="form.func_mode" type="text" placeholder="请输入功能模式">
        </div>
        <div class="form-item">
          <label>问题分类</label>
          <input v-model="form.problem_category" type="text" placeholder="请输入问题分类">
        </div>
        <div class="form-item">
          <label>接管类型</label>
          <input v-model="form.take_over_type" type="text" placeholder="请输入接管类型">
        </div>
        <div class="form-item">
          <label>车辆VIN号 <span class="required">*</span></label>
          <input
            v-model="form.car_vin"
            type="text"
            placeholder="请输入VIN号"
            required
          >
        </div>
        <div class="form-item">
          <label>问题时间 <span class="required">*</span></label>
          <input
            v-model="form.problem_time"
            type="datetime-local"
            required
          >
        </div>
        <div class="form-item">
          <label>软件版本</label>
          <input v-model="form.software_version" type="text" placeholder="请输入软件版本">
        </div>
        <div class="form-item">
          <label>数据链接</label>
          <input v-model="form.data_link" type="url" placeholder="请输入数据链接">
        </div>
        <div class="form-item">
          <label>Wetrack链接</label>
          <input v-model="form.wetrack_link" type="url" placeholder="请输入Wetrack链接">
        </div>
        <div class="form-item">
          <label>分析人员</label>
          <input v-model="form.analysis_person" type="text" placeholder="请输入分析人员">
        </div>
        <div class="form-item">
          <label>分析附件</label>
          <input v-model="form.analysis_attachment" type="text" placeholder="请输入附件链接">
        </div>
      </div>

      <!-- 文本域字段 -->
      <div class="form-textarea">
        <div class="form-item full-width">
          <label>问题描述</label>
          <textarea
            v-model="form.problem_desc"
            rows="3"
            placeholder="请输入问题描述"
          ></textarea>
        </div>
        <div class="form-item full-width">
          <label>问题现象</label>
          <textarea
            v-model="form.problem_phenomenon"
            rows="3"
            placeholder="请输入问题现象"
          ></textarea>
        </div>
        <div class="form-item full-width">
          <label>分析结果</label>
          <textarea
            v-model="form.analysis_result"
            rows="3"
            placeholder="请输入分析结果"
          ></textarea>
        </div>
        <div class="form-item full-width">
          <label>备注</label>
          <textarea
            v-model="form.remark"
            rows="2"
            placeholder="请输入备注信息"
          ></textarea>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="form-actions">
        <button type="button" class="btn btn-secondary" @click="onCancel">取消</button>
        <button type="submit" class="btn btn-primary">保存</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, watch, defineProps, defineEmits } from 'vue'
import { useTestRecordStore } from '../../stores/testRecord'

// 接收外部参数
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  editData: {
    type: Object,
    default: () => ({})
  }
})

// 触发外部事件
const emit = defineEmits(['close', 'save'])

const testRecordStore = useTestRecordStore()

// 表单数据
const form = reactive({
  id: null,
  project: '',
  car_model: '',
  func_mode: '',
  problem_desc: '',
  problem_category: '',
  problem_phenomenon: '',
  take_over_type: '',
  problem_time: '',
  car_vin: '',
  data_link: '',
  wetrack_link: '',
  analysis_result: '',
  analysis_person: '',
  analysis_attachment: '',
  software_version: '',
  remark: '',
  custom_fields: {}
})

// 是否为编辑模式
const isEdit = ref(false)

// 自定义字段列表
const customFields = ref([])

// 初始化表单
const initForm = () => {
  // 重置表单
  Object.keys(form).forEach(key => {
    if (key === 'custom_fields') {
      form[key] = {}
    } else {
      form[key] = ''
    }
  })



  // 如果是编辑，填充数据
  if (Object.keys(props.editData).length > 0) {
    isEdit.value = true
    Object.assign(form, props.editData)
    // 处理自定义字段默认值
    if (!form.custom_fields) form.custom_fields = {}
    // 处理时间格式
    if (form.problem_time) {
      form.problem_time = new Date(form.problem_time).toISOString().slice(0, 16)
    }
  } else {
    isEdit.value = false
  }
}

// 监听弹窗显示状态
watch(() => props.visible, (newVal) => {
  if (newVal) {
    initForm()
  }
}, { immediate: true })

// 提交表单
const handleSubmit = async () => {
  const success = await testRecordStore.saveTestRecordData({ ...form })
  if (success) {
    emit('save')
    emit('close')
  }
}

// 取消
const onCancel = () => {
  emit('close')
}
</script>

<style scoped>
.test_record-form-dialog {
  padding: 20px;
}

.dialog-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.form-textarea {
  margin-bottom: 20px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-item.full-width {
  grid-column: 1 / -1;
}

.form-item label {
  font-size: 14px;
  color: #333;
}

.required {
  color: #ff4d4f;
}

.form-item input,
.form-item textarea {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-item textarea {
  resize: vertical;
}

.custom-fields {
  margin: 20px 0;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 4px;
}

.custom-fields h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #666;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-secondary {
  background: #f0f0f0;
  color: #333;
}

.btn-primary {
  background: #1890ff;
  color: white;
}
</style>
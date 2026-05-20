// src/api/testRecord.js 完整正确代码
import api from './auth'

// 所有方法封装在 testRecordAPI 对象中（和 vehicleAPI 完全一致）
export const testRecordAPI = {
  // 获取测试记录列表（分页+搜索）
  getTestRecords: async (params = {}) => {
    const response = await api.get('/test_record/', { params })
    return response.data
  },
  // 获取车辆列表
//  getTestRecords: async (params = {}) => {
//    const response = await api.get('/test_record/', { params })
//    return response.data
//  },

  // 获取单个测试记录
  getTestRecord: async (id) => {
    const response = await api.get(`/test_record/${id}`)
    return response.data
  },

  // 创建测试记录（新增）
  createTestRecord: async (data) => {
    const response = await api.post('/test_record/save', data)
    return response.data
  },

  // 更新测试记录（编辑）
  updateTestRecord: async (id, data) => {
    const postData = { ...data, id }
    const response = await api.post('/test_record/save', postData)
    return response.data
  },

  // 删除测试记录
  deleteTestRecord: async (id) => {
    const response = await api.delete(`/test_record/delete/${id}`)
    return response.data
  }

}


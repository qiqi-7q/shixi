import api from './auth'

export const borrowAPI = {
  // 获取借用记录列表
  getBorrowRecords: async (params = {}) => {
    const response = await api.get('/borrows/', { params })
    return response.data
  },
  
  // 获取单个借用记录
  getBorrowRecord: async (id) => {
    const response = await api.get(`/borrows/${id}`)
    return response.data
  },
  
  // 创建借用记录
  createBorrowRecord: async (data) => {
    const response = await api.post('/borrows/', data)
    return response.data
  },
  
  // 归还车辆
  returnVehicle: async (id) => {
    const response = await api.post(`/borrows/${id}/return`)
    return response.data
  },
  
  // 取消借用
  cancelBorrow: async (id) => {
    const response = await api.post(`/borrows/${id}/cancel`)
    return response.data
  },
  
  // 获取借用统计
  getBorrowStats: async () => {
    const response = await api.get('/borrows/')
    const records = response.data
    
    const stats = {
      total: records.length,
      active: records.filter(r => r.status === 'active').length,
      returned: records.filter(r => r.status === 'returned').length,
      cancelled: records.filter(r => r.status === 'cancelled').length
    }
    
    return stats
  }
}
import api from './auth'

export const vehicleAPI = {
  // 获取车辆列表
  getVehicles: async (params = {}) => {
    const response = await api.get('/vehicles/', { params })
    return response.data
  },
  
  // 获取单个车辆
  getVehicle: async (id) => {
    const response = await api.get(`/vehicles/${id}`)
    return response.data
  },
  
  // 创建车辆
  createVehicle: async (data) => {
    const response = await api.post('/vehicles/', data)
    return response.data
  },
  
  // 更新车辆
  updateVehicle: async (id, data) => {
    const response = await api.put(`/vehicles/${id}`, data)
    return response.data
  },
  
  // 删除车辆
  deleteVehicle: async (id) => {
    const response = await api.delete(`/vehicles/${id}`)
    return response.data
  },
  
  // 获取车辆统计
  getVehicleStats: async () => {
    const response = await api.get('/vehicles/')
    const vehicles = response.data
    
    // 计算统计数据
    const stats = {
      total: vehicles.length,
      available: vehicles.filter(v => v.status === 'available').length,
      borrowed: vehicles.filter(v => v.status === 'borrowed').length,
      maintenance: vehicles.filter(v => v.status === 'maintenance').length
    }
    
    return stats
  }
}
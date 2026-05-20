import { defineStore } from 'pinia'
import { testRecordAPI } from '../api/testRecord'
import { useToast } from '../composables/useToast'

const toast = useToast()

export const useTestRecordStore = defineStore('testRecord', {
  state: () => ({
    list: [],        // 测试记录列表
    total: 0,        // 总条数
    page: 1,         // 当前页
    size: 10,        // 每页条数
    keyword: '',     // 搜索关键词
    loading: false   // 加载状态
  }),

  actions: {
    // 获取测试记录列表
    async fetchTestRecordList() {
      this.loading = true
      try {
        toast.info('开始获取测试记录列表')
        const res = await testRecordAPI.getTestRecords({
          page: this.page,
          size: this.size,
          keyword: this.keyword
        })
        toast.info('开始获取0000000000000')
        this.list = res.data.list
        console.log(this.list, "color:red; font-size:16px");
        this.total = res.data.total
      } catch (error) {
        toast.error('获取测试记录失败：' + error.message)
      } finally {
        this.loading = false
      }
    },

    // 保存测试记录（新增/编辑）
    async saveTestRecordData(data) {
      try {
        await testRecordAPI.saveTestRecord(data)
        toast.success(data.id ? '编辑成功' : '新增成功')
        await this.fetchTestRecordList()
        return true
      } catch (error) {
        toast.error('保存失败：' + error.message)
        return false
      }
    },

    // 删除测试记录
    async deleteTestRecordData(id) {
      try {
        await testRecordAPI.deleteTestRecord(id)
        toast.success('删除成功')
        await this.fetchTestRecordList()
      } catch (error) {
        toast.error('删除失败：' + error.message)
      }
    },





    // 重置搜索条件
    resetSearch() {
      this.page = 1
      this.keyword = ''
    }
  }
})
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      // API 代理配置
      '/auth': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/vehicles': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        // 正确使用 bypass：返回 false 或 undefined 继续代理，返回其他值则返回该值
        bypass: (req) => {
          // 只有精确匹配 API 路径才代理
          // /vehicles 或 /vehicles/ 或 /vehicles?xxx
          const url = req.url
          console.log('Proxying request:', url)
          
          // 如果是 API 路径，继续代理（返回 undefined）
          if (url === '/vehicles' || url === '/vehicles/' || url.startsWith('/vehicles?')) {
            return undefined
          }
          // 如果是带数字 ID 的路径，继续代理
          if (/^\/vehicles\/\d+/.test(url)) {
            return undefined
          }
          
          // 否则不代理，返回 index.html
          console.log('Bypass proxy, return index.html for:', url)
          return '/index.html'
        }
      },
      '/borrows': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        bypass: (req) => {
          const url = req.url
          
          if (url === '/borrows' || url === '/borrows/' || url.startsWith('/borrows?')) {
            return undefined
          }
          if (/^\/borrows\/\d+/.test(url)) {
            return undefined
          }
          
          return '/index.html'
        }
      },

      '/test_record': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        bypass: (req) => {
          const url = req.url

          if (url === '/tests_record' || url === '/test-record/' || url.startsWith('/test?')) {
            return undefined
          }
          if (/^\/test_record\/\d+/.test(url)) {
            return undefined
          }

          return '/index.html'
        }
      }

    }
  }
})
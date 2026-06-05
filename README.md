[点我查看 vue-pure-admin 文档](https://pure-admin.cn/)  
[点我查看 @pureadmin/utils 文档](https://pure-admin-utils.netlify.app)
目录结构架构
├── src/
│   ├── api/              # API 接口（routes、user）
│   ├── assets/           # 静态资源（SVG、图片、iconfont）
│   ├── components/       # 全局可复用组件
│   │   ├── ReAuth/       # 按钮级权限认证组件 (TSX)
│   │   ├── RePerms/      # 按钮级权限控制组件 (TSX)
│   │   ├── ReDialog/     # 全局对话框组件
│   │   ├── ReIcon/       # 图标渲染（在线/离线/iconfont三合一）
│   │   ├── RePureTableBar/ # 表格工具栏
│   │   ├── ReSegmented/  # 分段控制器 (TSX)
│   │   └── ReText/       # 文本溢出省略组件
│   ├── config/           # 运行时动态配置（从 platform-config.json 加载）
│   ├── directives/       # 自定义指令（权限、复制、长按、水波纹、拖拽优化）
│   ├── layout/           # 布局系统
│   │   ├── components/
│   │   │   ├── lay-sidebar/   # 侧边栏（垂直/水平/混合三种模式）
│   │   │   ├── lay-navbar/    # 导航栏
│   │   │   ├── lay-content/   # 内容主区域
│   │   │   ├── lay-tag/       # 多标签页（Chrome 风格）
│   │   │   ├── lay-search/    # 全局搜索（带历史记录）
│   │   │   ├── lay-notice/    # 通知中心
│   │   │   ├── lay-setting/   # 系统设置面板
│   │   │   ├── lay-frame/     # 内嵌 iframe
│   │   │   └── lay-footer/    # 页脚
│   │   ├── hooks/             # 布局相关 hooks
│   │   └── frame.vue / redirect.vue
│   ├── router/           # 路由（自动扫描 modules/、动态路由）
│   ├── store/            # Pinia 状态管理
│   │   └── modules/      # app、user、permission、settings、multiTags、epTheme
│   ├── style/            # 样式（SCSS + Tailwind + 暗色模式）
│   ├── utils/            # 工具库
│   │   ├── http/         # Axios 封装
│   │   ├── localforage/  # IndexedDB 存储
│   │   └── auth.ts / mitt.ts / tree.ts / progress.ts ...
│   └── views/            # 页面视图
│       ├── login/        # 登录页
│       ├── error/        # 403/404/500
│       ├── permission/   # 权限示例页（按钮级 + 页面级）
│       └── welcome/      # 欢迎页
├── build/                # Vite 构建配置（CDN、压缩、插件、优化）
├── mock/                 # Mock 服务（登录、异步路由、刷新Token）
├── public/               # 静态文件（favicon、platform-config.json）
└── types/                # 全局类型声明
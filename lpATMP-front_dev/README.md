# LPATMOTOR 前端

基于 Vue 3 + TypeScript + Vite 的自动驾驶测试管理平台前端项目。

## 技术栈

| 类别 | 技术 |
| --- | --- |
| 框架 | Vue 3.5 |
| 语言 | TypeScript 5.9 |
| 构建工具 | Vite 7 |
| UI 组件库 | Element Plus 2.11 + Plus Pro Components |
| 状态管理 | Pinia 3 |
| 路由 | Vue Router 4 |
| 图表 | ECharts 6 |
| CSS | Tailwind CSS 4 + SCSS |
| HTTP | Axios |
| 包管理 | pnpm >= 9 |

## 环境要求

- **Node.js**: `^20.19.4 || >=22.13.0`（推荐 v22.20.0，见 `.nvmrc`）
- **pnpm**: `>= 9`

## 快速开始

### 1. 配置私有 npm 源

```bash
npm config set registry http://10.1.12.10:8081/repository/npm-webproxy/
npm config set strict-ssl false
```

### 2. 安装 pnpm

```bash
npm install --global pnpm
```

### 3. 切换 Node 版本（推荐 nvm）

```bash
nvm install
nvm use
```

### 4. 安装依赖

```bash
pnpm install
```

### 5. 启动开发服务器

```bash
pnpm dev
```

启动后访问 `http://localhost:8848`。

## 常用脚本

| 命令 | 说明 |
| --- | --- |
| `pnpm dev` | 启动开发服务器（端口 8848） |
| `pnpm build` | 生产环境构建（输出到 dist） |
| `pnpm build:staging` | 预发布环境构建 |
| `pnpm preview` | 预览构建产物 |
| `pnpm lint` | 运行 ESLint + Prettier + Stylelint |
| `pnpm typecheck` | TypeScript 类型检查 |
| `pnpm clean:cache` | 清除缓存并重新安装依赖 |

## 环境变量

项目使用 Vite 多环境配置，所有以 `VITE_` 开头的变量可通过 `import.meta.env` 在前端代码中访问。

| 变量名 | 说明 | 默认值 |
| --- | --- | --- |
| `VITE_PORT` | 开发服务器端口 | 8848 |
| `VITE_PUBLIC_PATH` | 公共路径前缀 | `/` |
| `VITE_ROUTER_HISTORY` | 路由模式（hash / h5） | hash |
| `VITE_PROXY_DOMAIN_REAL` | 后端接口地址（仅开发环境） | `http://10.192.183.118:8000` |
| `VITE_CDN` | 是否使用 CDN 替换本地库 | false |
| `VITE_COMPRESSION` | 压缩方式（gzip / brotli / none） | none |

环境文件对应关系：

| 文件 | 加载时机 |
| --- | --- |
| `.env` | 所有环境 |
| `.env.development` | `pnpm dev` |
| `.env.staging` | `pnpm build:staging` |
| `.env.production` | `pnpm build` |

## 项目结构

```
src/
├── api/          # 接口请求
├── assets/       # 静态资源
├── components/   # 通用组件
├── config/       # 全局配置
├── directives/   # 自定义指令
├── layout/       # 布局框架
├── plugins/      # 插件注册
├── router/       # 路由配置
├── store/        # Pinia 状态管理
├── style/        # 全局样式
├── utils/        # 工具函数
├── views/        # 页面视图
├── App.vue       # 根组件
└── main.ts       # 入口文件
```

## Docker 部署

```bash
docker build -t lpatmotor-frontend .
docker run -d -p 80:80 lpatmotor-frontend
```

Docker 构建流程：Node 20 Alpine 安装依赖并打包 → Nginx Alpine 部署静态资源，监听 80 端口。

> 若使用 H5 路由模式，Nginx 需额外配置 `try_files $uri $uri/ /index.html;`。
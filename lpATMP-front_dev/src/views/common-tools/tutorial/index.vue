<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { useRenderIcon } from "@/components/ReIcon/src/hooks";

defineOptions({
  name: "Tutorial"
});

const router = useRouter();

const showBackTop = ref(false);

const handleScroll = () => {
  showBackTop.value = window.scrollY > 400;
};

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: "smooth" });
};

const navigateTo = (path: string) => {
  router.push(path);
};

const scrollToSection = (id: string) => {
  const el = document.getElementById(id);
  if (el) {
    el.scrollIntoView({ behavior: "smooth", block: "start" });
  }
};

const tocItems = [
  { id: "overview", label: "系统概述" },
  { id: "quickstart", label: "快速开始" },
  { id: "home", label: "首页" },
  { id: "test", label: "测试管理" },
  { id: "record", label: "测试记录" },
  { id: "statistics", label: "统计分析" },
  { id: "tools", label: "常用工具" },
  { id: "faq", label: "常见问题" }
];

onMounted(() => {
  window.addEventListener("scroll", handleScroll);
});

onUnmounted(() => {
  window.removeEventListener("scroll", handleScroll);
});
</script>

<template>
  <div class="tutorial-wrap main main-conten">
    <main class="tutorial-body">
      <!-- 目录 -->
      <div class="toc-inline">
        <div class="toc-inline-title">教程导航</div>
        <div class="toc-inline-list">
          <span
            v-for="item in tocItems"
            :key="item.id"
            class="toc-inline-item"
            @click="scrollToSection(item.id)"
          >
            {{ item.label }}
          </span>
        </div>
      </div>

      <!-- ========== 系统概述 ========== -->
      <section id="overview" class="doc-section">
        <h2 class="sec-title">
          <el-icon class="sec-icon"
            ><component :is="useRenderIcon('ep/monitor')"
          /></el-icon>
          系统概述
        </h2>
        <p class="sec-desc">
          自动化管理平台（LPATMOTOR）是一套面向车辆测试场景的综合管理系统，集测试管理、数据记录、统计分析、权限控制于一体，帮助团队高效完成车辆测试全流程管理。
        </p>
        <div class="card-row">
          <div
            class="feature-card"
            @click="navigateTo('/test/vehicle/resource')"
          >
            <div class="card-icon blue">
              <el-icon size="28"
                ><component :is="useRenderIcon('ep/notebook')"
              /></el-icon>
            </div>
            <div class="card-text">
              <div class="card-label">测试管理</div>
              <div class="card-desc">车辆、路线、人员、里程</div>
            </div>
          </div>
          <div class="feature-card" @click="navigateTo('/test-record/nap')">
            <div class="card-icon green">
              <el-icon size="28"
                ><component :is="useRenderIcon('ep/document')"
              /></el-icon>
            </div>
            <div class="card-text">
              <div class="card-label">测试记录</div>
              <div class="card-desc">NAP / CNAP / LCC-ACC</div>
            </div>
          </div>
          <div class="feature-card" @click="navigateTo('/statistics/nap')">
            <div class="card-icon orange">
              <el-icon size="28"
                ><component :is="useRenderIcon('ep/data-analysis')"
              /></el-icon>
            </div>
            <div class="card-text">
              <div class="card-label">统计分析</div>
              <div class="card-desc">统计结果与里程图</div>
            </div>
          </div>
          <div class="feature-card" @click="navigateTo('/common-tools/tools')">
            <div class="card-icon purple">
              <el-icon size="28"
                ><component :is="useRenderIcon('ep/setting')"
              /></el-icon>
            </div>
            <div class="card-text">
              <div class="card-label">常用工具</div>
              <div class="card-desc">教程与常用应用</div>
            </div>
          </div>
        </div>
      </section>

      <!-- ========== 快速开始 ========== -->
      <section id="quickstart" class="doc-section">
        <h2 class="sec-title">
          <el-icon class="sec-icon"
            ><component :is="useRenderIcon('ep/promotion')"
          /></el-icon>
          快速开始
        </h2>
        <p class="sec-desc">简单四步，快速上手平台操作。</p>
        <div class="quick-steps">
          <div class="qs-item">
            <div class="qs-num">1</div>
            <div class="qs-body">
              <div class="qs-title">登录系统</div>
              <div class="qs-desc">注册账号和密码登录平台</div>
            </div>
          </div>
          <div class="qs-item">
            <div class="qs-num">2</div>
            <div class="qs-body">
              <div class="qs-title">查看首页仪表盘</div>
              <div class="qs-desc">
                登录后进入首页，查看车辆总数、任务状态、借出情况等关键指标和图表
              </div>
            </div>
          </div>
          <div class="qs-item">
            <div class="qs-num">3</div>
            <div class="qs-body">
              <div class="qs-title">浏览测试管理</div>
              <div class="qs-desc">
                进入「测试管理」查看车辆资源表、路线管理、测试里程等模块
              </div>
            </div>
          </div>
          <div class="qs-item">
            <div class="qs-num">4</div>
            <div class="qs-body">
              <div class="qs-title">创建测试记录</div>
              <div class="qs-desc">
                进入「测试记录」模块，新增 NAP / CNAP / LCC-ACC 测试数据
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ========== 首页 ========== -->
      <section id="home" class="doc-section">
        <h2 class="sec-title">
          <el-icon class="sec-icon"
            ><component :is="useRenderIcon('ep/home-filled')"
          /></el-icon>
          首页
        </h2>
        <p class="sec-desc">
          首页仪表盘展示平台核心数据概览，帮助您快速了解当前测试工作的整体状态。
        </p>

        <h3 class="sub-title">统计卡片</h3>
        <p class="sec-desc">页面顶部展示四个关键指标卡片：</p>
        <div class="step-list">
          <div class="step-item">
            <span class="step-dot">1</span><strong>车辆总数</strong> —
            平台登记的全部车辆，含可用车辆数
          </div>
          <div class="step-item">
            <span class="step-dot">2</span><strong>今日借出</strong> —
            当日借出的车辆数及当前借用中的车辆数
          </div>
          <div class="step-item">
            <span class="step-dot">3</span><strong>总记录数</strong> —
            所有测试记录总数
          </div>
        </div>

        <h3 class="sub-title">图表分析</h3>
        <p class="sec-desc">页面下方展示两个可视化图表：</p>
        <div class="step-list">
          <div class="step-item">
            <span class="step-dot">1</span><strong>版本里程</strong> —
            各版本的测试里程对比柱状图
          </div>
          <div class="step-item">
            <span class="step-dot">4</span><strong>每日测试里程</strong> —
            每日行驶里程统计趋势
          </div>
        </div>
        <el-alert type="success" :closable="false" show-icon class="doc-alert">
          图表支持鼠标悬停查看详细数据，部分图表支持点击交互进行项目筛选。
        </el-alert>
        <div class="screenshot-area">
          <el-image
            class="screenshot-img"
            src="/tutorial/home.png"
            fit="contain"
            :preview-src-list="['/tutorial/home.png']"
            preview-teleported
            lazy
          >
            <template #error>
              <div class="img-placeholder">
                <el-icon size="28"
                  ><component :is="useRenderIcon('ep/picture')"
                /></el-icon>
                <span>待补充截图</span>
              </div>
            </template>
          </el-image>
          <span class="img-caption">首页仪表盘界面</span>
        </div>
      </section>

      <!-- ========== 测试管理 ========== -->
      <section id="test" class="doc-section">
        <h2 class="sec-title">
          <el-icon class="sec-icon"
            ><component :is="useRenderIcon('ep/notebook')"
          /></el-icon>
          测试管理
        </h2>
        <p class="sec-desc">
          测试管理是平台核心模块，包含车辆管理、路线管理、测试里程、人员管理四个子模块。
        </p>

        <!-- 车辆管理 -->
        <h3 class="sub-title">车辆管理</h3>
        <p class="sec-desc">
          管理所有测试车辆的基本信息和借用情况，确保车辆资源可追溯、可调度。包含两个子页面：
        </p>

        <div class="child-card">
          <div class="child-header">车辆资源表</div>
          <div class="child-body">
            <p>
              展示所有车辆列表，支持按车型、VIN码、组别、使用状态等条件筛选。
            </p>
            <div class="step-list">
              <div class="step-item">
                <span class="step-dot">1</span
                >点击「新增记录」填写车辆编号、型号、VIN码、车牌号等
              </div>
              <div class="step-item">
                <span class="step-dot">2</span>通过搜索栏按条件筛选目标车辆
              </div>
              <div class="step-item">
                <span class="step-dot">3</span>操作列支持编辑车辆信息，借用车辆
              </div>
              <div class="step-item">
                <span class="step-dot">4</span>支持批量导入 Excel 数据
              </div>
            </div>
          </div>
        </div>
        <div class="screenshot-area">
          <el-image
            class="screenshot-img"
            src="/tutorial/vehicle-resource.png"
            fit="contain"
            :preview-src-list="['/tutorial/vehicle-resource.png']"
            preview-teleported
            lazy
          >
            <template #error>
              <div class="img-placeholder">
                <el-icon size="28"
                  ><component :is="useRenderIcon('ep/picture')" /></el-icon
                ><span>待补充截图</span>
              </div>
            </template>
          </el-image>
          <span class="img-caption">车辆资源表界面</span>
        </div>
        <div class="child-card">
          <div class="child-header">车辆借用表</div>
          <div class="child-body">
            <p>记录车辆借用记录，跟踪车辆使用状态。</p>
            <div class="step-list">
              <div class="step-item">
                <span class="step-dot">1</span>归还时点击对应记录的「归还」按钮
              </div>
              <div class="step-item">
                <span class="step-dot">2</span
                >取消借用时点击对应记录的「取消」按钮
              </div>
              <div class="step-item">
                <span class="step-dot">3</span>系统自动更新车辆状态（借用中 /
                可用）
              </div>
            </div>
          </div>
        </div>
        <div class="screenshot-area">
          <el-image
            class="screenshot-img"
            src="/tutorial/vehicle-borrow.png"
            fit="contain"
            :preview-src-list="['/tutorial/vehicle-borrow.png']"
            preview-teleported
            lazy
          >
            <template #error>
              <div class="img-placeholder">
                <el-icon size="28"
                  ><component :is="useRenderIcon('ep/picture')" /></el-icon
                ><span>待补充截图</span>
              </div>
            </template>
          </el-image>
          <span class="img-caption">车辆借用表界面</span>
        </div>
        <el-alert type="warning" :closable="false" show-icon class="doc-alert">
          借用后车辆状态自动变为「借用中」，归还后恢复「可用」，请及时归还以保证资源可用。
        </el-alert>

        <!-- 路线管理 -->
        <h3 class="sub-title">路线管理</h3>
        <p class="sec-desc">
          管理测试路线信息，包括路线名称、起点终点、里程数、路况类型等。
        </p>
        <div class="step-list">
          <div class="step-item">
            <span class="step-dot">1</span>点击「新增路线」添加测试路线
          </div>
          <div class="step-item">
            <span class="step-dot">2</span
            >填写路线名称、创建人、测试功能、里程、难度系数等信息
          </div>
          <div class="step-item">
            <span class="step-dot">3</span>标注路况特征和路线描述
          </div>
          <div class="step-item">
            <span class="step-dot">4</span>路线信息可用于任务关联和里程统计
          </div>
        </div>
        <div class="screenshot-area">
          <el-image
            class="screenshot-img"
            src="/tutorial/route.png"
            fit="contain"
            :preview-src-list="['/tutorial/route.png']"
            preview-teleported
            lazy
          >
            <template #error>
              <div class="img-placeholder">
                <el-icon size="28"
                  ><component :is="useRenderIcon('ep/picture')" /></el-icon
                ><span>待补充截图</span>
              </div>
            </template>
          </el-image>
          <span class="img-caption">路线管理界面</span>
        </div>

        <!-- 测试里程 -->
        <h3 class="sub-title">测试里程</h3>
        <p class="sec-desc">
          记录和查看每次测试的功能里程、车辆行驶里程数据，支持按项目、测试版本、测试功能、时间段多维度筛选查询，汇总展示总里程、NAP/CNAP分类里程，并提供版本、每日、功能维度可视化图表统计。
        </p>
        <div class="step-list">
          <div class="step-item">
            <span class="step-dot">1</span
            >通过顶部筛选栏，按项目、测试版本、测试功能、起止时间筛选测试里程列表数据
          </div>
          <div class="step-item">
            <span class="step-dot">2</span
            >对里程记录执行新增、编辑操作，可查看每条记录的车辆VIN、功能测试里程、车辆行驶里程、KPI统计标记等详情
          </div>
          <div class="step-item">
            <span class="step-dot">3</span
            >页面底部自动汇总总里程、NAP里程、CNAP里程，同时展示版本里程柱状图、每日里程曲线图、功能里程环形图可视化统计
          </div>
        </div>
        <div class="screenshot-area">
          <el-image
            class="screenshot-img"
            src="/tutorial/mileage.png"
            fit="contain"
            :preview-src-list="['/tutorial/mileage.png']"
            preview-teleported
            lazy
          >
            <template #error>
              <div class="img-placeholder">
                <el-icon size="28"
                  ><component :is="useRenderIcon('ep/picture')" /></el-icon
                ><span>待补充截图</span>
              </div>
            </template>
          </el-image>
          <span class="img-caption">测试里程界面</span>
        </div>

        <!-- 人员管理 -->
        <h3 class="sub-title">人员管理</h3>
        <p class="sec-desc">管理参与测试的人员信息，包括司机、外协等角色。</p>
        <div class="step-list">
          <div class="step-item">
            <span class="step-dot">1</span
            >添加人员基本信息（姓名、岗位类型、负责任务等）
          </div>
          <div class="step-item">
            <span class="step-dot">2</span>填写模块名称、模块负责人
          </div>
          <div class="step-item">
            <span class="step-dot">3</span>通过姓名或者模块名称进行搜索
          </div>
        </div>
        <div class="screenshot-area">
          <el-image
            class="screenshot-img"
            src="/tutorial/personnel.png"
            fit="contain"
            :preview-src-list="['/tutorial/personnel.png']"
            preview-teleported
            lazy
          >
            <template #error>
              <div class="img-placeholder">
                <el-icon size="28"
                  ><component :is="useRenderIcon('ep/picture')" /></el-icon
                ><span>待补充截图</span>
              </div>
            </template>
          </el-image>
          <span class="img-caption">人员管理界面</span>
        </div>
      </section>

      <!-- ========== 测试记录 ========== -->
      <section id="record" class="doc-section">
        <h2 class="sec-title">
          <el-icon class="sec-icon"
            ><component :is="useRenderIcon('ep/document')"
          /></el-icon>
          测试记录
        </h2>
        <p class="sec-desc">
          存储和查询三类核心测试数据，每个子页面支持多维度筛选、详情查看和 Excel
          导出。
        </p>

        <div class="record-cards">
          <div class="record-card">
            <div class="rc-header nap">NAP</div>
            <div class="rc-body">
              <div class="rc-desc">导航辅助驾驶测试记录</div>
              <div class="rc-steps">
                <div>1. 进入「测试记录 > NAP」</div>
                <div>2. 按项目、车辆、时间范围筛选</div>
                <div>
                  3. 点击新增问题，填写项目、车型、问题时间、问题类型等信息
                </div>
                <div>4. 支持批量导入和导出Excel</div>
              </div>
            </div>
          </div>
          <div class="record-card">
            <div class="rc-header cnap">CNAP</div>
            <div class="rc-body">
              <div class="rc-desc">城市导航辅助驾驶测试记录</div>
              <div class="rc-steps">
                <div>1. 进入「测试记录 > CNAP」</div>
                <div>2. 查看 CNAP 测试数据</div>
                <div>3. 多维度筛选搜索</div>
              </div>
            </div>
          </div>
          <div class="record-card">
            <div class="rc-header lcc">LCC/ACC</div>
            <div class="rc-body">
              <div class="rc-desc">车道居中 / 自适应巡航测试记录</div>
              <div class="rc-steps">
                <div>1. 进入「测试记录 > LCC/ACC」</div>
                <div>2. 查看功能测试数据</div>
                <div>3. 支持筛选和导出</div>
              </div>
            </div>
          </div>
        </div>
        <div class="screenshot-area">
          <el-image
            class="screenshot-img"
            src="/tutorial/record.png"
            fit="contain"
            :preview-src-list="['/tutorial/record.png']"
            preview-teleported
            lazy
          >
            <template #error>
              <div class="img-placeholder">
                <el-icon size="28"
                  ><component :is="useRenderIcon('ep/picture')" /></el-icon
                ><span>待补充截图</span>
              </div>
            </template>
          </el-image>
          <span class="img-caption">测试记录界面</span>
        </div>
      </section>

      <!-- ========== 统计分析 ========== -->
      <section id="statistics" class="doc-section">
        <h2 class="sec-title">
          <el-icon class="sec-icon"
            ><component :is="useRenderIcon('ep/data-analysis')"
          /></el-icon>
          统计分析
        </h2>
        <p class="sec-desc">
          多维度数据可视化，帮助测试趋势和问题。包含四个子页面：
        </p>

        <div class="stats-grid">
          <div class="stats-card">
            <div class="sc-icon">
              <el-icon size="22"
                ><component :is="useRenderIcon('ep/histogram')"
              /></el-icon>
            </div>
            <div class="sc-info">
              <div class="sc-name">NAP 统计结果</div>
              <div class="sc-desc">
                按项目、时间等维度汇总分析，点击项目可进入详情页
              </div>
            </div>
          </div>
          <div class="stats-card">
            <div class="sc-icon">
              <el-icon size="22"
                ><component :is="useRenderIcon('ep/pie-chart')"
              /></el-icon>
            </div>
            <div class="sc-info">
              <div class="sc-name">CNAP 统计结果</div>
              <div class="sc-desc">城市导航辅助驾驶测试数据统计分析</div>
            </div>
          </div>
          <div class="stats-card">
            <div class="sc-icon">
              <el-icon size="22"
                ><component :is="useRenderIcon('ep/trend-charts')"
              /></el-icon>
            </div>
            <div class="sc-info">
              <div class="sc-name">LCC/ACC 统计结果</div>
              <div class="sc-desc">辅助驾驶功能测试的统计汇总</div>
            </div>
          </div>
          <div class="stats-card">
            <div class="sc-icon">
              <el-icon size="22"
                ><component :is="useRenderIcon('ep/map-location')"
              /></el-icon>
            </div>
            <div class="sc-info">
              <div class="sc-name">功能里程图</div>
              <div class="sc-desc">以地图形式展示各功能测试的里程分布</div>
            </div>
          </div>
        </div>
        <div class="screenshot-area">
          <el-image
            class="screenshot-img"
            src="/tutorial/statistics.png"
            fit="contain"
            :preview-src-list="['/tutorial/statistics.png']"
            preview-teleported
            lazy
          >
            <template #error>
              <div class="img-placeholder">
                <el-icon size="28"
                  ><component :is="useRenderIcon('ep/picture')" /></el-icon
                ><span>待补充截图</span>
              </div>
            </template>
          </el-image>
          <span class="img-caption">统计分析界面</span>
        </div>
      </section>

      <!-- ========== 常用工具 ========== -->
      <section id="tools" class="doc-section">
        <h2 class="sec-title">
          <el-icon class="sec-icon"
            ><component :is="useRenderIcon('ep/setting')"
          /></el-icon>
          常用工具
        </h2>
        <p class="sec-desc">
          汇集日常高频使用的功能入口和帮助资源，包含两个子页面：
        </p>
        <div class="step-list">
          <div class="step-item">
            <span class="step-dot">1</span><strong>使用教程</strong> —
            即当前页面，提供平台各模块的详细使用说明和操作指引
          </div>
          <div class="step-item">
            <span class="step-dot">2</span><strong>常用应用</strong> —
            常用外部应用和工具的快捷入口，方便快速访问相关资源
          </div>
        </div>
        <div class="screenshot-area">
          <el-image
            class="screenshot-img"
            src="/tutorial/tools.png"
            fit="contain"
            :preview-src-list="['/tutorial/tools.png']"
            preview-teleported
            lazy
          >
            <template #error>
              <div class="img-placeholder">
                <el-icon size="28"
                  ><component :is="useRenderIcon('ep/picture')" /></el-icon
                ><span>待补充截图</span>
              </div>
            </template>
          </el-image>
          <span class="img-caption">常用工具界面</span>
        </div>
      </section>

      <!-- ========== 常见问题 ========== -->
      <section id="faq" class="doc-section">
        <h2 class="sec-title">
          <el-icon class="sec-icon"
            ><component :is="useRenderIcon('ep/question-filled')"
          /></el-icon>
          常见问题
        </h2>
        <div class="faq-list">
          <div class="faq-item">
            <div class="faq-q">Q: 忘记密码怎么办？</div>
            <div class="faq-a">
              联系管理员在「权限管理 > 用户管理」中重置密码。
            </div>
          </div>
          <div class="faq-item">
            <div class="faq-q">Q: 为什么看不到某些菜单？</div>
            <div class="faq-a">
              菜单可见性由角色权限控制，请联系管理员检查您的角色权限配置。
            </div>
          </div>
          <div class="faq-item">
            <div class="faq-q">Q: 如何批量导入数据？</div>
            <div class="faq-a">
              点击「导入」按钮，先下载模板，按格式填写后上传 Excel
              即可。支持车辆资源、人员管理、测试记录等模块。
            </div>
          </div>
          <div class="faq-item">
            <div class="faq-q">Q: 数据可以导出吗？</div>
            <div class="faq-a">
              大部分列表页面支持导出，点击「导出」按钮将当前筛选结果导出为 Excel
              文件。
            </div>
          </div>
          <div class="faq-item">
            <div class="faq-q">Q: 如何切换主题/暗黑模式？</div>
            <div class="faq-a">
              点击右上角设置图标，在面板中切换亮色/暗色主题、调整布局等个性化设置。
            </div>
          </div>
          <div class="faq-item">
            <div class="faq-q">Q: 页面加载缓慢怎么办？</div>
            <div class="faq-a">
              建议检查网络，或缩小查询时间范围和数据量。如持续有问题，请联系技术支持。
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- 回到顶部 -->
    <transition name="fade">
      <div v-if="showBackTop" class="back-top" @click="scrollToTop">
        <el-icon size="20"
          ><component :is="useRenderIcon('ep/caret-top')"
        /></el-icon>
      </div>
    </transition>
  </div>
</template>

<style lang="scss" scoped>
.tutorial-wrap {
  min-height: calc(100vh - 84px);
  background: var(--el-bg-color-page);
}

/* 内联目录 */
.toc-inline {
  margin-bottom: 32px;
  padding: 16px 20px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-lighter);

  .toc-inline-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--el-text-color-secondary);
    margin-bottom: 10px;
  }

  .toc-inline-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .toc-inline-item {
    display: inline-block;
    padding: 4px 14px;
    font-size: 13px;
    color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      background: var(--el-color-primary);
      color: #fff;
    }
  }
}

/* 内容区 - Card样式 */
.tutorial-body {
  max-width: Auto;
  margin: 0 auto;
  padding: 24px 32px 40px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.doc-section {
  margin-bottom: 48px;
  scroll-margin-top: 20px;
}

.sec-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  margin: 0 0 6px;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--el-color-primary);

  .sec-icon {
    color: var(--el-color-primary);
    font-size: 22px;
  }
}

.sec-desc {
  font-size: 14px;
  color: var(--el-text-color-regular);
  line-height: 1.7;
  margin: 8px 0 14px;
}

.sub-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 20px 0 10px;
  padding-left: 10px;
  border-left: 3px solid var(--el-color-primary-light-3);
}

/* 特性卡片 */
.card-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin: 16px 0;
}

.feature-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 20px 16px;
  text-align: center;
  transition: all 0.25s;
  cursor: pointer;

  &:hover {
    box-shadow: 0 4px 16px rgba(64, 158, 255, 0.15);
    transform: translateY(-2px);
    border-color: var(--el-color-primary-light-5);
  }

  .card-icon {
    width: 52px;
    height: 52px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 12px;

    &.blue {
      background: #ecf5ff;
      color: #409eff;
    }
    &.green {
      background: #e8f8f0;
      color: #67c23a;
    }
    &.orange {
      background: #fdf6ec;
      color: #e6a23c;
    }
    &.purple {
      background: #f4f0fe;
      color: #7846e5;
    }
  }

  .card-label {
    font-size: 14px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    margin-bottom: 4px;
  }

  .card-desc {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    line-height: 1.5;
  }
}

/* 快速开始 */
.quick-steps {
  margin: 16px 0;
}

.qs-item {
  display: flex;
  gap: 16px;
  padding: 16px 0;
  border-bottom: 1px dashed var(--el-border-color-lighter);

  &:last-child {
    border-bottom: none;
  }

  .qs-num {
    width: 36px;
    height: 36px;
    min-width: 36px;
    border-radius: 50%;
    background: var(--el-color-primary);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    font-weight: 700;
  }

  .qs-body {
    .qs-title {
      font-size: 15px;
      font-weight: 600;
      color: var(--el-text-color-primary);
      margin-bottom: 4px;
    }

    .qs-desc {
      font-size: 13px;
      color: var(--el-text-color-secondary);
      line-height: 1.6;
    }
  }
}

/* 子模块卡片 */
.child-card {
  margin: 12px 0;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  overflow: hidden;

  .child-header {
    padding: 10px 16px;
    font-size: 14px;
    font-weight: 600;
    color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
    border-bottom: 1px solid var(--el-border-color-lighter);
  }

  .child-body {
    padding: 12px 16px;
    background: var(--el-bg-color);

    p {
      font-size: 13px;
      color: var(--el-text-color-secondary);
      margin: 0 0 8px;
      line-height: 1.6;
    }
  }
}

/* 步骤列表 */
.step-list {
  margin: 6px 0 12px;
}

.step-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 5px 0;
  font-size: 14px;
  line-height: 1.6;
  color: var(--el-text-color-regular);

  .step-dot {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    min-width: 20px;
    border-radius: 50%;
    background: var(--el-color-primary-light-9);
    color: var(--el-color-primary);
    font-size: 12px;
    font-weight: 600;
    margin-top: 1px;
  }

  strong {
    color: var(--el-text-color-primary);
  }
}

/* 提示条 */
.doc-alert {
  margin: 12px 0;
}

/* 测试记录卡片 */
.record-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin: 16px 0;
}

.record-card {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  overflow: hidden;
  transition: box-shadow 0.25s;

  &:hover {
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  }

  .rc-header {
    padding: 12px 16px;
    font-size: 16px;
    font-weight: 700;
    color: #fff;

    &.nap {
      background: #409eff;
    }
    &.cnap {
      background: #67c23a;
    }
    &.lcc {
      background: #e6a23c;
    }
  }

  .rc-body {
    padding: 14px 16px;
    background: var(--el-bg-color);

    .rc-desc {
      font-size: 13px;
      color: var(--el-text-color-secondary);
      margin-bottom: 10px;
    }

    .rc-steps {
      div {
        font-size: 13px;
        color: var(--el-text-color-regular);
        line-height: 1.7;
        padding-left: 4px;
      }
    }
  }
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin: 16px 0;
}

.stats-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  transition: all 0.25s;

  &:hover {
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  }

  .sc-icon {
    width: 44px;
    height: 44px;
    min-width: 44px;
    border-radius: 10px;
    background: var(--el-color-primary-light-9);
    color: var(--el-color-primary);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .sc-info {
    .sc-name {
      font-size: 14px;
      font-weight: 600;
      color: var(--el-text-color-primary);
      margin-bottom: 4px;
    }

    .sc-desc {
      font-size: 12px;
      color: var(--el-text-color-secondary);
      line-height: 1.5;
    }
  }
}

/* 截图区域 */
.screenshot-area {
  margin: 24px auto;
  padding: 20px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-lighter);

  .screenshot-img {
    max-width: 100%;
    border-radius: 8px;
    border: 1px solid var(--el-border-color-lighter);
    cursor: zoom-in;
    background: #fff;

    :deep(.el-image__inner) {
      max-height: 480px;
      object-fit: contain;
    }
  }

  .img-placeholder {
    width: 100%;
    height: 160px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    background: var(--el-fill-color-lighter);
    border-radius: 8px;
    color: var(--el-text-color-placeholder);
    font-size: 13px;
  }

  .img-caption {
    display: block;
    margin-top: 6px;
    font-size: 12px;
    color: var(--el-text-color-placeholder);
  }
}

/* FAQ */
.faq-list {
  margin: 12px 0;
}

.faq-item {
  padding: 14px 16px;
  margin-bottom: 8px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 6px;
  transition: all 0.2s;

  &:hover {
    border-color: var(--el-color-primary-light-5);
  }

  .faq-q {
    font-size: 14px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    margin-bottom: 6px;
  }

  .faq-a {
    font-size: 13px;
    color: var(--el-text-color-secondary);
    line-height: 1.6;
  }
}

/* 回到顶部 */
.back-top {
  position: fixed;
  right: 32px;
  bottom: 32px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--el-color-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.35);
  transition: all 0.3s;
  z-index: 100;

  &:hover {
    transform: scale(1.1);
    box-shadow: 0 4px 16px rgba(64, 158, 255, 0.5);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 900px) {
  .tutorial-body {
    padding: 20px 16px 32px;
    margin: 0 10px;
    border-radius: 6px;
  }

  .card-row {
    grid-template-columns: repeat(2, 1fr);
  }

  .record-cards {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .tutorial-wrap {
  }

  .tutorial-body {
    padding: 16px 12px 24px;
    margin: 0;
    border-radius: 4px;
  }
}
</style>

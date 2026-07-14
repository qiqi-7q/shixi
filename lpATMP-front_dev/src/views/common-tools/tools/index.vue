<script setup lang="ts">
import { ref } from "vue";

defineOptions({
  name: "Tools"
});

const toolsList = ref([
  {
    id: 1,
    name: "LeapMind",
    description: "LeapMind AI平台",
    icon: "ri/robot-line",
    url: "https://ai.leapmotor.com/",
    color: "#409EFF"
  },
  {
    id: 2,
    name: "Redmine",
    description: "查看上位机打点数据，可根据车型、时间或描述筛选数据",
    icon: "ri/database-2-line",
    url: "https://leap-redmine.leapmotor.com/redmine/login?back_url=http%3A%2F%2Fleap-redmine.leapmotor.com%2Fredmine%2Fmy%2Fpage",
    color: "#E6A23C"
  },
  {
    id: 3,
    name: "Wetrack",
    description: "问题单跟踪平台",
    icon: "ri/bug-line",
    url: "https://dts.leapmotor.com/DTS/defect/pending",
    color: "#F56C6C"
  },
  {
    id: 4,
    name: "AI Platform",
    description: "巨灵平台：查看数据上传、解析记录",
    icon: "ri/cloud-line",
    url: "https://leapai.leapmotor.com/#/login?redirect=%2FallIntroduction",
    color: "#67C23A"
  },
  {
    id: 5,
    name: "LPFServer",
    description: "上位机发布平台",
    icon: "ri/server-line",
    url: "http://roadtest.leapmotor.com/home/ServerSpace/ReleaseServer/001_LPRoadTestMaster",
    color: "#909399"
  },
  {
    id: 6,
    name: "网盘",
    description: "企业网盘",
    icon: "ri/folder-line",
    url: "https://pan.leapmotor.com/anyshare/zh-cn?redirect=%2Fzh-cn%2Fdir%2F236D7D56DFAA4E4F8331E912A842E9AA",
    color: "#B37FEB"
  },

  {
    id: 7,
    name: "Foxglove",
    description: "用于问题分析",
    icon: "ri/bar-chart-box-line",
    url: "https://leapvize.leapmotor.com/?ds=ros1-local-bagfile",
    color: "#FF85C0"
  },
  {
    id: 8,
    name: "AI助手",
    description: "AI智能助手（内网）",
    icon: "ri/chat-smile-3-line",
    url: "http://10.195.136.18:3000/chat/share?shareId=61x3h2vodkq5gtxhp9fwxu8t",
    color: "#13C2C2"
  },
  {
    id: 9,
    name: "零云平台",
    description: "零云管理平台",
    icon: "ri/cloudy-line",
    url: "https://leapcloud.leapmotor.com/login?redirect=%2FnoAuth",
    color: "#36CFC9"
  },
  // {
  //   id: 10,
  //   name: "零云平台(正式版)",
  //   description: "零云正式环境",
  //   icon: "ri/global-line",
  //   url: "https://leapcloud.leapmotor.com/login?redirect=%2FnoAuth",
  //   color: "#597EF7"
  // },
  {
    id: 11,
    name: "零云平台(测试版)",
    description: "零云测试环境",
    icon: "ri/settings-4-line",
    url: "https://test3.leapmotor.com/login",
    color: "#FAAD14"
  },
  {
    id: 12,
    name: "统一用户中心",
    description: "统一用户中心",
    icon: "ri/settings-4-line",
    url: "https://test3.leapmotor.com/login",
    color: "#FAAD14"
  },
  {
    id: 13,
    name: "OA",
    description: "办公自动化系统",
    icon: "ri/contacts-book-line",
    url: "https://oa.leapmotor.com/wui/index.html#/main/portal/portal-32161-41?menuIds=0,32161&menuPathIds=0,32161&_key=uftner",
    color: "#722ED1"
  },
  {
    id: 14,
    name: "BI数据分析",
    description: "商业智能数据分析平台",
    icon: "ri/pie-chart-2-line",
    url: "https://bi.leapmotor.com/home",
    color: "#13C2C2"
  },
  {
    id: 15,
    name: "工时管理",
    description: "工时管理系统",
    icon: "ri/time-line",
    url: "https://lppms.leapmotor.com/cusapp/1782733409564233495/PAGE/1042912896695590913-1773578496570765281?wea_link_keep_loginType=intunifyauth&wea_link_keep_basic_intercept=0&cusMenuId=1773578496570765281&urlPageTitle=ICAg5bel5pe255m76K6w&appId_1042912896695590913=1020363970691293184&sourceType=2",
    color: "#EB2F96"
  },
  {
    id: 16,
    name: "虚拟上网",
    description: "虚拟专用网络",
    icon: "ri/global-line",
    url: "https://yfvapp.leapmotor.com/#/user/login",
    color: "#597EF7"
  },
  {
    id: 17,
    name: "试验车管理系统",
    description: "试验车管理平台",
    icon: "ri/car-line",
    url: "https://lppms.leapmotor.com/ebdapp/view/992533445825929217/SEARCH/992539231158779905-8261429238047494408?wea_link_keep_loginType=intunifyauth&cusMenuId=8261429238047494408&urlPageTitle=6K%2BV6aqM6L2m6L6G",
    color: "#FA8C16"
  },
  {
    id: 18,
    name: "行车测试组Wiki",
    description: "行车测试组知识库",
    icon: "ri/book-open-line",
    url: "https://eitwiki.leapmotor.com/doc/6kgm6l2m5rwl6kv57ue-TQ9ZcYm8BZ",
    color: "#73D13D"
  }
]);

const openTool = (url: string) => {
  window.open(url, "_blank");
};
</script>

<template>
  <div class="main-content">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span class="text-lg font-medium">常用工具</span>
        </div>
      </template>
      <div class="tools-grid">
        <div
          v-for="tool in toolsList"
          :key="tool.id"
          class="tool-card"
          @click="openTool(tool.url)"
        >
          <div class="tool-icon" :style="{ backgroundColor: tool.color }">
            <span class="tool-icon-text">{{ tool.name.charAt(0) }}</span>
          </div>
          <div class="tool-info">
            <div class="tool-name">{{ tool.name }}</div>
            <div class="tool-description">{{ tool.description }}</div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<style lang="scss" scoped>
.main-content {
  margin: 24px 24px 0 !important;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  padding: 20px 0;
}

.tool-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #e4e7ed;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
}

.tool-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  border-radius: 12px;
  color: #fff;
  font-size: 28px;
  font-weight: bold;
}

.tool-icon-text {
  font-size: 24px;
  font-weight: 600;
}

.tool-info {
  flex: 1;
}

.tool-name {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.tool-description {
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
}
</style>

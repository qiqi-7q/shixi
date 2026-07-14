const Layout = () => import("@/layout/index.vue");

export default {
  path: "/statistics",
  name: "Statistics",
  component: Layout,
  redirect: "/statistics/cnap",
  meta: {
    icon: "ep/data-analysis",
    title: "统计分析",
    rank: 13
  },
  children: [
    {
      path: "/statistics/nap",
      name: "StatisticsNap",
      component: () => import("@/views/statistics/nap/index.vue"),
      meta: {
        title: "NAP统计结果",
        icon: "ep/histogram"
      }
    },
    {
      path: "/statistics/cnap",
      name: "StatisticsCnap",
      component: () => import("@/views/statistics/cnap/index.vue"),
      meta: {
        title: "CNAP统计结果(开发中）",
        icon: "ep/pie-chart"
      }
    },
    {
      path: "/statistics/lcc-acc",
      name: "StatisticsLccAcc",
      component: () => import("@/views/statistics/lcc-acc/index.vue"),
      meta: {
        showLink: false,
        title: "LCC/ACC统计结果(开发中）",
        icon: "ep/trend-charts"
      }
    },
    {
      path: "/statistics/mileage-chart",
      name: "StatisticsMileageChart",
      component: () => import("@/views/statistics/mileage-chart/index.vue"),
      meta: {
        showLink: false,
        title: "功能里程图",
        icon: "ep/map-location"
      }
    },
    {
      path: "/statistics/nap-detail/:id",
      name: "NapProjectDetail",
      component: () => import("@/views/statistics/nap/project-detail.vue"),
      meta: {
        title: "项目详情",
        showLink: false,
        activePath: "/statistics/nap"
      }
    }
    // {
    //   path: "/statistics/heatmap",
    //   name: "StatisticsHeatmap",
    //   component: () => import("@/views/statistics/heatmap/index.vue"),
    //   meta: {
    //     title: "热力图",
    //     icon: "ep/position"
    //   }
    // }
  ]
} satisfies RouteConfigsTable;

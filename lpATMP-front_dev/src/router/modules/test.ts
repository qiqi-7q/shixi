import { tr } from "element-plus/es/locale/index.mjs";

const Layout = () => import("@/layout/index.vue");

export default {
  path: "/test",
  name: "Test",
  component: Layout,
  redirect: "/test/vehicle/resource",
  meta: {
    icon: "ep/notebook",
    title: "测试管理",
    rank: 11
  },
  children: [
    {
      path: "/test/vehicle",
      name: "TestVehicle",
      redirect: "/test/vehicle/resource",
      meta: {
        title: "车辆管理",
        icon: "ep/van"
      },
      children: [
        {
          path: "/test/vehicle/resource",
          name: "TestVehicleResource",
          component: () => import("@/views/test/vehicle/resource/index.vue"),
          meta: {
            title: "车辆资源表",
            icon: "ep/document"
          }
        },

        {
          path: "/test/vehicle/borrow",
          name: "TestVehicleBorrow",
          component: () => import("@/views/test/vehicle/borrow/index.vue"),
          meta: {
            title: "车辆借用表",
            icon: "ep/data-analysis"
          }
        },
        {
          path: "/test/vehicle/monitor",
          name: "TestVehicleMonitor",
          component: () => import("@/views/test/vehicle/monitor/index.vue"),
          meta: {
            title: "车辆监控表",
            icon: "ep/monitor"
          }
        }
      ]
    },
    {
      path: "/test/project-plan",
      name: "TestProjectPlan",
      component: () => import("@/views/test/project-plan/index.vue"),
      meta: {
        title: "项目计划",
        icon: "ep/calendar",
        showLink: false
      }
    },
    {
      path: "/test/task",
      name: "TestTask",
      component: () => import("@/views/test/task/index.vue"),
      meta: {
        title: "任务管理",
        icon: "ep/list",
        showLink: false
      }
    },
    {
      path: "/test/route",
      name: "TestRoute",
      component: () => import("@/views/test/route/index.vue"),
      meta: {
        title: "路线管理",
        icon: "ep/map-location"
      }
    },
    {
      path: "/test/driver",
      name: "TestDriver",
      component: () => import("@/views/test/driver/index.vue"),
      meta: {
        title: "驾驶员监测（开发中）",
        icon: "ep/user",
        showLink: false
      }
    },

    {
      path: "/test/personnel",
      name: "TestPersonnel",
      component: () => import("@/views/test/personnel/index.vue"),
      meta: {
        title: "人员管理",
        icon: "ep/avatar"
      }
    }
  ]
} satisfies RouteConfigsTable;

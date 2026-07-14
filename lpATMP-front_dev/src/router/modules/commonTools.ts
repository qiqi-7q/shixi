const Layout = () => import("@/layout/index.vue");

export default {
  path: "/common-tools",
  name: "CommonTools",
  component: Layout,
  redirect: "/common-tools/tutorial",
  meta: {
    icon: "ep/setting",
    title: "常用工具",
    rank: 15
  },
  children: [
    {
      path: "/common-tools/tutorial",
      name: "Tutorial",
      component: () => import("@/views/common-tools/tutorial/index.vue"),
      meta: {
        title: "使用教程",
        icon: "ep/reading"
      }
    },
    {
      path: "/common-tools/tools",
      name: "Tools",
      component: () => import("@/views/common-tools/tools/index.vue"),
      meta: {
        title: "常用应用",
        icon: "ep/connection"
      }
    },
    {
      path: "/common-tools/dict",
      name: "DictManage",
      component: () => import("@/views/common-tools/dict/index.vue"),
      meta: {
        title: "数据字典",
        icon: "ep/notebook"
      }
    }
  ]
} satisfies RouteConfigsTable;

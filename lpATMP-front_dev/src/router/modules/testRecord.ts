const Layout = () => import("@/layout/index.vue");

export default {
  path: "/test-record",
  name: "TestRecord",
  component: Layout,
  redirect: "/test-record/nap",
  meta: {
    icon: "ep/document",
    title: "测试记录",
    rank: 12
  },
  children: [
    {
      path: "/test-record/nap",
      name: "TestRecordNap",
      component: () => import("@/views/test-record/record/nap/index.vue"),
      meta: {
        title: "NAP",
        icon: "ep/histogram"
      }
    },
    {
      path: "/test/mileage",
      name: "TestMileage",
      component: () => import("@/views/test/mileage/index.vue"),
      meta: {
        title: "测试里程",
        icon: "ep/odometer"
      }
    },
    {
      path: "/test-record/cnap",
      name: "TestRecordCnap",
      component: () => import("@/views/test-record/record/cnap/index.vue"),
      meta: {
        title: "CNAP(开发中）",
        icon: "ep/pie-chart"
      }
    },
    {
      path: "/test-record/lcc-acc",
      name: "TestRecordLccAcc",
      component: () => import("@/views/test-record/record/lccAcc/index.vue"),
      meta: {
        showLink: false,
        title: "LCC/ACC(开发中）",
        icon: "ep/trend-charts"
      }
    }
  ]
} satisfies RouteConfigsTable;

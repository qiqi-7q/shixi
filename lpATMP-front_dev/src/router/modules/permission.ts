const Layout = () => import("@/layout/index.vue");

export default {
  path: "/permission",
  name: "PermissionManage",
  component: Layout,
  redirect: "/permission/user",
  meta: {
    icon: "ep/lollipop",
    title: "权限管理",
    rank: 99
  },
  children: [
    {
      path: "/permission/user",
      name: "PermissionUser",
      component: () => import("@/views/permission/user/index.vue"),
      meta: {
        title: "人员列表",
        showParent: true,
        icon: "ep/user",
        roles: ["admin", "superuser"]
      }
    },
    {
      path: "/permission/role",
      name: "PermissionRole",
      component: () => import("@/views/permission/role/index.vue"),
      meta: {
        showLink: true,
        title: "角色权限",
        showParent: true,
        icon: "ep/lock",
        roles: ["superuser"]
      }
    }
  ]
} satisfies RouteConfigsTable;

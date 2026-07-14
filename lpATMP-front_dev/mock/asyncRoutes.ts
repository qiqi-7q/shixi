// 模拟后端动态生成路由
import { defineFakeRoute } from "vite-plugin-fake-server/client";

/**
 * roles：页面级别权限，这里模拟二种 "admin"、"common"
 * admin：管理员角色
 * common：普通角色
 */
const permissionRouter = {
  path: "/permission",
  meta: {
    title: "权限管理",
    icon: "ep/lollipop",
    rank: 99,
    showLink: false
  },
  children: [
    {
      path: "/permission/page/index",
      name: "PermissionPage",
      meta: {
        title: "页面权限",
        icon: "ep/document-checked",
        roles: ["admin", "common"]
      }
    },
    {
      path: "/permission/button",
      meta: {
        title: "按钮权限",
        roles: ["admin", "common"]
      },
      children: [
        {
          path: "/permission/button/router",
          component: "permission/button/index",
          name: "PermissionButtonRouter",
          meta: {
            title: "路由返回按钮权限",
            auths: [
              "permission:btn:add",
              "permission:btn:edit",
              "permission:btn:delete"
            ]
          }
        },
        {
          path: "/permission/button/login",
          component: "permission/button/perms",
          name: "PermissionButtonLogin",
          meta: {
            title: "登录接口返回按钮权限"
          }
        }
      ]
    },
    {
      path: "/permission/user",
      name: "PermissionUser",
      meta: {
        title: "人员权限管理",
        icon: "ep/user-filled",
        roles: ["admin", "common"]
      },
      children: [
        {
          path: "/permission/user/list",
          component: "permission/user/list",
          name: "PermissionUserList",
          meta: {
            title: "人员列表",
            roles: ["admin", "common"]
          }
        },
        {
          path: "/permission/user/role",
          component: "permission/user/role",
          name: "PermissionUserRole",
          meta: {
            title: "角色管理",
            roles: ["admin"]
          }
        }
      ]
    }
  ]
};

export default defineFakeRoute([
  {
    url: "/get-async-routes",
    method: "get",
    response: () => {
      return {
        success: true,
        data: [permissionRouter]
      };
    }
  }
]);

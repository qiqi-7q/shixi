import { defineStore } from "pinia";
import {
  type userType,
  store,
  router,
  resetRouter,
  routerArrays,
  storageLocal
} from "../utils";
import {
  type UserResult,
  type RefreshTokenResult,
  getLogin,
  refreshTokenApi,
  getMe
} from "@/api/user";
import { useMultiTagsStoreHook } from "./multiTags";
import {
  type DataInfo,
  setToken,
  removeToken,
  userKey,
  formatToken
} from "@/utils/auth";

export const useUserStore = defineStore("pure-user", {
  state: (): userType => ({
    // 头像
    avatar: storageLocal().getItem<DataInfo<number>>(userKey)?.avatar ?? "",
    // 用户名
    username: storageLocal().getItem<DataInfo<number>>(userKey)?.username ?? "",
    // 昵称
    nickname: storageLocal().getItem<DataInfo<number>>(userKey)?.nickname ?? "",
    userid: storageLocal().getItem<DataInfo<number>>(userKey)?.userid ?? "",
    platform_uuid:
      storageLocal().getItem<DataInfo<number>>(userKey)?.platform_uuid ?? "",
    // 页面级别权限
    roles: storageLocal().getItem<DataInfo<number>>(userKey)?.roles ?? [],
    // 按钮级别权限
    permissions:
      storageLocal().getItem<DataInfo<number>>(userKey)?.permissions ?? [],
    // 是否勾选了登录页的免登录
    isRemembered: false,
    // 登录页的免登录存储几天，默认7天
    loginDay: 7
  }),
  actions: {
    /** 存储头像 */
    SET_AVATAR(avatar: string) {
      this.avatar = avatar;
    },
    /** 存储用户名 */
    SET_USERNAME(username: string) {
      this.username = username;
    },
    /** 存储昵称 */
    SET_NICKNAME(nickname: string) {
      this.nickname = nickname;
    },
    /** 存储角色 */
    SET_ROLES(roles: Array<string>) {
      this.roles = roles;
    },
    /** 存储按钮级别权限 */
    SET_PERMS(permissions: Array<string>) {
      this.permissions = permissions;
    },
    /** 存储平台UUID */
    SET_PLATFORM_UUID(platform_uuid: string) {
      this.platform_uuid = platform_uuid;
    },
    /** 存储是否勾选了登录页的免登录 */
    SET_ISREMEMBERED(bool: boolean) {
      this.isRemembered = bool;
    },
    /** 设置登录页的免登录存储几天 */
    SET_LOGINDAY(value: number) {
      this.loginDay = Number(value);
    },
    /** 登入 */
    async loginByUsername(data) {
      return new Promise<any>((resolve, reject) => {
        getLogin(data)
          .then(async res => {
            console.log("res:", res);
            if (res?.data?.access_token) {
              const token = res.data.access_token;
              // 调用 /api/auth/me 获取完整用户信息
              try {
                const meRes: any = await getMe({
                  headers: { Authorization: formatToken(token) }
                });
                const meData = meRes?.data || {};
                setToken({
                  ...res.data,
                  accessToken: token,
                  refreshToken: token,
                  expires: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000),
                  full_name: meData.full_name || "",
                  avatar: meData.avatar || "",
                  nickname: meData.nickname || meData.full_name || "",
                  roles: meData.role ? [meData.role] : [],
                  permissions: meData.permissions || []
                } as any);
              } catch {
                // 获取用户信息失败，使用登录返回的兜底数据
                setToken({
                  ...res.data,
                  accessToken: token,
                  refreshToken: token,
                  expires: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000),
                  roles: res.data.role ? [res.data.role] : [],
                  permissions: ["superuser", "admin"].includes(res.data.role)
                    ? ["*"]
                    : []
                } as any);
              }
              resolve({ success: true, data: res.data });
            } else {
              resolve({
                success: false,
                message: res.message || res || "登录失败"
              });
            }
          })
          .catch(error => {
            console.log("error:", error);

            resolve({
              success: false,
              message:
                error?.message || error?.response?.data?.detail || "登录失败"
            });
            reject(error);
          });
      });
    },
    /** 前端登出（不调用接口） */
    logOut() {
      this.username = "";
      this.roles = [];
      this.permissions = [];
      removeToken();
      useMultiTagsStoreHook().handleTags("equal", [...routerArrays]);
      resetRouter();
      router.push("/login");
    },
    /** 刷新`token` */
    async handRefreshToken(data) {
      return new Promise<RefreshTokenResult>((resolve, reject) => {
        refreshTokenApi(data)
          .then(data => {
            if (data) {
              // 从本地存储获取 username 补充到 data 中
              const localUserInfo =
                storageLocal().getItem<DataInfo<number>>(userKey);
              const tokenData = {
                ...data.data,
                username: localUserInfo?.username || ""
              };
              setToken(tokenData as DataInfo<Date>);
              resolve(data);
            }
          })
          .catch(error => {
            reject(error);
          });
      });
    }
  }
});

export function useUserStoreHook() {
  return useUserStore(store);
}

import Cookies from "js-cookie";
import { useUserStoreHook } from "@/store/modules/user";
import { storageLocal, isString, isIncludeAllChildren } from "@pureadmin/utils";

export interface DataInfo<T> {
  username: string;
  /** token */
  accessToken: string;
  /** `accessToken`的过期时间（时间戳） */
  expires: T;
  /** 用于调用刷新accessToken的接口时所需的token */
  refreshToken: string;
  /** 头像 */
  avatar?: string;
  /** 用户名 */
  full_name?: string;
  /** 昵称 */
  nickname?: string;
  /** 当前登录用户的角色 */
  roles?: Array<string>;
  /** 当前登录用户的按钮级别权限 */
  permissions?: Array<string>;
  /** 当前登录用户的userid */
  userid?: string;
  /** 当前登录用户的平台UUID */
  platform_uuid?: string;
}

export const userKey = "user-info";
export const TokenKey = "authorized-token";
/**
 * 通过`multiple-tabs`是否在`cookie`中，判断用户是否已经登录系统，
 * 从而支持多标签页打开已经登录的系统后无需再登录。
 * 浏览器完全关闭后`multiple-tabs`将自动从`cookie`中销毁，
 * 再次打开浏览器需要重新登录系统
 * */
export const multipleTabsKey = "multiple-tabs";

/** 获取`token` */
export function getToken(): DataInfo<number> {
  // 此处与`TokenKey`相同，此写法解决初始化时`Cookies`中不存在`TokenKey`报错
  return Cookies.get(TokenKey)
    ? JSON.parse(Cookies.get(TokenKey))
    : storageLocal().getItem(userKey);
}

/**
 * @description 设置`token`以及一些必要信息并采用无感刷新`token`方案
 * 无感刷新：后端返回`accessToken`（访问接口使用的`token`）、`refreshToken`（用于调用刷新`accessToken`的接口时所需的`token`，`refreshToken`的过期时间（比如30天）应大于`accessToken`的过期时间（比如2小时））、`expires`（`accessToken`的过期时间）
 * 将`accessToken`、`expires`、`refreshToken`这三条信息放在key值为authorized-token的cookie里（过期自动销毁）
 * 将`avatar`、`full_name`、`nickname`、`roles`、`permissions`、`refreshToken`、`expires`这七条信息放在key值为`user-info`的localStorage里（利用`multipleTabsKey`当浏览器完全关闭后自动销毁）
 */
/**
 * 设置 Token 及相关用户信息到 Cookie 和 LocalStorage
 *
 * 1. 将 accessToken、refreshToken、expires 序列化后存入 Cookie（TokenKey）
 * 2. 设置多标签页模式标记到 Cookie（multipleTabsKey）
 * 3. 将用户信息（头像、用户名、昵称、角色、权限）写入 LocalStorage 和 Pinia 状态
 *
 * @param data - 令牌及用户数据
 * @param data.accessToken - 访问令牌
 * @param data.refreshToken - 刷新令牌
 * @param data.expires - 过期时间（支持 Date 对象，内部转为时间戳）
 * @param data.avatar - 用户头像（可选）
 * @param data.full_name - 用户名（可选，若与 roles 同时存在则立即写入用户信息）
 * @param data.nickname - 用户昵称（可选）
 * @param data.roles - 用户角色列表（可选）
 * @param data.permissions - 按钮权限列表（可选）
 *
 * @example
 * ```ts
 * setToken({
 *   accessToken: "eyJ...",
 *   refreshToken: "eyJ...",
 *   expires: new Date(Date.now() + 8 * 60 * 60 * 1000),
 *   full_name: "admin",
 *   roles: ["admin"],
 *   permissions: ["btn:add"]
 * });
 * ```
 */
export function setToken(data: DataInfo<Date>) {
  let expires = 0;
  const { accessToken, refreshToken } = data;
  const { isRemembered, loginDay } = useUserStoreHook();
  expires = new Date(data.expires).getTime(); // 如果后端直接设置时间戳，将此处代码改为expires = data.expires，然后把上面的DataInfo<Date>改成DataInfo<number>即可
  const cookieString = JSON.stringify({ accessToken, expires, refreshToken });

  expires > 0
    ? Cookies.set(TokenKey, cookieString, {
        expires: (expires - Date.now()) / 86400000
      })
    : Cookies.set(TokenKey, cookieString);

  Cookies.set(multipleTabsKey, "true", {
    expires: loginDay
  });

  function setUserKey(data) {
    // 全部从data中取值，缺失给兜底
    const {
      avatar = "",
      full_name = "",
      nickname = "",
      roles = [],
      permissions = [],
      refreshToken,
      expires
    } = data || {};
    useUserStoreHook().SET_AVATAR(avatar);
    useUserStoreHook().SET_USERNAME(full_name);
    useUserStoreHook().SET_NICKNAME(nickname);
    useUserStoreHook().SET_ROLES(roles);
    useUserStoreHook().SET_PERMS(permissions);
    storageLocal().setItem(userKey, {
      ...data,
      refreshToken,
      expires,
      avatar,
      full_name,
      nickname,
      roles,
      permissions
    });
  }

  if (data) {
    const { roles } = data;
    setUserKey({
      ...data,
      avatar: data?.avatar ?? "",
      nickname: data?.nickname ?? "",
      roles: data?.roles ?? "",
      permissions: data?.permissions ?? []
    });
  } else {
    const avatar =
      storageLocal().getItem<DataInfo<number>>(userKey)?.avatar ?? "";
    const full_name =
      storageLocal().getItem<DataInfo<number>>(userKey)?.full_name ?? "";
    const nickname =
      storageLocal().getItem<DataInfo<number>>(userKey)?.nickname ?? "";
    const roles =
      storageLocal().getItem<DataInfo<number>>(userKey)?.roles ?? [];
    const permissions =
      storageLocal().getItem<DataInfo<number>>(userKey)?.permissions ?? [];
    setUserKey({
      avatar,
      full_name,
      nickname,
      roles,
      permissions
    });
  }
}

/** 删除`token`以及key值为`user-info`的localStorage信息 */
export function removeToken() {
  Cookies.remove(TokenKey);
  Cookies.remove(multipleTabsKey);
  storageLocal().removeItem(userKey);
}

/** 格式化token（jwt格式） */
export const formatToken = (token: string): string => {
  return "Bearer " + token;
};

/** 是否有按钮级别的权限（根据登录接口返回的`permissions`字段进行判断）*/
export const hasPerms = (value: string | Array<string>): boolean => {
  if (!value) return false;
  const allPerms = "*:*:*";
  const { permissions } = useUserStoreHook();
  if (!permissions) return false;
  if (permissions.length === 1 && permissions[0] === allPerms) return true;
  const isAuths = isString(value)
    ? permissions.includes(value)
    : isIncludeAllChildren(value, permissions);
  return isAuths ? true : false;
};

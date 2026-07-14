import { http } from "@/utils/http";
import type { AxiosRequestConfig } from "axios";

export type UserResult = {
  code: number;
  message: string;
  data: {
    role: any;
    /** JWT 访问令牌 */
    access_token: string;
    /** 令牌类型（bearer） */
    token_type: string;
  };
};

export type RefreshTokenResult = {
  success: boolean;
  data: {
    /** `token` */
    accessToken: string;
    /** 用于调用刷新`accessToken`的接口时所需的`token` */
    refreshToken: string;
    /** `accessToken`的过期时间（格式'xxxx/xx/xx xx:xx:xx'） */
    expires: Date;
  };
};

/** 登录 */
export const getLogin = (data?: { username: string; password: string }) => {
  const formData = new URLSearchParams();
  formData.append("username", data.username);
  formData.append("password", data.password);
  return http.request<UserResult>("post", "/api/auth/login", {
    data: formData,
    headers: { "Content-Type": "application/x-www-form-urlencoded" }
  });
};

/** 刷新`token` */
export const refreshTokenApi = (data?: object) => {
  return http.request<RefreshTokenResult>("post", "/refresh-token", { data });
};

/** 获取当前用户信息 */
export const getMe = (config?: AxiosRequestConfig) => {
  return http.request("get", "/api/auth/me", config);
};

/** 修改密码 */
export const changePassword = (data: {
  old_password: string;
  new_password: string;
}) => {
  return http.request("put", "/api/auth/password", { data });
};

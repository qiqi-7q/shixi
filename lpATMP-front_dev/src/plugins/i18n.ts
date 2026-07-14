/**
 * i18n 插件（占位实现）
 * 用于临时解决构建错误，后续可根据需要接入完整的国际化方案
 */

/**
 * 转换国际化文本
 * 当前直接返回原始文本，不做翻译处理
 */
export function transformI18n(text: string): string {
  if (!text) return "";
  return text;
}

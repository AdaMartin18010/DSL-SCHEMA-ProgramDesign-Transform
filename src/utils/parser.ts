/**
 * 解析工具函数
 * 
 * 支持JSON和YAML格式的解析
 */

import { parse as parseYaml } from "yaml";

/**
 * 解析YAML或JSON字符串
 * 
 * @param content YAML或JSON格式的字符串
 * @returns 解析后的对象
 */
export function parseYamlOrJson(content: string): any {
  const trimmed = content.trim();

  // 尝试解析为JSON
  if (trimmed.startsWith("{") || trimmed.startsWith("[")) {
    try {
      return JSON.parse(trimmed);
    } catch (e) {
      // JSON解析失败，尝试YAML
    }
  }

  // 解析为YAML
  try {
    return parseYaml(trimmed);
  } catch (e) {
    throw new Error(
      `无法解析内容，既不是有效的JSON也不是有效的YAML: ${e instanceof Error ? e.message : String(e)}`
    );
  }
}

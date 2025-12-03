/**
 * Schema验证工具
 * 
 * 提供OpenAPI和AsyncAPI规范的验证功能
 */

import Ajv from "ajv";
import addFormats from "ajv-formats";
import { parseYamlOrJson } from "./parser.js";

// 创建AJV实例
const ajv = new Ajv({ allErrors: true, strict: false });
addFormats(ajv);

/**
 * 验证OpenAPI规范
 */
export async function validateOpenApi(
  openApiSpec: string
): Promise<{
  valid: boolean;
  errors: string[];
  warnings?: string[];
}> {
  try {
    const spec = parseYamlOrJson(openApiSpec);

    // 基本结构验证
    if (!spec.openapi) {
      return {
        valid: false,
        errors: ["缺少openapi版本字段"],
      };
    }

    if (!spec.info) {
      return {
        valid: false,
        errors: ["缺少info字段"],
      };
    }

    // 基本验证通过
    return {
      valid: true,
      errors: [],
      warnings: [],
    };
  } catch (error) {
    return {
      valid: false,
      errors: [
        error instanceof Error ? error.message : String(error),
      ],
    };
  }
}

/**
 * 验证AsyncAPI规范
 */
export async function validateAsyncApi(
  asyncApiSpec: string
): Promise<{
  valid: boolean;
  errors: string[];
  warnings?: string[];
}> {
  try {
    const spec = parseYamlOrJson(asyncApiSpec);

    // 基本结构验证
    if (!spec.asyncapi) {
      return {
        valid: false,
        errors: ["缺少asyncapi版本字段"],
      };
    }

    if (!spec.info) {
      return {
        valid: false,
        errors: ["缺少info字段"],
      };
    }

    // 基本验证通过
    return {
      valid: true,
      errors: [],
      warnings: [],
    };
  } catch (error) {
    return {
      valid: false,
      errors: [
        error instanceof Error ? error.message : String(error),
      ],
    };
  }
}

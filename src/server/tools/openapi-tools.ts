/**
 * OpenAPI转换工具定义
 */

import { Tool } from "../types.js";
import { openApiToAsyncApi } from
  "../../transformers/openapi/openapi-to-asyncapi.js";
import { validateOpenApi } from "../../utils/validation.js";

/**
 * 注册OpenAPI相关工具
 */
export async function registerOpenApiTools(): Promise<Tool[]> {
  return [
    {
      definition: {
        name: "openapi_to_asyncapi",
        description:
          "将OpenAPI规范转换为AsyncAPI规范",
        inputSchema: {
          type: "object",
          properties: {
            openapi_spec: {
              type: "string",
              description: "OpenAPI规范（JSON或YAML格式）",
            },
            target_version: {
              type: "string",
              description: "目标AsyncAPI版本（默认：3.0.0）",
              default: "3.0.0",
            },
          },
          required: ["openapi_spec"],
        },
      },
      handler: async (args: any) => {
        const { openapi_spec, target_version = "3.0.0" } = args;

        // 验证OpenAPI规范
        const validationResult = await validateOpenApi(openapi_spec);
        if (!validationResult.valid) {
          throw new Error(
            `OpenAPI规范验证失败: ${validationResult.errors.join(", ")}`
          );
        }

        // 执行转换
        const asyncApiSpec = await openApiToAsyncApi(
          openapi_spec,
          target_version
        );

        return {
          success: true,
          asyncapi_spec: asyncApiSpec,
          metadata: {
            source_format: "openapi",
            target_format: "asyncapi",
            target_version,
          },
        };
      },
    },
    {
      definition: {
        name: "validate_openapi",
        description: "验证OpenAPI规范的有效性",
        inputSchema: {
          type: "object",
          properties: {
            openapi_spec: {
              type: "string",
              description: "OpenAPI规范（JSON或YAML格式）",
            },
          },
          required: ["openapi_spec"],
        },
      },
      handler: async (args: any) => {
        const { openapi_spec } = args;
        const result = await validateOpenApi(openapi_spec);

        return {
          valid: result.valid,
          errors: result.errors,
          warnings: result.warnings || [],
        };
      },
    },
  ];
}

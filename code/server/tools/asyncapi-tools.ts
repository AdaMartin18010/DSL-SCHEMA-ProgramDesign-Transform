/**
 * AsyncAPI转换工具定义
 */

import { Tool } from "../types.js";
import { asyncApiToOpenApi } from
  "../../transformers/asyncapi/asyncapi-to-openapi.js";
import { validateAsyncApi } from "../../utils/validation.js";

/**
 * 注册AsyncAPI相关工具
 */
export async function registerAsyncApiTools(): Promise<Tool[]> {
  return [
    {
      definition: {
        name: "asyncapi_to_openapi",
        description:
          "将AsyncAPI规范转换为OpenAPI规范",
        inputSchema: {
          type: "object",
          properties: {
            asyncapi_spec: {
              type: "string",
              description: "AsyncAPI规范（JSON或YAML格式）",
            },
            target_version: {
              type: "string",
              description: "目标OpenAPI版本（默认：3.1.0）",
              default: "3.1.0",
            },
          },
          required: ["asyncapi_spec"],
        },
      },
      handler: async (args: any) => {
        const { asyncapi_spec, target_version = "3.1.0" } = args;

        // 验证AsyncAPI规范
        const validationResult = await validateAsyncApi(asyncapi_spec);
        if (!validationResult.valid) {
          throw new Error(
            `AsyncAPI规范验证失败: ${validationResult.errors.join(", ")}`
          );
        }

        // 执行转换
        const openApiSpec = await asyncApiToOpenApi(
          asyncapi_spec,
          target_version
        );

        return {
          success: true,
          openapi_spec: openApiSpec,
          metadata: {
            source_format: "asyncapi",
            target_format: "openapi",
            target_version,
          },
        };
      },
    },
    {
      definition: {
        name: "validate_asyncapi",
        description: "验证AsyncAPI规范的有效性",
        inputSchema: {
          type: "object",
          properties: {
            asyncapi_spec: {
              type: "string",
              description: "AsyncAPI规范（JSON或YAML格式）",
            },
          },
          required: ["asyncapi_spec"],
        },
      },
      handler: async (args: any) => {
        const { asyncapi_spec } = args;
        const result = await validateAsyncApi(asyncapi_spec);

        return {
          valid: result.valid,
          errors: result.errors,
          warnings: result.warnings || [],
        };
      },
    },
  ];
}

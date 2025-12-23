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
            conversion_rules: {
              type: "object",
              description: "自定义转换规则（可选）",
            },
          },
          required: ["openapi_spec"],
        },
      },
      handler: async (args: any) => {
        const { openapi_spec, target_version = "3.0.0", conversion_rules } = args;

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
          target_version,
          conversion_rules
        );

        return {
          success: true,
          asyncapi_spec: asyncApiSpec,
          metadata: {
            source_format: "openapi",
            target_format: "asyncapi",
            target_version,
            conversion_rules_applied: !!conversion_rules,
          },
        };
      },
    },
    {
      definition: {
        name: "batch_openapi_to_asyncapi",
        description: "批量将多个OpenAPI规范转换为AsyncAPI规范",
        inputSchema: {
          type: "object",
          properties: {
            openapi_specs: {
              type: "array",
              description: "OpenAPI规范数组",
              items: {
                type: "object",
                properties: {
                  name: { type: "string", description: "规范名称" },
                  spec: { type: "string", description: "OpenAPI规范（JSON或YAML）" },
                },
                required: ["name", "spec"],
              },
            },
            target_version: {
              type: "string",
              description: "目标AsyncAPI版本（默认：3.0.0）",
              default: "3.0.0",
            },
          },
          required: ["openapi_specs"],
        },
      },
      handler: async (args: any) => {
        const { openapi_specs, target_version = "3.0.0" } = args;
        const results = [];

        for (const spec of openapi_specs) {
          try {
            const validationResult = await validateOpenApi(spec.spec);
            if (!validationResult.valid) {
              results.push({
                name: spec.name,
                success: false,
                error: `验证失败: ${validationResult.errors.join(", ")}`,
              });
              continue;
            }

            const asyncApiSpec = await openApiToAsyncApi(
              spec.spec,
              target_version
            );

            results.push({
              name: spec.name,
              success: true,
              asyncapi_spec: asyncApiSpec,
            });
          } catch (error) {
            results.push({
              name: spec.name,
              success: false,
              error: error instanceof Error ? error.message : String(error),
            });
          }
        }

        return {
          success: true,
          results,
          summary: {
            total: openapi_specs.length,
            successful: results.filter((r) => r.success).length,
            failed: results.filter((r) => !r.success).length,
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

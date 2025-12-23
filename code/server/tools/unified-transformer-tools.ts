/**
 * 统一转换框架工具定义
 * 
 * 提供统一的Schema转换接口，支持OpenAPI、AsyncAPI、IoT Schema之间的转换
 */

import { Tool } from "../types.js";
import { openApiToAsyncApi } from "../../transformers/openapi/openapi-to-asyncapi.js";
import { asyncApiToOpenApi } from "../../transformers/asyncapi/asyncapi-to-openapi.js";
import { iotToOpenApi } from "../../transformers/iot/iot-to-openapi.js";
import { openApiToIot } from "../../transformers/iot/openapi-to-iot.js";
import { validateOpenApi } from "../../utils/validation.js";
import { validateAsyncApi } from "../../utils/validation.js";

/**
 * 支持的转换方向
 */
export type ConversionDirection =
  | "openapi_to_asyncapi"
  | "asyncapi_to_openapi"
  | "iot_to_openapi"
  | "openapi_to_iot"
  | "iot_to_asyncapi"
  | "asyncapi_to_iot";

/**
 * 统一转换函数
 */
export async function unifiedTransform(
  sourceFormat: string,
  targetFormat: string,
  sourceSpec: string,
  options?: any
): Promise<any> {
  const direction = `${sourceFormat}_to_${targetFormat}` as ConversionDirection;

  switch (direction) {
    case "openapi_to_asyncapi":
      return await openApiToAsyncApi(
        sourceSpec,
        options?.target_version || "3.0.0",
        options?.conversion_rules
      );

    case "asyncapi_to_openapi":
      return await asyncApiToOpenApi(
        sourceSpec,
        options?.target_version || "3.1.0"
      );

    case "iot_to_openapi":
      return await iotToOpenApi(sourceSpec, options?.device_type);

    case "openapi_to_iot":
      return await openApiToIot(sourceSpec, options?.device_type);

    case "iot_to_asyncapi":
      // IoT -> OpenAPI -> AsyncAPI
      const openApiSpec = await iotToOpenApi(sourceSpec, options?.device_type);
      return await openApiToAsyncApi(
        JSON.stringify(openApiSpec),
        options?.target_version || "3.0.0"
      );

    case "asyncapi_to_iot":
      // AsyncAPI -> OpenAPI -> IoT
      const openApiFromAsync = await asyncApiToOpenApi(
        sourceSpec,
        options?.target_version || "3.1.0"
      );
      return await openApiToIot(
        JSON.stringify(openApiFromAsync),
        options?.device_type
      );

    default:
      throw new Error(`不支持的转换方向: ${direction}`);
  }
}

/**
 * 注册统一转换工具
 */
export async function registerUnifiedTransformerTools(): Promise<Tool[]> {
  return [
    {
      definition: {
        name: "unified_schema_transform",
        description:
          "统一的Schema转换工具，支持OpenAPI、AsyncAPI、IoT Schema之间的任意转换",
        inputSchema: {
          type: "object",
          properties: {
            source_format: {
              type: "string",
              description: "源格式：openapi、asyncapi、iot",
              enum: ["openapi", "asyncapi", "iot"],
            },
            target_format: {
              type: "string",
              description: "目标格式：openapi、asyncapi、iot",
              enum: ["openapi", "asyncapi", "iot"],
            },
            source_spec: {
              type: "string",
              description: "源Schema规范（JSON或YAML格式）",
            },
            options: {
              type: "object",
              description: "转换选项（可选）",
              properties: {
                target_version: {
                  type: "string",
                  description: "目标版本",
                },
                device_type: {
                  type: "string",
                  description: "设备类型（IoT转换时使用）",
                },
                conversion_rules: {
                  type: "object",
                  description: "自定义转换规则",
                },
              },
            },
          },
          required: ["source_format", "target_format", "source_spec"],
        },
      },
      handler: async (args: any) => {
        const {
          source_format,
          target_format,
          source_spec,
          options = {},
        } = args;

        // 验证源格式
        if (source_format === "openapi") {
          const validationResult = await validateOpenApi(source_spec);
          if (!validationResult.valid) {
            throw new Error(
              `OpenAPI规范验证失败: ${validationResult.errors.join(", ")}`
            );
          }
        } else if (source_format === "asyncapi") {
          const validationResult = await validateAsyncApi(source_spec);
          if (!validationResult.valid) {
            throw new Error(
              `AsyncAPI规范验证失败: ${validationResult.errors.join(", ")}`
            );
          }
        }

        // 执行转换
        const result = await unifiedTransform(
          source_format,
          target_format,
          source_spec,
          options
        );

        return {
          success: true,
          result,
          metadata: {
            source_format,
            target_format,
            conversion_direction: `${source_format}_to_${target_format}`,
            options_applied: Object.keys(options).length > 0,
          },
        };
      },
    },
    {
      definition: {
        name: "get_supported_conversions",
        description: "获取支持的转换方向列表",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
      handler: async () => {
        return {
          supported_conversions: [
            "openapi_to_asyncapi",
            "asyncapi_to_openapi",
            "iot_to_openapi",
            "openapi_to_iot",
            "iot_to_asyncapi",
            "asyncapi_to_iot",
          ],
          supported_formats: ["openapi", "asyncapi", "iot"],
          openapi_versions: ["3.0.0", "3.0.1", "3.0.2", "3.1.0"],
          asyncapi_versions: ["2.0.0", "2.1.0", "2.2.0", "2.3.0", "2.4.0", "2.5.0", "2.6.0", "3.0.0"],
        };
      },
    },
  ];
}

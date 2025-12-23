/**
 * IoT Schema转换工具定义
 */

import { Tool } from "../types.js";
import { iotToOpenApi } from "../../transformers/iot/iot-to-openapi.js";
import { openApiToIot } from "../../transformers/iot/openapi-to-iot.js";

/**
 * 注册IoT Schema相关工具
 */
export async function registerIoTools(): Promise<Tool[]> {
  return [
    {
      definition: {
        name: "iot_to_openapi",
        description:
          "将IoT Schema转换为OpenAPI规范",
        inputSchema: {
          type: "object",
          properties: {
            iot_schema: {
              type: "string",
              description: "IoT Schema（JSON格式）",
            },
            device_type: {
              type: "string",
              description: "设备类型（sensor, actuator, gateway等）",
            },
            protocol: {
              type: "string",
              description: "IoT协议（mqtt, coap, http等）",
              enum: ["mqtt", "coap", "http", "websocket"],
            },
          },
          required: ["iot_schema"],
        },
      },
      handler: async (args: any) => {
        const { iot_schema, device_type, protocol } = args;

        // 验证IoT Schema
        try {
          const schema = JSON.parse(iot_schema);
          if (!schema.deviceId || !schema.capabilities) {
            throw new Error("IoT Schema必须包含deviceId和capabilities字段");
          }
        } catch (error) {
          throw new Error(`IoT Schema格式错误: ${error instanceof Error ? error.message : String(error)}`);
        }

        // 执行转换
        const openApiSpec = await iotToOpenApi(iot_schema, device_type);

        return {
          success: true,
          openapi_spec: openApiSpec,
          metadata: {
            source_format: "iot",
            target_format: "openapi",
            device_type,
            protocol: protocol || "mqtt",
          },
        };
      },
    },
    {
      definition: {
        name: "openapi_to_iot",
        description:
          "将OpenAPI规范转换为IoT Schema",
        inputSchema: {
          type: "object",
          properties: {
            openapi_spec: {
              type: "string",
              description: "OpenAPI规范（JSON或YAML格式）",
            },
            device_type: {
              type: "string",
              description: "目标设备类型",
            },
          },
          required: ["openapi_spec"],
        },
      },
      handler: async (args: any) => {
        const { openapi_spec, device_type } = args;

        // 执行转换
        const iotSchema = await openApiToIot(openapi_spec, device_type);

        return {
          success: true,
          iot_schema: iotSchema,
          metadata: {
            source_format: "openapi",
            target_format: "iot",
            device_type,
          },
        };
      },
    },
    {
      definition: {
        name: "validate_iot_schema",
        description: "验证IoT Schema的有效性",
        inputSchema: {
          type: "object",
          properties: {
            iot_schema: {
              type: "string",
              description: "IoT Schema（JSON格式）",
            },
          },
          required: ["iot_schema"],
        },
      },
      handler: async (args: any) => {
        const { iot_schema } = args;
        const errors: string[] = [];
        const warnings: string[] = [];

        try {
          const schema = JSON.parse(iot_schema);

          // 验证必需字段
          if (!schema.deviceId) {
            errors.push("缺少必需字段: deviceId");
          }
          if (!schema.capabilities) {
            errors.push("缺少必需字段: capabilities");
          } else if (!Array.isArray(schema.capabilities)) {
            errors.push("capabilities必须是数组");
          }

          // 验证设备类型
          if (schema.deviceType && !["sensor", "actuator", "gateway"].includes(schema.deviceType)) {
            warnings.push(`未知的设备类型: ${schema.deviceType}`);
          }

          return {
            valid: errors.length === 0,
            errors,
            warnings,
          };
        } catch (error) {
          return {
            valid: false,
            errors: [`JSON解析错误: ${error instanceof Error ? error.message : String(error)}`],
            warnings: [],
          };
        }
      },
    },
  ];
}

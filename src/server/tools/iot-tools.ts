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
          },
          required: ["iot_schema"],
        },
      },
      handler: async (args: any) => {
        const { iot_schema, device_type } = args;

        // 执行转换
        const openApiSpec = await iotToOpenApi(iot_schema, device_type);

        return {
          success: true,
          openapi_spec: openApiSpec,
          metadata: {
            source_format: "iot",
            target_format: "openapi",
            device_type,
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
  ];
}

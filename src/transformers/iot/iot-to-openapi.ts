/**
 * IoT Schema到OpenAPI转换器
 * 
 * 实现IoT Schema到OpenAPI规范的转换逻辑
 */

import { parseYamlOrJson } from "../../utils/parser.js";

/**
 * 将IoT Schema转换为OpenAPI规范
 * 
 * @param iotSchema IoT Schema（JSON字符串）
 * @param deviceType 设备类型
 * @returns OpenAPI规范对象
 */
export async function iotToOpenApi(
  iotSchema: string,
  deviceType?: string
): Promise<any> {
  // 解析IoT Schema
  const iot = parseYamlOrJson(iotSchema);

  // 构建OpenAPI规范基础结构
  const openApi: any = {
    openapi: "3.1.0",
    info: {
      title: iot.device?.name || "IoT Device API",
      version: iot.device?.version || "1.0.0",
      description: `IoT设备API - ${deviceType || "未知设备类型"}`,
    },
    servers: [
      {
        url: iot.device?.endpoint || "http://localhost:8080",
        description: "IoT设备端点",
      },
    ],
    paths: convertIoTPropertiesToPaths(iot.properties, deviceType),
    components: {
      schemas: convertIoTPropertiesToSchemas(iot.properties),
    },
  };

  return openApi;
}

/**
 * 转换IoT属性为API路径
 */
function convertIoTPropertiesToPaths(
  properties?: Record<string, any>,
  deviceType?: string
): any {
  if (!properties) {
    return {};
  }

  const paths: Record<string, any> = {};

  // 为每个属性创建对应的API端点
  for (const [key, prop] of Object.entries(properties)) {
    const path = `/api/${deviceType || "device"}/${key}`;

    paths[path] = {
      get: {
        operationId: `get_${key}`,
        summary: `获取${key}属性`,
        description: prop.description || `获取设备属性: ${key}`,
        responses: {
          "200": {
            description: "成功",
            content: {
              "application/json": {
                schema: {
                  type: prop.type || "string",
                  description: prop.description,
                },
              },
            },
          },
        },
      },
    };

    // 如果属性可写，添加PUT端点
    if (prop.writable !== false) {
      paths[path].put = {
        operationId: `set_${key}`,
        summary: `设置${key}属性`,
        description: prop.description || `设置设备属性: ${key}`,
        requestBody: {
          content: {
            "application/json": {
              schema: {
                type: prop.type || "string",
                description: prop.description,
              },
            },
          },
        },
        responses: {
          "200": {
            description: "成功",
          },
        },
      };
    }
  }

  return paths;
}

/**
 * 转换IoT属性为Schema定义
 */
function convertIoTPropertiesToSchemas(
  properties?: Record<string, any>
): Record<string, any> {
  if (!properties) {
    return {};
  }

  const schemas: Record<string, any> = {};

  for (const [key, prop] of Object.entries(properties)) {
    schemas[key] = {
      type: prop.type || "string",
      description: prop.description,
      ...(prop.unit && { unit: prop.unit }),
      ...(prop.min !== undefined && { minimum: prop.min }),
      ...(prop.max !== undefined && { maximum: prop.max }),
    };
  }

  return schemas;
}

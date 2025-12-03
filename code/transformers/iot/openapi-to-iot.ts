/**
 * OpenAPI到IoT Schema转换器
 * 
 * 实现OpenAPI规范到IoT Schema的转换逻辑
 */

import { parseYamlOrJson } from "../../utils/parser.js";

/**
 * 将OpenAPI规范转换为IoT Schema
 * 
 * @param openApiSpec OpenAPI规范（JSON或YAML字符串）
 * @param deviceType 设备类型
 * @returns IoT Schema对象
 */
export async function openApiToIot(
  openApiSpec: string,
  deviceType?: string
): Promise<any> {
  // 解析OpenAPI规范
  const openApi = parseYamlOrJson(openApiSpec);

  // 从路径中提取设备属性
  const properties = extractPropertiesFromPaths(openApi.paths);

  // 构建IoT Schema
  const iotSchema: any = {
    device: {
      name: openApi.info?.title || "IoT Device",
      version: openApi.info?.version || "1.0.0",
      type: deviceType || "generic",
      endpoint: openApi.servers?.[0]?.url || "http://localhost:8080",
    },
    properties: properties,
    metadata: {
      converted_from: "openapi",
      openapi_version: openApi.openapi,
    },
  };

  return iotSchema;
}

/**
 * 从OpenAPI路径中提取设备属性
 */
function extractPropertiesFromPaths(paths?: any): Record<string, any> {
  if (!paths) {
    return {};
  }

  const properties: Record<string, any> = {};

  for (const [path, pathItem] of Object.entries(paths as any)) {
    // 解析路径，提取属性名
    // 假设路径格式为 /api/device/{propertyName}
    const match = path.match(/\/api\/\w+\/(\w+)/);
    if (!match) continue;

    const propertyName = match[1];

    // 从GET操作中提取属性定义
    if (pathItem.get) {
      const getOp = pathItem.get;
      const responseSchema =
        getOp.responses?.["200"]?.content?.["application/json"]?.schema;

      properties[propertyName] = {
        type: responseSchema?.type || "string",
        description: getOp.summary || getOp.description,
        readable: true,
        writable: !!pathItem.put || !!pathItem.post,
      };
    }

    // 从PUT操作中提取可写属性
    if (pathItem.put) {
      const putOp = pathItem.put;
      const requestSchema =
        putOp.requestBody?.content?.["application/json"]?.schema;

      if (!properties[propertyName]) {
        properties[propertyName] = {
          type: requestSchema?.type || "string",
          description: putOp.summary || putOp.description,
          readable: false,
          writable: true,
        };
      } else {
        properties[propertyName].writable = true;
        if (requestSchema?.type) {
          properties[propertyName].type = requestSchema.type;
        }
      }
    }
  }

  return properties;
}

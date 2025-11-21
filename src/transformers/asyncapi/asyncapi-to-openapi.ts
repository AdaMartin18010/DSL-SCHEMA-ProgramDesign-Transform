/**
 * AsyncAPI到OpenAPI转换器
 * 
 * 实现AsyncAPI规范到OpenAPI规范的转换逻辑
 */

import { parseYamlOrJson } from "../../utils/parser.js";

/**
 * 将AsyncAPI规范转换为OpenAPI规范
 * 
 * @param asyncApiSpec AsyncAPI规范（JSON或YAML字符串）
 * @param targetVersion 目标OpenAPI版本
 * @returns OpenAPI规范对象
 */
export async function asyncApiToOpenApi(
  asyncApiSpec: string,
  targetVersion: string = "3.1.0"
): Promise<any> {
  // 解析AsyncAPI规范
  const asyncApi = parseYamlOrJson(asyncApiSpec);

  // 构建OpenAPI规范基础结构
  const openApi: any = {
    openapi: targetVersion,
    info: {
      title: asyncApi.info?.title || "Converted API",
      version: asyncApi.info?.version || "1.0.0",
      description: asyncApi.info?.description || "",
    },
    servers: convertServers(asyncApi.servers),
    paths: convertChannelsToPaths(asyncApi.channels),
    components: convertComponents(asyncApi.components),
  };

  return openApi;
}

/**
 * 转换服务器定义
 */
function convertServers(servers?: Record<string, any>): any[] {
  if (!servers) {
    return [
      {
        url: "http://localhost:8080",
        description: "Default server",
      },
    ];
  }

  return Object.entries(servers).map(([key, server]) => ({
    url: server.url,
    description: server.description || key,
  }));
}

/**
 * 转换通道为路径
 */
function convertChannelsToPaths(channels?: Record<string, any>): any {
  if (!channels) {
    return {};
  }

  const paths: Record<string, any> = {};

  for (const [channelKey, channel] of Object.entries(channels)) {
    // 解析通道键（格式：METHOD /path）
    const match = channelKey.match(/^(\w+)\s+(.+)$/);
    if (!match) continue;

    const [, method, path] = match;
    const lowerMethod = method.toLowerCase();

    if (!paths[path]) {
      paths[path] = {};
    }

    // 构建操作对象
    const operation: any = {
      operationId: channel.publish?.operationId ||
        channel.subscribe?.operationId ||
        `${lowerMethod}_${path.replace(/\//g, "_")}`,
      summary: channel.publish?.summary || channel.subscribe?.summary,
      description:
        channel.publish?.description || channel.subscribe?.description,
    };

    // 处理请求体（publish消息）
    if (channel.publish?.message) {
      if (channel.publish.message.payload) {
        operation.requestBody = {
          content: {
            "application/json": {
              schema: channel.publish.message.payload,
            },
          },
        };
      }
    }

    // 处理响应（subscribe消息）
    if (channel.subscribe?.message) {
      operation.responses = {
        "200": {
          description: "Success",
          content: {
            "application/json": {
              schema: channel.subscribe.message.payload || {},
            },
          },
        },
      };
    } else {
      operation.responses = {
        "200": {
          description: "Success",
        },
      };
    }

    paths[path][lowerMethod] = operation;
  }

  return paths;
}

/**
 * 转换组件定义
 */
function convertComponents(components?: any): any {
  if (!components) {
    return {};
  }

  return {
    schemas: components.schemas || {},
    parameters: components.parameters || {},
    securitySchemes: components.securitySchemes || {},
  };
}

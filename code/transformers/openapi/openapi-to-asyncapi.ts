/**
 * OpenAPI到AsyncAPI转换器
 * 
 * 实现OpenAPI规范到AsyncAPI规范的转换逻辑
 */

import { parseYamlOrJson } from "../../utils/parser.js";

/**
 * 将OpenAPI规范转换为AsyncAPI规范
 * 
 * @param openApiSpec OpenAPI规范（JSON或YAML字符串）
 * @param targetVersion 目标AsyncAPI版本
 * @param conversionRules 自定义转换规则（可选）
 * @returns AsyncAPI规范对象
 */
export async function openApiToAsyncApi(
  openApiSpec: string,
  targetVersion: string = "3.0.0",
  conversionRules?: any
): Promise<any> {
  // 解析OpenAPI规范
  const openApi = parseYamlOrJson(openApiSpec);

  // 构建AsyncAPI规范基础结构
  const asyncApi: any = {
    asyncapi: targetVersion,
    info: {
      title: openApi.info?.title || "Converted API",
      version: openApi.info?.version || "1.0.0",
      description: openApi.info?.description || "",
    },
    servers: convertServers(openApi.servers, conversionRules),
    channels: convertPathsToChannels(openApi.paths, conversionRules),
    components: convertComponents(openApi.components),
  };

  // 应用自定义转换规则
  if (conversionRules) {
    applyConversionRules(asyncApi, conversionRules);
  }

  return asyncApi;
}

/**
 * 应用自定义转换规则
 */
function applyConversionRules(asyncApi: any, rules: any): void {
  if (rules.channel_mapping) {
    // 应用通道映射规则
    const newChannels: Record<string, any> = {};
    for (const [oldKey, newKey] of Object.entries(rules.channel_mapping)) {
      if (asyncApi.channels[oldKey]) {
        newChannels[newKey as string] = asyncApi.channels[oldKey];
      }
    }
    asyncApi.channels = { ...asyncApi.channels, ...newChannels };
  }

  if (rules.server_protocols) {
    // 应用服务器协议规则
    for (const [serverName, protocol] of Object.entries(rules.server_protocols)) {
      if (asyncApi.servers[serverName]) {
        asyncApi.servers[serverName].protocol = protocol;
      }
    }
  }
}

/**
 * 转换服务器定义
 */
function convertServers(servers?: any[], conversionRules?: any): Record<string, any> {
  if (!servers || servers.length === 0) {
    return {
      production: {
        url: "http://localhost:8080",
        protocol: "http",
      },
    };
  }

  const result: Record<string, any> = {};
  servers.forEach((server, index) => {
    const key = server.description || `server${index}`;
    result[key] = {
      url: server.url,
      protocol: extractProtocol(server.url),
      description: server.description,
    };
  });

  return result;
}

/**
 * 转换路径为通道
 */
function convertPathsToChannels(paths?: any, conversionRules?: any): Record<string, any> {
  if (!paths) {
    return {};
  }

  const channels: Record<string, any> = {};

  for (const [path, pathItem] of Object.entries(paths as any)) {
    // 为每个HTTP方法创建对应的通道
    const methods = ["get", "post", "put", "delete", "patch"];
    for (const method of methods) {
      if (pathItem[method]) {
        const operation = pathItem[method];
        const channelKey = `${method.toUpperCase()} ${path}`;

        channels[channelKey] = {
          publish: method === "get" ? undefined : {
            message: {
              payload: operation.requestBody?.content?.["application/json"]
                ?.schema || {},
              headers: operation.parameters
                ?.filter((p: any) => p.in === "header")
                .reduce((acc: any, p: any) => {
                  acc[p.name] = p.schema || {};
                  return acc;
                }, {}),
            },
            operationId: operation.operationId,
            summary: operation.summary,
            description: operation.description,
          },
          subscribe: method === "get" ? {
            message: {
              payload: operation.responses?.["200"]?.content?.["application/json"]
                ?.schema || {},
            },
            operationId: operation.operationId,
            summary: operation.summary,
            description: operation.description,
          } : undefined,
        };
      }
    }
  }

  return channels;
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
    messages: {},
    parameters: components.parameters || {},
    securitySchemes: components.securitySchemes || {},
  };
}

/**
 * 从URL提取协议
 */
function extractProtocol(url: string): string {
  if (url.startsWith("https://")) return "https";
  if (url.startsWith("http://")) return "http";
  if (url.startsWith("ws://")) return "ws";
  if (url.startsWith("wss://")) return "wss";
  return "http";
}

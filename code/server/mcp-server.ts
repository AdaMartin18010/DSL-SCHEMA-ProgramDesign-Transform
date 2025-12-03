/**
 * MCP Server核心实现
 * 
 * 提供Schema转换的MCP工具接口
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { registerOpenApiTools } from "./tools/openapi-tools.js";
import { registerAsyncApiTools } from "./tools/asyncapi-tools.js";
import { registerIoTools } from "./tools/iot-tools.js";

/**
 * 创建并配置MCP Server
 */
export function createMcpServer(): Server {
  const server = new Server(
    {
      name: "mcp-schema-transformer",
      version: "1.0.0",
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  // 注册工具列表处理器
  server.setRequestHandler(ListToolsRequestSchema, async () => {
    const tools = [
      ...(await registerOpenApiTools()).map((t) => t.definition),
      ...(await registerAsyncApiTools()).map((t) => t.definition),
      ...(await registerIoTools()).map((t) => t.definition),
    ];

    return { tools };
  });

  // 注册工具调用处理器
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    // 查找并执行对应的工具
    const allTools = [
      ...(await registerOpenApiTools()),
      ...(await registerAsyncApiTools()),
      ...(await registerIoTools()),
    ];

    const tool = allTools.find((t) => t.definition.name === name);

    if (!tool) {
      throw new Error(`未知工具: ${name}`);
    }

    try {
      const result = await tool.handler(args);
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `错误: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
        isError: true,
      };
    }
  });

  return server;
}

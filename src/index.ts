#!/usr/bin/env node

/**
 * MCP Schema转换服务器入口文件
 * 
 * 实现基于MCP协议的Schema转换功能，支持：
 * - OpenAPI ↔ AsyncAPI双向转换
 * - IoT Schema集成转换
 * - 统一转换框架
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from
  "@modelcontextprotocol/sdk/server/stdio.js";
import { createMcpServer } from "./server/mcp-server.js";

/**
 * 主函数：启动MCP Server
 */
async function main() {
  // 创建MCP Server实例
  const server = createMcpServer();

  // 创建stdio传输层
  const transport = new StdioServerTransport();

  // 连接Server和Transport
  await server.connect(transport);

  console.error("MCP Schema转换服务器已启动");
}

// 启动服务器
main().catch((error) => {
  console.error("服务器启动失败:", error);
  process.exit(1);
});

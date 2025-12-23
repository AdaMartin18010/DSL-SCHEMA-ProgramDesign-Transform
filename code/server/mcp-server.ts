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
import { registerUnifiedTransformerTools } from "./tools/unified-transformer-tools.js";
import { ConnectionPool } from "./performance/connection-pool.js";
import { BatchProcessor } from "./performance/batch-processor.js";
import { CacheManager } from "./performance/cache-manager.js";
import { PerformanceMonitor } from "./performance/performance-monitor.js";

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

  // 初始化性能优化组件
  const connectionPool = new ConnectionPool({
    minSize: 5,
    maxSize: 20,
    idleTimeout: 30000,
  });

  const batchProcessor = new BatchProcessor({
    batchSize: 10,
    batchWindow: 100,
  });

  const cacheManager = new CacheManager({
    maxSize: 1000,
    defaultTTL: 3600000, // 1小时
    strategy: 'LRU',
  });

  const performanceMonitor = new PerformanceMonitor();

  // 注册工具列表处理器
  server.setRequestHandler(ListToolsRequestSchema, async () => {
    const tools = [
      ...(await registerOpenApiTools()).map((t) => t.definition),
      ...(await registerAsyncApiTools()).map((t) => t.definition),
      ...(await registerIoTools()).map((t) => t.definition),
      ...(await registerUnifiedTransformerTools()).map((t) => t.definition),
    ];

    return { tools };
  });

  // 注册工具调用处理器（带性能优化）
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    // 性能监控：记录请求开始
    const recordEnd = performanceMonitor.recordRequestStart();

    try {
      // 获取连接
      const connection = await connectionPool.acquire();

      try {
        // 检查缓存
        const cacheKey = CacheManager.generateKey(name, args);
        const cachedResult = cacheManager.get(cacheKey);

        if (cachedResult) {
          recordEnd();
          performanceMonitor.recordSuccess();
          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(cachedResult, null, 2),
              },
            ],
          };
        }

        // 查找并执行对应的工具
        const allTools = [
          ...(await registerOpenApiTools()),
          ...(await registerAsyncApiTools()),
          ...(await registerIoTools()),
          ...(await registerUnifiedTransformerTools()),
        ];

        const tool = allTools.find((t) => t.definition.name === name);

        if (!tool) {
          throw new Error(`未知工具: ${name}`);
        }

        // 执行工具处理函数
        const result = await tool.handler(args);

        // 缓存结果
        cacheManager.set(cacheKey, result);

        recordEnd();
        performanceMonitor.recordSuccess();

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      } finally {
        // 释放连接
        connectionPool.release(connection.id);
      }
    } catch (error) {
      recordEnd();
      performanceMonitor.recordError();

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

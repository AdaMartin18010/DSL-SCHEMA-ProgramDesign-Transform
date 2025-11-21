/**
 * MCP Server类型定义
 */

import { Tool as McpTool } from "@modelcontextprotocol/sdk/types.js";

/**
 * 工具定义
 */
export interface Tool {
  definition: McpTool;
  handler: (args: any) => Promise<any>;
}

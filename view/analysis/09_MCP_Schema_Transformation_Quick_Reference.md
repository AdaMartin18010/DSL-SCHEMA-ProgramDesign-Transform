# MCP Schema转换快速参考指南

## 📑 目录

- [MCP Schema转换快速参考指南](#mcp-schema转换快速参考指南)
  - [📑 目录](#-目录)
  - [1. 快速开始](#1-快速开始)
    - [1.1 5分钟搭建MCP Server](#11-5分钟搭建mcp-server)
    - [1.2 基础转换工具](#12-基础转换工具)
  - [2. 常用代码片段](#2-常用代码片段)
    - [2.1 OpenAPI解析](#21-openapi解析)
    - [2.2 AsyncAPI生成](#22-asyncapi生成)
    - [2.3 IoT Schema处理](#23-iot-schema处理)
  - [3. 转换规则速查](#3-转换规则速查)
    - [3.1 OpenAPI → AsyncAPI](#31-openapi--asyncapi)
    - [3.2 AsyncAPI → OpenAPI](#32-asyncapi--openapi)
    - [3.3 IoT Schema → OpenAPI](#33-iot-schema--openapi)
  - [4. MCP工具定义模板](#4-mcp工具定义模板)
    - [4.1 基础工具模板](#41-基础工具模板)
    - [4.2 批量转换工具](#42-批量转换工具)
    - [4.3 验证工具](#43-验证工具)
  - [5. 错误处理模式](#5-错误处理模式)
    - [5.1 输入验证](#51-输入验证)
    - [5.2 转换错误](#52-转换错误)
    - [5.3 超时处理](#53-超时处理)
  - [6. 性能优化技巧](#6-性能优化技巧)
    - [6.1 缓存策略](#61-缓存策略)
    - [6.2 并行处理](#62-并行处理)
    - [6.3 增量转换](#63-增量转换)
  - [7. 调试命令](#7-调试命令)
    - [7.1 日志级别](#71-日志级别)
    - [7.2 性能分析](#72-性能分析)
    - [7.3 测试工具](#73-测试工具)
  - [8. 常见问题速查](#8-常见问题速查)
    - [8.1 转换失败](#81-转换失败)
    - [8.2 性能问题](#82-性能问题)
    - [8.3 兼容性问题](#83-兼容性问题)
  - [9. 实用工具函数](#9-实用工具函数)
    - [9.1 Schema类型检测](#91-schema类型检测)
    - [9.2 资源名提取](#92-资源名提取)
    - [9.3 内容哈希](#93-内容哈希)
  - [10. 参考链接](#10-参考链接)

---

## 1. 快速开始

### 1.1 5分钟搭建MCP Server

**最小化实现**：

```typescript
// package.json
{
  "name": "mcp-schema-transformer",
  "version": "1.0.0",
  "type": "module",
  "dependencies": {
    "@modelcontextprotocol/sdk": "^0.5.0"
  }
}

// index.ts
import { Server } from
  "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from
  "@modelcontextprotocol/sdk/server/stdio.js";

const server = new Server(
  { name: "schema-transformer", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(
  ListToolsRequestSchema,
  async () => ({
    tools: [{
      name: "transform",
      description: "转换Schema",
      inputSchema: {
        type: "object",
        properties: {
          source: { type: "string" },
          target: { type: "string" },
        },
      },
    }],
  })
);

const transport = new StdioServerTransport();
await server.connect(transport);
```

### 1.2 基础转换工具

**OpenAPI → AsyncAPI**：

```typescript
function openapiToAsyncAPI(openapi: any): any {
  return {
    asyncapi: "3.0.0",
    info: {
      title: openapi.info.title,
      version: openapi.info.version,
    },
    channels: extractChannels(openapi.paths),
  };
}

function extractChannels(paths: any): any {
  const channels: any = {};
  for (const [path, methods] of Object.entries(paths)) {
    for (const [method, op] of Object.entries(methods)) {
      if (method === "post") {
        const eventName = `${extractResource(path)}.created`;
        channels[eventName] = {
          publish: {
            message: {
              payload: op.requestBody?.content?.["application/json"]?.schema,
            },
          },
        };
      }
    }
  }
  return channels;
}
```

---

## 2. 常用代码片段

### 2.1 OpenAPI解析

**解析和验证**：

```typescript
import Ajv from "ajv";
import openapiSchema from "openapi-schema-validation";

function parseOpenAPI(spec: string): any {
  const parsed = JSON.parse(spec);

  // 验证格式
  const ajv = new Ajv();
  const valid = ajv.validate(openapiSchema, parsed);
  if (!valid) {
    throw new Error(`OpenAPI验证失败: ${ajv.errorsText()}`);
  }

  return parsed;
}
```

**提取路径信息**：

```typescript
function extractPaths(openapi: any): Array<{
  path: string;
  method: string;
  operation: any;
}> {
  const results = [];
  for (const [path, methods] of Object.entries(openapi.paths)) {
    for (const [method, operation] of Object.entries(methods)) {
      if (["get", "post", "put", "delete", "patch"].includes(method)) {
        results.push({ path, method, operation });
      }
    }
  }
  return results;
}
```

### 2.2 AsyncAPI生成

**生成基础AsyncAPI**：

```typescript
function generateAsyncAPI(
  title: string,
  version: string,
  channels: any
): any {
  return {
    asyncapi: "3.0.0",
    info: { title, version },
    channels,
    servers: {
      production: {
        url: "mqtt://broker.example.com",
        protocol: "mqtt",
      },
    },
  };
}
```

**添加MQTT绑定**：

```typescript
function addMQTTBinding(channel: any, topic: string): any {
  return {
    ...channel,
    bindings: {
      mqtt: {
        topic,
        qos: 1,
        retain: false,
      },
    },
  };
}
```

### 2.3 IoT Schema处理

**解析IoT扩展字段**：

```typescript
function extractIoTMetadata(openapi: any): any {
  const iotPaths = [];
  for (const [path, methods] of Object.entries(openapi.paths)) {
    for (const [method, operation] of Object.entries(methods)) {
      if (operation["x-iot"]) {
        iotPaths.push({
          path,
          method,
          iot: operation["x-iot"],
        });
      }
    }
  }
  return iotPaths;
}
```

**生成MQTT主题**：

```typescript
function generateMQTTTopic(
  path: string,
  params: Record<string, string>
): string {
  let topic = path;
  for (const [key, value] of Object.entries(params)) {
    topic = topic.replace(`{${key}}`, value);
  }
  return topic.replace(/\//g, ".");
}
```

---

## 3. 转换规则速查

### 3.1 OpenAPI → AsyncAPI

| OpenAPI元素 | AsyncAPI元素 | 转换规则 |
|-----------|------------|---------|
| `POST /users` | `user.created` | 资源名 + `.created` |
| `GET /users/{id}` | `user.read` | 资源名 + `.read` |
| `PUT /users/{id}` | `user.updated` | 资源名 + `.updated` |
| `DELETE /users/{id}` | `user.deleted` | 资源名 + `.deleted` |
| `requestBody` | `message.payload` | 直接映射 |
| `parameters` | `message.headers` | 转换为消息头 |

**代码实现**：

```typescript
const methodToAction: Record<string, string> = {
  post: "created",
  get: "read",
  put: "updated",
  delete: "deleted",
  patch: "patched",
};

function mapToEvent(path: string, method: string): string {
  const resource = extractResource(path);
  const action = methodToAction[method.toLowerCase()] || "unknown";
  return `${resource}.${action}`;
}
```

### 3.2 AsyncAPI → OpenAPI

| AsyncAPI元素 | OpenAPI元素 | 转换规则 |
|------------|-----------|---------|
| `user.created` | `POST /users` | 事件名 → REST操作 |
| `user.updated` | `PUT /users/{id}` | 事件名 → REST操作 |
| `message.payload` | `requestBody` | 直接映射 |
| `channel.bindings.mqtt` | `x-mqtt-binding` | 扩展字段保存 |

### 3.3 IoT Schema → OpenAPI

| IoT元素 | OpenAPI元素 | 转换规则 |
|--------|-----------|---------|
| `x-iot.topic` | `path` | MQTT主题 → REST路径 |
| `x-iot.protocol` | `x-protocol` | 协议信息保存 |
| `x-iot.qos` | `x-qos` | QoS信息保存 |

---

## 4. MCP工具定义模板

### 4.1 基础工具模板

```typescript
server.setRequestHandler(
  CallToolRequestSchema,
  async (request) => {
    const { name, arguments: args } = request.params;

    switch (name) {
      case "transform_openapi_to_asyncapi":
        return {
          content: [{
            type: "text",
            text: JSON.stringify(
              await transformOpenAPIToAsyncAPI(args.openapi_spec),
              null,
              2
            ),
          }],
        };

      default:
        throw new Error(`未知工具: ${name}`);
    }
  }
);
```

### 4.2 批量转换工具

```typescript
{
  name: "batch_transform",
  description: "批量转换多个Schema",
  inputSchema: {
    type: "object",
    properties: {
      schemas: {
        type: "array",
        items: {
          type: "object",
          properties: {
            source: { type: "string" },
            target: { type: "string" },
            content: { type: "string" },
          },
        },
      },
    },
  },
}
```

### 4.3 验证工具

```typescript
{
  name: "validate_schema",
  description: "验证Schema格式",
  inputSchema: {
    type: "object",
    properties: {
      schema_type: {
        type: "string",
        enum: ["openapi", "asyncapi", "iot"],
      },
      schema_content: { type: "string" },
    },
  },
}
```

---

## 5. 错误处理模式

### 5.1 输入验证

```typescript
function validateInput(
  input: any,
  schema: any
): void {
  const ajv = new Ajv();
  const validate = ajv.compile(schema);

  if (!validate(input)) {
    throw new Error(
      `输入验证失败: ${ajv.errorsText(validate.errors)}`
    );
  }
}
```

### 5.2 转换错误

```typescript
async function safeTransform(
  transformFn: () => Promise<any>
): Promise<{ success: boolean; data?: any; error?: string }> {
  try {
    const data = await transformFn();
    return { success: true, data };
  } catch (error) {
    logger.error("转换失败", { error });
    return {
      success: false,
      error: error instanceof Error ? error.message : String(error),
    };
  }
}
```

### 5.3 超时处理

```typescript
async function transformWithTimeout(
  transformFn: () => Promise<any>,
  timeoutMs: number = 5000
): Promise<any> {
  return Promise.race([
    transformFn(),
    new Promise((_, reject) =>
      setTimeout(
        () => reject(new Error("转换超时")),
        timeoutMs
      )
    ),
  ]);
}
```

---

## 6. 性能优化技巧

### 6.1 缓存策略

```typescript
import { LRUCache } from "lru-cache";

const cache = new LRUCache<string, any>({
  max: 1000,
  ttl: 3600000, // 1小时
});

async function transformWithCache(
  source: string,
  target: string,
  content: string
): Promise<any> {
  const cacheKey = `${source}-${target}-${hash(content)}`;

  const cached = cache.get(cacheKey);
  if (cached) {
    return cached;
  }

  const result = await transform(source, target, content);
  cache.set(cacheKey, result);
  return result;
}
```

### 6.2 并行处理

```typescript
async function parallelTransform(
  schemas: Array<{ source: string; target: string; content: string }>
): Promise<any[]> {
  return Promise.all(
    schemas.map(s => transform(s.source, s.target, s.content))
  );
}
```

### 6.3 增量转换

```typescript
function incrementalTransform(
  oldSchema: any,
  newSchema: any,
  target: string
): any {
  const diff = computeDiff(oldSchema, newSchema);
  const oldTransformed = transform(oldSchema, target);
  return applyDiff(oldTransformed, diff, target);
}
```

---

## 7. 调试命令

### 7.1 日志级别

```typescript
const LOG_LEVEL = process.env.LOG_LEVEL || "info";

function log(level: string, message: string, data?: any) {
  const levels = ["debug", "info", "warn", "error"];
  if (levels.indexOf(level) >= levels.indexOf(LOG_LEVEL)) {
    console.log(`[${level.toUpperCase()}] ${message}`, data);
  }
}
```

### 7.2 性能分析

```typescript
function withTiming<T>(
  name: string,
  fn: () => Promise<T>
): Promise<T> {
  const start = performance.now();
  return fn().finally(() => {
    const duration = performance.now() - start;
    log("debug", `[${name}] 耗时: ${duration}ms`);
  });
}
```

### 7.3 测试工具

```typescript
// 测试转换函数
async function testTransform() {
  const testCases = [
    {
      input: { openapi: "3.0.0", paths: { "/users": { post: {} } } },
      expected: { asyncapi: "3.0.0", channels: {} },
    },
  ];

  for (const testCase of testCases) {
    const result = await transform(testCase.input);
    assert.deepEqual(result, testCase.expected);
  }
}
```

---

## 8. 常见问题速查

### 8.1 转换失败

**问题**：`OpenAPI验证失败`

**解决**：

```typescript
// 1. 检查OpenAPI版本
if (!spec.openapi || !spec.openapi.startsWith("3.")) {
  throw new Error("仅支持OpenAPI 3.x");
}

// 2. 验证必需字段
if (!spec.info || !spec.paths) {
  throw new Error("缺少必需字段: info 或 paths");
}
```

### 8.2 性能问题

**问题**：转换速度慢

**解决**：

1. **启用缓存**：

   ```typescript
   const result = await transformWithCache(source, target, content);
   ```

2. **并行处理**：

   ```typescript
   const results = await parallelTransform(schemas);
   ```

3. **增量转换**：

   ```typescript
   const result = await incrementalTransform(old, new, target);
   ```

### 8.3 兼容性问题

**问题**：不同版本Schema不兼容

**解决**：

```typescript
function normalizeSchema(schema: any): any {
  // 统一版本格式
  if (schema.swagger) {
    return convertSwaggerToOpenAPI(schema);
  }
  if (schema.asyncapi && schema.asyncapi.startsWith("2.")) {
    return convertAsyncAPI2To3(schema);
  }
  return schema;
}
```

---

## 9. 实用工具函数

### 9.1 Schema类型检测

```typescript
function detectSchemaType(schema: any): string {
  if (schema.openapi) return "openapi";
  if (schema.asyncapi) return "asyncapi";
  if (schema["x-iot"]) return "iot";
  throw new Error("无法识别Schema类型");
}
```

### 9.2 资源名提取

```typescript
function extractResource(path: string): string {
  // /users/{id} -> user
  // /api/v1/products -> product
  const parts = path.split("/").filter(p => p && !p.startsWith("{"));
  return parts[parts.length - 1]?.replace(/s$/, "") || "resource";
}
```

### 9.3 内容哈希

```typescript
import crypto from "crypto";

function hash(content: string): string {
  return crypto.createHash("sha256")
    .update(content)
    .digest("hex")
    .substring(0, 16);
}
```

---

## 10. 参考链接

- **完整实施指南**：
  `analysis/08_MCP_Based_Schema_Transformation_Implementation_Guide.md`
- **MCP协议分析**：
  `analysis/01_MCP_Protocol_Integration_Analysis.md`
- **工具链对比**：
  `analysis/02_DSL_Transformation_Toolchain_Comparison.md`

---

**文档版本**：1.0
**最后更新**：2025-01-21
**维护者**：DSL Schema研究团队

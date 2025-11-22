# MCP Schema转换代码模板库

## 📑 目录

- [MCP Schema转换代码模板库](#mcp-schema转换代码模板库)
  - [📑 目录](#-目录)
  - [1. 项目模板](#1-项目模板)
    - [1.1 TypeScript项目模板](#11-typescript项目模板)
    - [1.2 Python项目模板](#12-python项目模板)
    - [1.3 Go项目模板](#13-go项目模板)
  - [2. MCP Server模板](#2-mcp-server模板)
    - [2.1 基础Server](#21-基础server)
    - [2.2 完整Server](#22-完整server)
    - [2.3 多工具Server](#23-多工具server)
  - [3. 转换器模板](#3-转换器模板)
    - [3.1 OpenAPI转换器](#31-openapi转换器)
    - [3.2 AsyncAPI转换器](#32-asyncapi转换器)
    - [3.3 IoT Schema转换器](#33-iot-schema转换器)
  - [4. 工具定义模板](#4-工具定义模板)
    - [4.1 单Schema转换工具](#41-单schema转换工具)
    - [4.2 批量转换工具](#42-批量转换工具)
    - [4.3 验证工具](#43-验证工具)
  - [5. 测试模板](#5-测试模板)
    - [5.1 单元测试](#51-单元测试)
    - [5.2 集成测试](#52-集成测试)
    - [5.3 E2E测试](#53-e2e测试)
  - [6. 配置模板](#6-配置模板)
    - [6.1 Docker配置](#61-docker配置)
    - [6.2 Kubernetes配置](#62-kubernetes配置)
    - [6.3 环境变量配置](#63-环境变量配置)
  - [7. 参考文档](#7-参考文档)

---

## 1. 项目模板

### 1.1 TypeScript项目模板

**package.json**：

```json
{
  "name": "mcp-schema-transformer",
  "version": "1.0.0",
  "type": "module",
  "description": "MCP Schema转换服务器",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "tsx watch src/index.ts",
    "test": "vitest"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^0.5.0",
    "ajv": "^8.12.0",
    "openapi-types": "^12.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "tsx": "^4.7.0",
    "typescript": "^5.3.0",
    "vitest": "^1.0.0"
  }
}
```

**tsconfig.json**：

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "node",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

### 1.2 Python项目模板

**requirements.txt**：

```txt
mcp>=0.1.0
pydantic>=2.0.0
openapi-spec-validator>=0.7.0
asyncapi>=0.1.0
```

**setup.py**：

```python
from setuptools import setup, find_packages

setup(
    name="mcp-schema-transformer",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "mcp>=0.1.0",
        "pydantic>=2.0.0",
        "openapi-spec-validator>=0.7.0",
    ],
    python_requires=">=3.10",
)
```

### 1.3 Go项目模板

**go.mod**：

```go
module github.com/yourorg/mcp-schema-transformer

go 1.21

require (
    github.com/modelcontextprotocol/go-sdk v0.1.0
    github.com/getkin/kin-openapi v0.122.0
)
```

---

## 2. MCP Server模板

### 2.1 基础Server

**TypeScript版本**：

```typescript
// src/index.ts
import { Server } from
  "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from
  "@modelcontextprotocol/sdk/server/stdio.js";
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const server = new Server(
  {
    name: "schema-transformer",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// 列出工具
server.setRequestHandler(
  ListToolsRequestSchema,
  async () => ({
    tools: [
      {
        name: "transform",
        description: "转换Schema",
        inputSchema: {
          type: "object",
          properties: {
            source: { type: "string" },
            target: { type: "string" },
            content: { type: "string" },
          },
          required: ["source", "target", "content"],
        },
      },
    ],
  })
);

// 处理工具调用
server.setRequestHandler(
  CallToolRequestSchema,
  async (request) => {
    const { name, arguments: args } = request.params;

    if (name === "transform") {
      // 实现转换逻辑
      const result = await transform(
        args.source,
        args.target,
        args.content
      );

      return {
        content: [{
          type: "text",
          text: JSON.stringify(result, null, 2),
        }],
      };
    }

    throw new Error(`未知工具: ${name}`);
  }
);

// 启动服务器
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("MCP Schema转换服务器已启动");
}

main().catch(console.error);
```

### 2.2 完整Server

**包含错误处理和日志**：

```typescript
import winston from "winston";

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || "info",
  format: winston.format.json(),
  transports: [
    new winston.transports.Console({
      format: winston.format.simple(),
    }),
  ],
});

server.setRequestHandler(
  CallToolRequestSchema,
  async (request) => {
    const { name, arguments: args } = request.params;

    try {
      logger.info("工具调用", { name, args });

      const result = await handleTool(name, args);

      logger.info("工具调用成功", { name });
      return result;
    } catch (error) {
      logger.error("工具调用失败", {
        name,
        error: error instanceof Error ? error.message : String(error),
      });

      return {
        content: [{
          type: "text",
          text: `错误: ${error instanceof Error ? error.message : String(error)}`,
        }],
        isError: true,
      };
    }
  }
);
```

### 2.3 多工具Server

**支持多个转换工具**：

```typescript
const tools = [
  {
    name: "transform_openapi_to_asyncapi",
    description: "将OpenAPI规范转换为AsyncAPI规范",
    inputSchema: {
      type: "object",
      properties: {
        openapi_spec: {
          type: "string",
          description: "OpenAPI规范JSON字符串",
        },
      },
      required: ["openapi_spec"],
    },
  },
  {
    name: "transform_asyncapi_to_openapi",
    description: "将AsyncAPI规范转换为OpenAPI规范",
    inputSchema: {
      type: "object",
      properties: {
        asyncapi_spec: {
          type: "string",
          description: "AsyncAPI规范JSON字符串",
        },
      },
      required: ["asyncapi_spec"],
    },
  },
  {
    name: "validate_schema",
    description: "验证Schema格式",
    inputSchema: {
      type: "object",
      properties: {
        schema_type: {
          type: "string",
          enum: ["openapi", "asyncapi"],
        },
        schema_content: { type: "string" },
      },
      required: ["schema_type", "schema_content"],
    },
  },
];

server.setRequestHandler(
  ListToolsRequestSchema,
  async () => ({ tools })
);
```

---

## 3. 转换器模板

### 3.1 OpenAPI转换器

**完整实现**：

```typescript
// src/transformers/openapi.ts
import { OpenAPIV3 } from "openapi-types";

export class OpenAPITransformer {
  async toAsyncAPI(openapi: OpenAPIV3.Document): Promise<any> {
    return {
      asyncapi: "3.0.0",
      info: {
        title: openapi.info.title,
        version: openapi.info.version,
        description: openapi.info.description,
      },
      channels: this.extractChannels(openapi.paths),
      components: this.extractComponents(openapi.components),
    };
  }

  private extractChannels(paths: OpenAPIV3.PathsObject): any {
    const channels: any = {};

    for (const [path, pathItem] of Object.entries(paths)) {
      if (!pathItem) continue;

      for (const [method, operation] of Object.entries(pathItem)) {
        if (!this.isHttpMethod(method)) continue;
        if (!operation) continue;

        const eventName = this.mapToEventName(path, method);
        channels[eventName] = {
          [this.getOperationType(method)]: {
            message: {
              payload: this.extractMessageSchema(operation),
            },
          },
        };
      }
    }

    return channels;
  }

  private mapToEventName(path: string, method: string): string {
    const resource = this.extractResource(path);
    const action = this.mapMethodToAction(method);
    return `${resource}.${action}`;
  }

  private extractResource(path: string): string {
    const parts = path.split("/").filter(p => p && !p.startsWith("{"));
    const lastPart = parts[parts.length - 1] || "resource";
    return lastPart.replace(/s$/, "").toLowerCase();
  }

  private mapMethodToAction(method: string): string {
    const mapping: Record<string, string> = {
      post: "created",
      get: "read",
      put: "updated",
      delete: "deleted",
      patch: "patched",
    };
    return mapping[method.toLowerCase()] || "unknown";
  }

  private getOperationType(method: string): string {
    return method.toLowerCase() === "get" ? "subscribe" : "publish";
  }

  private extractMessageSchema(operation: OpenAPIV3.OperationObject): any {
    if (operation.requestBody) {
      const content = operation.requestBody.content;
      const jsonContent = content?.["application/json"];
      return jsonContent?.schema || {};
    }
    return {};
  }

  private extractComponents(components?: OpenAPIV3.ComponentsObject): any {
    if (!components) return {};

    return {
      schemas: components.schemas || {},
      messages: {},
    };
  }

  private isHttpMethod(method: string): boolean {
    return ["get", "post", "put", "delete", "patch", "head", "options"].includes(
      method.toLowerCase()
    );
  }
}
```

### 3.2 AsyncAPI转换器

**完整实现**：

```typescript
// src/transformers/asyncapi.ts
export class AsyncAPITransformer {
  async toOpenAPI(asyncapi: any): Promise<any> {
    return {
      openapi: "3.1.0",
      info: {
        title: asyncapi.info.title,
        version: asyncapi.info.version,
        description: asyncapi.info.description,
      },
      paths: this.extractPaths(asyncapi.channels),
      components: this.extractComponents(asyncapi.components),
    };
  }

  private extractPaths(channels: any): any {
    const paths: any = {};

    for (const [channelName, channel] of Object.entries(channels)) {
      const { path, method } = this.mapEventToREST(channelName);

      if (!paths[path]) {
        paths[path] = {};
      }

      paths[path][method] = {
        summary: `操作: ${channelName}`,
        requestBody: this.extractRequestBody(channel),
        responses: {
          "200": {
            description: "成功",
            content: {
              "application/json": {
                schema: this.extractResponseSchema(channel),
              },
            },
          },
        },
      };
    }

    return paths;
  }

  private mapEventToREST(eventName: string): { path: string; method: string } {
    const [resource, action] = eventName.split(".");

    const actionToMethod: Record<string, string> = {
      created: "post",
      read: "get",
      updated: "put",
      deleted: "delete",
      patched: "patch",
    };

    const method = actionToMethod[action] || "post";
    const path = method === "get" || method === "post"
      ? `/${resource}s`
      : `/${resource}s/{id}`;

    return { path, method };
  }

  private extractRequestBody(channel: any): any {
    const publish = channel.publish || channel.subscribe;
    if (!publish?.message?.payload) return undefined;

    return {
      required: true,
      content: {
        "application/json": {
          schema: publish.message.payload,
        },
      },
    };
  }

  private extractResponseSchema(channel: any): any {
    const subscribe = channel.subscribe || channel.publish;
    return subscribe?.message?.payload || {};
  }

  private extractComponents(components?: any): any {
    if (!components) return {};

    return {
      schemas: components.schemas || {},
    };
  }
}
```

### 3.3 IoT Schema转换器

**完整实现**：

```typescript
// src/transformers/iot.ts
export class IoTSchemaTransformer {
  async toOpenAPI(iotSchema: any): Promise<any> {
    return {
      openapi: "3.1.0",
      info: {
        title: iotSchema.info?.title || "IoT API",
        version: iotSchema.info?.version || "1.0.0",
      },
      paths: this.extractPaths(iotSchema.devices),
    };
  }

  private extractPaths(devices: any[]): any {
    const paths: any = {};

    for (const device of devices) {
      for (const sensor of device.sensors || []) {
        const path = `/devices/${device.id}/sensors/${sensor.id}`;
        paths[path] = {
          get: {
            summary: `获取传感器数据: ${sensor.name}`,
            parameters: [
              {
                name: "deviceId",
                in: "path",
                required: true,
                schema: { type: "string" },
              },
              {
                name: "sensorId",
                in: "path",
                required: true,
                schema: { type: "string" },
              },
            ],
            responses: {
              "200": {
                description: "传感器数据",
                content: {
                  "application/json": {
                    schema: sensor.schema,
                  },
                },
              },
            },
            "x-iot": {
              deviceType: "sensor",
              protocol: sensor.protocol || "mqtt",
              topic: sensor.topic,
              qos: sensor.qos || 0,
            },
          },
        };
      }
    }

    return paths;
  }
}
```

---

## 4. 工具定义模板

### 4.1 单Schema转换工具

```typescript
{
  name: "transform_schema",
  description: "通用Schema转换工具",
  inputSchema: {
    type: "object",
    properties: {
      source_type: {
        type: "string",
        enum: ["openapi", "asyncapi", "iot"],
        description: "源Schema类型",
      },
      target_type: {
        type: "string",
        enum: ["openapi", "asyncapi", "iot"],
        description: "目标Schema类型",
      },
      schema_content: {
        type: "string",
        description: "Schema内容（JSON字符串）",
      },
    },
    required: ["source_type", "target_type", "schema_content"],
  },
}
```

### 4.2 批量转换工具

```typescript
{
  name: "batch_transform",
  description: "批量转换多个Schema",
  inputSchema: {
    type: "object",
    properties: {
      transformations: {
        type: "array",
        items: {
          type: "object",
          properties: {
            source_type: { type: "string" },
            target_type: { type: "string" },
            schema_content: { type: "string" },
          },
          required: ["source_type", "target_type", "schema_content"],
        },
      },
    },
    required: ["transformations"],
  },
}
```

### 4.3 验证工具

```typescript
{
  name: "validate_schema",
  description: "验证Schema格式和内容",
  inputSchema: {
    type: "object",
    properties: {
      schema_type: {
        type: "string",
        enum: ["openapi", "asyncapi", "iot"],
      },
      schema_content: { type: "string" },
      strict: {
        type: "boolean",
        description: "是否严格验证",
        default: false,
      },
    },
    required: ["schema_type", "schema_content"],
  },
}
```

---

## 5. 测试模板

### 5.1 单元测试

```typescript
// tests/transformers/openapi.test.ts
import { describe, it, expect } from "vitest";
import { OpenAPITransformer } from "../src/transformers/openapi";

describe("OpenAPITransformer", () => {
  const transformer = new OpenAPITransformer();

  it("应该正确转换POST操作到事件", async () => {
    const openapi = {
      openapi: "3.1.0",
      info: { title: "Test API", version: "1.0.0" },
      paths: {
        "/users": {
          post: {
            requestBody: {
              content: {
                "application/json": {
                  schema: {
                    type: "object",
                    properties: {
                      name: { type: "string" },
                    },
                  },
                },
              },
            },
          },
        },
      },
    };

    const asyncapi = await transformer.toAsyncAPI(openapi);

    expect(asyncapi.asyncapi).toBe("3.0.0");
    expect(asyncapi.channels).toHaveProperty("user.created");
  });
});
```

### 5.2 集成测试

```typescript
// tests/integration/mcp-server.test.ts
import { describe, it, expect } from "vitest";
import { createTestClient } from "./test-utils";

describe("MCP Server集成测试", () => {
  it("应该响应工具调用", async () => {
    const client = await createTestClient();

    const response = await client.callTool("transform", {
      source: "openapi",
      target: "asyncapi",
      content: JSON.stringify({
        openapi: "3.1.0",
        info: { title: "Test", version: "1.0.0" },
        paths: {},
      }),
    });

    expect(response.content[0].text).toContain("asyncapi");
  });
});
```

### 5.3 E2E测试

```typescript
// tests/e2e/full-transformation.test.ts
import { describe, it, expect } from "vitest";

describe("端到端转换测试", () => {
  it("应该完成完整的OpenAPI到AsyncAPI转换流程", async () => {
    // 1. 加载测试数据
    const openapi = loadTestOpenAPISpec();

    // 2. 调用MCP工具
    const result = await mcpClient.callTool(
      "transform_openapi_to_asyncapi",
      { openapi_spec: JSON.stringify(openapi) }
    );

    // 3. 验证结果
    const asyncapi = JSON.parse(result.content[0].text);
    expect(asyncapi.asyncapi).toBeDefined();

    // 4. 验证转换正确性
    validateAsyncAPISpec(asyncapi);
  });
});
```

---

## 6. 配置模板

### 6.1 Docker配置

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --production

COPY . .
RUN npm run build

CMD ["node", "dist/index.js"]
```

```yaml
# docker-compose.yml
version: "3.8"

services:
  mcp-server:
    build: .
    environment:
      - LOG_LEVEL=info
      - CACHE_ENABLED=true
    volumes:
      - ./logs:/app/logs
```

### 6.2 Kubernetes配置

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-schema-transformer
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-schema-transformer
  template:
    metadata:
      labels:
        app: mcp-schema-transformer
    spec:
      containers:
      - name: mcp-server
        image: mcp-schema-transformer:latest
        env:
        - name: LOG_LEVEL
          value: "info"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### 6.3 环境变量配置

```bash
# .env.example
LOG_LEVEL=info
CACHE_ENABLED=true
CACHE_TTL=3600
REDIS_URL=redis://localhost:6379
MAX_CONCURRENT_TRANSFORMS=10
TIMEOUT_MS=5000
```

---

## 7. 参考文档

- **实施指南**：
  `analysis/08_MCP_Based_Schema_Transformation_Implementation_Guide.md`
- **快速参考**：
  `analysis/09_MCP_Schema_Transformation_Quick_Reference.md`

---

**文档版本**：1.0
**最后更新**：2025-01-21
**维护者**：DSL Schema研究团队

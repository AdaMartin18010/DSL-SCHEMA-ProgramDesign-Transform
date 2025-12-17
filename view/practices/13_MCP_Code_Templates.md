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
  - [7. MCP模板综合应用实际示例](#7-mcp模板综合应用实际示例)
  - [8. 参考文档](#8-参考文档)
    - [MCP文档](#mcp文档)
    - [模式文档 ⭐新增](#模式文档-新增)
  - [📝 版本历史](#-版本历史)
    - [v1.2 (2025-01-21) - 实际应用示例增强版](#v12-2025-01-21---实际应用示例增强版)
    - [v1.1 (2025-01-27) - 初始版本](#v11-2025-01-27---初始版本)

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

## 7. MCP模板综合应用实际示例

**示例：实现完整的MCP Schema转换服务生成器**

```python
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum
import json

class Language(Enum):
    """支持的语言"""
    TYPESCRIPT = "typescript"
    PYTHON = "python"
    GO = "go"

class TemplateType(Enum):
    """模板类型"""
    PROJECT = "project"
    SERVER = "server"
    TRANSFORMER = "transformer"
    TOOL = "tool"
    TEST = "test"
    CONFIG = "config"

@dataclass
class GeneratedFile:
    """生成的文件"""
    path: str
    content: str
    language: str

class MCPTemplateGenerator:
    """MCP模板生成器"""

    def __init__(self, project_name: str, language: Language = Language.TYPESCRIPT):
        self.project_name = project_name
        self.language = language
        self.generated_files: List[GeneratedFile] = []

    def generate_complete_project(self, transformers: List[str]) -> List[GeneratedFile]:
        """生成完整项目"""
        self.generated_files = []

        # 1. 生成项目配置（基于第1章）
        self._generate_project_config()

        # 2. 生成MCP Server（基于第2章）
        self._generate_mcp_server(transformers)

        # 3. 生成转换器（基于第3章）
        for transformer in transformers:
            self._generate_transformer(transformer)

        # 4. 生成工具定义（基于第4章）
        self._generate_tool_definitions(transformers)

        # 5. 生成测试（基于第5章）
        self._generate_tests(transformers)

        # 6. 生成配置（基于第6章）
        self._generate_deployment_config()

        return self.generated_files

    def _generate_project_config(self):
        """生成项目配置（基于第1章）"""
        if self.language == Language.TYPESCRIPT:
            # package.json
            package_json = {
                "name": self.project_name,
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
            self.generated_files.append(GeneratedFile(
                path="package.json",
                content=json.dumps(package_json, indent=2),
                language="json"
            ))

            # tsconfig.json
            tsconfig = {
                "compilerOptions": {
                    "target": "ES2022",
                    "module": "ESNext",
                    "moduleResolution": "node",
                    "outDir": "./dist",
                    "rootDir": "./src",
                    "strict": True,
                    "esModuleInterop": True,
                    "declaration": True
                },
                "include": ["src/**/*"],
                "exclude": ["node_modules"]
            }
            self.generated_files.append(GeneratedFile(
                path="tsconfig.json",
                content=json.dumps(tsconfig, indent=2),
                language="json"
            ))

        elif self.language == Language.PYTHON:
            # requirements.txt
            requirements = """mcp>=0.5.0
pydantic>=2.0.0
fastapi>=0.100.0
uvicorn>=0.23.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
"""
            self.generated_files.append(GeneratedFile(
                path="requirements.txt",
                content=requirements,
                language="txt"
            ))

            # pyproject.toml
            pyproject = f'''[project]
name = "{self.project_name}"
version = "1.0.0"
description = "MCP Schema转换服务器"
requires-python = ">=3.10"

[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"
'''
            self.generated_files.append(GeneratedFile(
                path="pyproject.toml",
                content=pyproject,
                language="toml"
            ))

    def _generate_mcp_server(self, transformers: List[str]):
        """生成MCP Server（基于第2章）"""
        if self.language == Language.TYPESCRIPT:
            server_code = self._generate_typescript_server(transformers)
        else:
            server_code = self._generate_python_server(transformers)

        ext = "ts" if self.language == Language.TYPESCRIPT else "py"
        self.generated_files.append(GeneratedFile(
            path=f"src/index.{ext}",
            content=server_code,
            language=ext
        ))

    def _generate_typescript_server(self, transformers: List[str]) -> str:
        """生成TypeScript服务器代码"""
        transformer_imports = "\n".join([
            f'import {{ {t}Transformer }} from "./transformers/{t.lower()}";'
            for t in transformers
        ])

        tool_registrations = "\n".join([
            f'''    server.setRequestHandler(ListToolsRequestSchema, async () => {{
      return {{
        tools: [
          {{
            name: "transform_{t.lower()}",
            description: "{t} Schema转换",
            inputSchema: {{
              type: "object",
              properties: {{
                source: {{ type: "object", description: "源Schema" }},
                options: {{ type: "object", description: "转换选项" }}
              }},
              required: ["source"]
            }}
          }}
        ]
      }};
    }});'''
            for t in transformers
        ])

        return f'''import {{ Server }} from "@modelcontextprotocol/sdk/server/index.js";
import {{ StdioServerTransport }} from "@modelcontextprotocol/sdk/server/stdio.js";
import {{ ListToolsRequestSchema, CallToolRequestSchema }} from "@modelcontextprotocol/sdk/types.js";
{transformer_imports}

const server = new Server(
  {{ name: "{self.project_name}", version: "1.0.0" }},
  {{ capabilities: {{ tools: {{}} }} }}
);

// 工具列表
{tool_registrations}

// 工具调用处理
server.setRequestHandler(CallToolRequestSchema, async (request) => {{
  const {{ name, arguments: args }} = request.params;

  switch (name) {{
{self._generate_typescript_switch_cases(transformers)}
    default:
      throw new Error(`Unknown tool: ${{name}}`);
  }}
}});

// 启动服务器
async function main() {{
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("{self.project_name} MCP server running");
}}

main().catch(console.error);
'''

    def _generate_typescript_switch_cases(self, transformers: List[str]) -> str:
        """生成TypeScript switch cases"""
        cases = []
        for t in transformers:
            cases.append(f'''    case "transform_{t.lower()}":
      const {t.lower()}Result = new {t}Transformer().transform(args.source, args.options);
      return {{ content: [{{ type: "text", text: JSON.stringify({t.lower()}Result, null, 2) }}] }};''')
        return "\n".join(cases)

    def _generate_python_server(self, transformers: List[str]) -> str:
        """生成Python服务器代码"""
        transformer_imports = "\n".join([
            f'from transformers.{t.lower()} import {t}Transformer'
            for t in transformers
        ])

        return f'''import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
{transformer_imports}

server = Server("{self.project_name}")

# 转换器实例
transformers = {{
{self._generate_python_transformer_dict(transformers)}
}}

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
{self._generate_python_tool_list(transformers)}
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name.startswith("transform_"):
        transformer_name = name.replace("transform_", "")
        if transformer_name in transformers:
            result = transformers[transformer_name].transform(
                arguments.get("source", {{}}),
                arguments.get("options", {{}})
            )
            return [TextContent(type="text", text=str(result))]

    raise ValueError(f"Unknown tool: {{name}}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    asyncio.run(main())
'''

    def _generate_python_transformer_dict(self, transformers: List[str]) -> str:
        """生成Python转换器字典"""
        return ",\n".join([
            f'    "{t.lower()}": {t}Transformer()'
            for t in transformers
        ])

    def _generate_python_tool_list(self, transformers: List[str]) -> str:
        """生成Python工具列表"""
        tools = []
        for t in transformers:
            tools.append(f'''        Tool(
            name="transform_{t.lower()}",
            description="{t} Schema转换",
            inputSchema={{
                "type": "object",
                "properties": {{
                    "source": {{"type": "object", "description": "源Schema"}},
                    "options": {{"type": "object", "description": "转换选项"}}
                }},
                "required": ["source"]
            }}
        )''')
        return ",\n".join(tools)

    def _generate_transformer(self, transformer_name: str):
        """生成转换器（基于第3章）"""
        if self.language == Language.TYPESCRIPT:
            content = self._generate_typescript_transformer(transformer_name)
            ext = "ts"
        else:
            content = self._generate_python_transformer(transformer_name)
            ext = "py"

        self.generated_files.append(GeneratedFile(
            path=f"src/transformers/{transformer_name.lower()}.{ext}",
            content=content,
            language=ext
        ))

    def _generate_typescript_transformer(self, name: str) -> str:
        """生成TypeScript转换器"""
        return f'''export interface TransformOptions {{
  preserveComments?: boolean;
  strictMode?: boolean;
}}

export interface TransformResult {{
  success: boolean;
  data: any;
  errors?: string[];
}}

export class {name}Transformer {{
  transform(source: any, options: TransformOptions = {{}}): TransformResult {{
    try {{
      // TODO: 实现{name}转换逻辑
      const transformed = this._doTransform(source, options);

      return {{
        success: true,
        data: transformed
      }};
    }} catch (error) {{
      return {{
        success: false,
        data: null,
        errors: [error.message]
      }};
    }}
  }}

  private _doTransform(source: any, options: TransformOptions): any {{
    // 基础转换实现
    return {{
      transformed: true,
      originalType: "{name}",
      timestamp: new Date().toISOString(),
      ...source
    }};
  }}

  validate(schema: any): boolean {{
    // TODO: 实现验证逻辑
    return true;
  }}
}}
'''

    def _generate_python_transformer(self, name: str) -> str:
        """生成Python转换器"""
        return f'''from dataclasses import dataclass
from typing import Dict, Any, Optional, List

@dataclass
class TransformOptions:
    preserve_comments: bool = False
    strict_mode: bool = False

@dataclass
class TransformResult:
    success: bool
    data: Optional[Dict[str, Any]]
    errors: Optional[List[str]] = None

class {name}Transformer:
    def transform(self, source: Dict[str, Any],
                  options: Optional[Dict[str, Any]] = None) -> TransformResult:
        """执行{name}转换"""
        try:
            opts = TransformOptions(**(options or {{}}))
            transformed = self._do_transform(source, opts)

            return TransformResult(
                success=True,
                data=transformed
            )
        except Exception as e:
            return TransformResult(
                success=False,
                data=None,
                errors=[str(e)]
            )

    def _do_transform(self, source: Dict[str, Any],
                      options: TransformOptions) -> Dict[str, Any]:
        """内部转换实现"""
        from datetime import datetime

        return {{
            "transformed": True,
            "originalType": "{name}",
            "timestamp": datetime.now().isoformat(),
            **source
        }}

    def validate(self, schema: Dict[str, Any]) -> bool:
        """验证Schema"""
        # TODO: 实现验证逻辑
        return True
'''

    def _generate_tool_definitions(self, transformers: List[str]):
        """生成工具定义（基于第4章）"""
        if self.language == Language.TYPESCRIPT:
            content = self._generate_typescript_tools(transformers)
            ext = "ts"
        else:
            content = self._generate_python_tools(transformers)
            ext = "py"

        self.generated_files.append(GeneratedFile(
            path=f"src/tools/definitions.{ext}",
            content=content,
            language=ext
        ))

    def _generate_typescript_tools(self, transformers: List[str]) -> str:
        """生成TypeScript工具定义"""
        tool_defs = []
        for t in transformers:
            tool_defs.append(f'''  {{
    name: "transform_{t.lower()}",
    description: "{t} Schema转换工具",
    inputSchema: {{
      type: "object",
      properties: {{
        source: {{ type: "object", description: "源Schema" }},
        options: {{
          type: "object",
          properties: {{
            preserveComments: {{ type: "boolean", default: false }},
            strictMode: {{ type: "boolean", default: false }}
          }}
        }}
      }},
      required: ["source"]
    }}
  }}''')

        return f'''export const toolDefinitions = [
{",".join(tool_defs)}
];
'''

    def _generate_python_tools(self, transformers: List[str]) -> str:
        """生成Python工具定义"""
        return f'''TOOL_DEFINITIONS = [
{self._generate_python_tool_defs(transformers)}
]
'''

    def _generate_python_tool_defs(self, transformers: List[str]) -> str:
        """生成Python工具定义列表"""
        defs = []
        for t in transformers:
            defs.append(f'''    {{
        "name": "transform_{t.lower()}",
        "description": "{t} Schema转换工具",
        "inputSchema": {{
            "type": "object",
            "properties": {{
                "source": {{"type": "object", "description": "源Schema"}},
                "options": {{
                    "type": "object",
                    "properties": {{
                        "preserve_comments": {{"type": "boolean", "default": False}},
                        "strict_mode": {{"type": "boolean", "default": False}}
                    }}
                }}
            }},
            "required": ["source"]
        }}
    }}''')
        return ",\n".join(defs)

    def _generate_tests(self, transformers: List[str]):
        """生成测试（基于第5章）"""
        for t in transformers:
            if self.language == Language.TYPESCRIPT:
                content = self._generate_typescript_test(t)
                ext = "test.ts"
            else:
                content = self._generate_python_test(t)
                ext = "test.py"

            self.generated_files.append(GeneratedFile(
                path=f"tests/{t.lower()}.{ext}",
                content=content,
                language=ext.split(".")[-1]
            ))

    def _generate_typescript_test(self, transformer_name: str) -> str:
        """生成TypeScript测试"""
        return f'''import {{ describe, it, expect }} from "vitest";
import {{ {transformer_name}Transformer }} from "../src/transformers/{transformer_name.lower()}";

describe("{transformer_name}Transformer", () => {{
  const transformer = new {transformer_name}Transformer();

  it("should transform valid schema", () => {{
    const source = {{ type: "object", properties: {{}} }};
    const result = transformer.transform(source);

    expect(result.success).toBe(true);
    expect(result.data).toBeDefined();
    expect(result.data.transformed).toBe(true);
  }});

  it("should handle empty schema", () => {{
    const result = transformer.transform({{}});

    expect(result.success).toBe(true);
  }});

  it("should pass validation", () => {{
    const schema = {{ type: "object" }};
    expect(transformer.validate(schema)).toBe(true);
  }});
}});
'''

    def _generate_python_test(self, transformer_name: str) -> str:
        """生成Python测试"""
        return f'''import pytest
from src.transformers.{transformer_name.lower()} import {transformer_name}Transformer

class Test{transformer_name}Transformer:
    def setup_method(self):
        self.transformer = {transformer_name}Transformer()

    def test_transform_valid_schema(self):
        source = {{"type": "object", "properties": {{}}}}
        result = self.transformer.transform(source)

        assert result.success is True
        assert result.data is not None
        assert result.data["transformed"] is True

    def test_transform_empty_schema(self):
        result = self.transformer.transform({{}})

        assert result.success is True

    def test_validate_schema(self):
        schema = {{"type": "object"}}
        assert self.transformer.validate(schema) is True
'''

    def _generate_deployment_config(self):
        """生成部署配置（基于第6章）"""
        # Dockerfile
        if self.language == Language.TYPESCRIPT:
            dockerfile = f'''FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY dist ./dist
CMD ["node", "dist/index.js"]
'''
        else:
            dockerfile = f'''FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
CMD ["python", "-m", "src.index"]
'''

        self.generated_files.append(GeneratedFile(
            path="Dockerfile",
            content=dockerfile,
            language="dockerfile"
        ))

        # docker-compose.yml
        docker_compose = f'''version: "3.8"

services:
  mcp-server:
    build: .
    environment:
      - LOG_LEVEL=info
      - CACHE_ENABLED=true
    volumes:
      - ./logs:/app/logs
'''
        self.generated_files.append(GeneratedFile(
            path="docker-compose.yml",
            content=docker_compose,
            language="yaml"
        ))

        # .env.example
        env_example = '''LOG_LEVEL=info
CACHE_ENABLED=true
CACHE_TTL=3600
MAX_CONCURRENT_TRANSFORMS=10
TIMEOUT_MS=5000
'''
        self.generated_files.append(GeneratedFile(
            path=".env.example",
            content=env_example,
            language="env"
        ))

    def get_project_summary(self) -> Dict:
        """获取项目摘要"""
        file_types = {}
        for f in self.generated_files:
            ext = f.path.split(".")[-1]
            file_types[ext] = file_types.get(ext, 0) + 1

        return {
            "project_name": self.project_name,
            "language": self.language.value,
            "total_files": len(self.generated_files),
            "file_types": file_types,
            "files": [f.path for f in self.generated_files]
        }

# 实际应用示例
generator = MCPTemplateGenerator(
    project_name="my-mcp-transformer",
    language=Language.TYPESCRIPT
)

# 生成完整项目
transformers = ["OpenAPI", "AsyncAPI", "JSONSchema"]
files = generator.generate_complete_project(transformers)

# 输出项目摘要
print("=== MCP项目生成摘要 ===")
summary = generator.get_project_summary()
print(f"项目名称: {summary['project_name']}")
print(f"语言: {summary['language']}")
print(f"生成文件数: {summary['total_files']}")
print(f"\n文件列表:")
for file_path in summary['files']:
    print(f"  - {file_path}")

# 预览生成的主文件
print("\n=== 主文件预览（前50行）===")
main_file = next((f for f in files if "index" in f.path), None)
if main_file:
    lines = main_file.content.split('\n')[:50]
    for i, line in enumerate(lines, 1):
        print(f"{i:3}: {line}")
```

---

## 8. 参考文档

### MCP文档

- **实施指南**：
  `analysis/08_MCP_Based_Schema_Transformation_Implementation_Guide.md`
- **快速参考**：
  `analysis/09_MCP_Schema_Transformation_Quick_Reference.md`

### 模式文档 ⭐新增

- `docs/structure/DESIGN_PATTERNS_SUMMARY.md`：设计模式总结（15个模式）
  - 在代码模板设计中，可以参考工厂模式、建造者模式、模板方法模式等
- `docs/structure/ARCHITECTURE_PATTERNS_SUMMARY.md`：架构模式总结（12个模式）
  - 在MCP系统架构设计中，可以参考分层架构、微服务架构等
- `docs/structure/PATTERNS_QUICK_REFERENCE.md`：模式快速参考指南 ⭐推荐

---

## 📝 版本历史

### v1.2 (2025-01-21) - 实际应用示例增强版

- ✅ 扩展第7章：为MCP模板添加综合应用实际示例（包含完整项目生成器实现、TypeScript/Python双语言支持、Server生成、转换器生成、工具定义生成、测试生成、部署配置生成）
- ✅ 添加版本历史章节
- ✅ 更新文档版本号至v1.2

### v1.1 (2025-01-27) - 初始版本

- ✅ 创建文档：MCP Schema转换代码模板库
- ✅ 添加项目模板
- ✅ 添加MCP Server模板
- ✅ 添加转换器模板
- ✅ 添加工具定义模板
- ✅ 添加测试模板
- ✅ 添加配置模板

---

**文档版本**：1.2（实际应用示例增强版）
**最后更新**：2025-01-27
**维护者**：DSL Schema研究团队

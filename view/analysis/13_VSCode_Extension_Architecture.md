# VS Code插件架构设计

## 📑 目录

- [VS Code插件架构设计](#vs-code插件架构设计)
  - [📑 目录](#-目录)
  - [1. 架构概述](#1-架构概述)
    - [1.1 插件目标](#11-插件目标)
    - [1.2 架构设计原则](#12-架构设计原则)
  - [2. 插件架构](#2-插件架构)
    - [2.1 整体架构](#21-整体架构)
    - [2.2 核心模块](#22-核心模块)
    - [2.3 模块间通信](#23-模块间通信)
  - [3. Schema编辑器](#3-schema编辑器)
    - [3.1 编辑器功能](#31-编辑器功能)
    - [3.2 语法高亮](#32-语法高亮)
    - [3.3 自动补全](#33-自动补全)
    - [3.4 错误检查](#34-错误检查)
  - [4. 转换功能](#4-转换功能)
    - [4.1 转换工具集成](#41-转换工具集成)
    - [4.2 转换预览](#42-转换预览)
    - [4.3 转换执行](#43-转换执行)
  - [5. 用户界面](#5-用户界面)
    - [5.1 命令面板](#51-命令面板)
    - [5.2 状态栏](#52-状态栏)
    - [5.3 侧边栏](#53-侧边栏)
  - [6. 扩展性设计](#6-扩展性设计)
    - [6.1 插件扩展点](#61-插件扩展点)
    - [6.2 自定义转换器](#62-自定义转换器)
    - [6.3 主题定制](#63-主题定制)
  - [7. 性能优化](#7-性能优化)
    - [7.1 延迟加载](#71-延迟加载)
    - [7.2 缓存机制](#72-缓存机制)
    - [7.3 异步处理](#73-异步处理)
  - [8. 测试与发布](#8-测试与发布)
    - [8.1 单元测试](#81-单元测试)
    - [8.2 集成测试](#82-集成测试)
    - [8.3 发布流程](#83-发布流程)

---

## 1. 架构概述

### 1.1 插件目标

**插件功能**：

1. **Schema编辑**：提供Schema编辑功能
2. **语法支持**：语法高亮、自动补全、错误检查
3. **转换功能**：Schema转换和预览
4. **验证功能**：Schema验证和错误提示

### 1.2 架构设计原则

**设计原则**：

1. **模块化**：清晰的模块划分
2. **可扩展**：支持插件扩展
3. **高性能**：优化性能，减少延迟
4. **用户友好**：直观的用户界面

---

## 2. 插件架构

### 2.1 整体架构

**架构图**：

```text
VS Code Extension Host
    ↓
Extension Main (extension.ts)
    ├── Schema Editor
    │   ├── Language Server
    │   ├── Syntax Highlighter
    │   └── Auto Completion
    ├── Transformation Engine
    │   ├── Converter Registry
    │   ├── Preview Manager
    │   └── Execution Engine
    ├── Validation Service
    │   ├── Validator
    │   └── Error Reporter
    └── UI Components
        ├── Command Palette
        ├── Status Bar
        └── Sidebar
```

### 2.2 核心模块

**模块划分**：

1. **Schema Editor模块**：
   - 语言服务器
   - 语法高亮
   - 自动补全
   - 错误检查

2. **Transformation Engine模块**：
   - 转换器注册
   - 转换预览
   - 转换执行

3. **Validation Service模块**：
   - Schema验证
   - 错误报告
   - 修复建议

4. **UI Components模块**：
   - 命令面板
   - 状态栏
   - 侧边栏

### 2.3 模块间通信

**通信机制**：

- **事件总线**：模块间事件通信
- **API接口**：模块间API调用
- **消息传递**：异步消息传递

---

## 3. Schema编辑器

### 3.1 编辑器功能

**功能列表**：

1. **语法高亮**：DSL语法高亮
2. **自动补全**：智能代码补全
3. **错误检查**：实时错误检查
4. **代码格式化**：自动代码格式化
5. **代码折叠**：代码块折叠
6. **符号导航**：快速符号导航

### 3.2 语法高亮

**实现方式**：

```json
// package.json
{
  "contributes": {
    "languages": [{
      "id": "dsl-schema",
      "aliases": ["DSL Schema", "dsl"],
      "extensions": [".dsl", ".schema"]
    }],
    "grammars": [{
      "language": "dsl-schema",
      "scopeName": "source.dsl",
      "path": "./syntaxes/dsl.tmLanguage.json"
    }]
  }
}
```

### 3.3 自动补全

**补全实现**：

```typescript
// src/completion.ts
import * as vscode from 'vscode';

export function provideCompletionItems(
  document: vscode.TextDocument,
  position: vscode.Position
): vscode.CompletionItem[] {
  const completions: vscode.CompletionItem[] = [];

  // Schema关键字补全
  completions.push({
    label: 'schema',
    kind: vscode.CompletionItemKind.Keyword,
    detail: 'Schema definition',
    documentation: 'Define a new schema'
  });

  // 类型补全
  completions.push({
    label: 'String',
    kind: vscode.CompletionItemKind.TypeParameter,
    detail: 'String type',
    documentation: 'String data type'
  });

  return completions;
}
```

### 3.4 错误检查

**错误检查实现**：

```typescript
// src/diagnostics.ts
import * as vscode from 'vscode';

export function validateDocument(
  document: vscode.TextDocument
): vscode.Diagnostic[] {
  const diagnostics: vscode.Diagnostic[] = [];
  const text = document.getText();

  // 解析Schema
  try {
    const schema = parseSchema(text);

    // 验证Schema
    const errors = validateSchema(schema);

    errors.forEach(error => {
      diagnostics.push({
        range: new vscode.Range(
          error.line,
          error.column,
          error.line,
          error.column + error.length
        ),
        message: error.message,
        severity: vscode.DiagnosticSeverity.Error,
        source: 'dsl-schema'
      });
    });
  } catch (error) {
    // 解析错误
    diagnostics.push({
      range: new vscode.Range(0, 0, 0, 0),
      message: error.message,
      severity: vscode.DiagnosticSeverity.Error,
      source: 'dsl-schema'
    });
  }

  return diagnostics;
}
```

---

## 4. 转换功能

### 4.1 转换工具集成

**转换器注册**：

```typescript
// src/transformers/registry.ts
export class TransformerRegistry {
  private transformers: Map<string, Transformer> = new Map();

  register(name: string, transformer: Transformer): void {
    this.transformers.set(name, transformer);
  }

  get(name: string): Transformer | undefined {
    return this.transformers.get(name);
  }

  list(): string[] {
    return Array.from(this.transformers.keys());
  }
}

// 注册转换器
const registry = new TransformerRegistry();
registry.register('openapi', new OpenAPITransformer());
registry.register('json-schema', new JSONSchemaTransformer());
registry.register('asyncapi', new AsyncAPITransformer());
```

### 4.2 转换预览

**预览实现**：

```typescript
// src/preview.ts
import * as vscode from 'vscode';

export class PreviewManager {
  private previewPanels: Map<string, vscode.WebviewPanel> = new Map();

  async showPreview(
    document: vscode.TextDocument,
    targetFormat: string
  ): Promise<void> {
    const schema = parseSchema(document.getText());
    const transformer = registry.get(targetFormat);

    if (!transformer) {
      vscode.window.showErrorMessage(`Unknown format: ${targetFormat}`);
      return;
    }

    const transformed = await transformer.transform(schema);

    // 创建预览面板
    const panel = vscode.window.createWebviewPanel(
      'schemaPreview',
      `Preview: ${targetFormat}`,
      vscode.ViewColumn.Beside,
      { enableScripts: true }
    );

    panel.webview.html = this.generatePreviewHTML(transformed);
    this.previewPanels.set(document.uri.toString(), panel);
  }
}
```

### 4.3 转换执行

**执行实现**：

```typescript
// src/commands/transform.ts
import * as vscode from 'vscode';

export async function transformCommand(
  context: vscode.ExtensionContext
): Promise<void> {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showErrorMessage('No active editor');
    return;
  }

  // 选择目标格式
  const formats = registry.list();
  const selected = await vscode.window.showQuickPick(formats, {
    placeHolder: 'Select target format'
  });

  if (!selected) return;

  // 执行转换
  const schema = parseSchema(editor.document.getText());
  const transformer = registry.get(selected);

  if (!transformer) return;

  try {
    const result = await transformer.transform(schema);

    // 创建新文档显示结果
    const doc = await vscode.workspace.openTextDocument({
      content: JSON.stringify(result, null, 2),
      language: 'json'
    });

    await vscode.window.showTextDocument(doc);
  } catch (error) {
    vscode.window.showErrorMessage(`Transformation failed: ${error.message}`);
  }
}
```

---

## 5. 用户界面

### 5.1 命令面板

**命令注册**：

```json
// package.json
{
  "contributes": {
    "commands": [
      {
        "command": "dsl-schema.transform",
        "title": "Transform Schema",
        "category": "DSL Schema"
      },
      {
        "command": "dsl-schema.validate",
        "title": "Validate Schema",
        "category": "DSL Schema"
      },
      {
        "command": "dsl-schema.preview",
        "title": "Preview Transformation",
        "category": "DSL Schema"
      }
    ]
  }
}
```

### 5.2 状态栏

**状态栏实现**：

```typescript
// src/statusbar.ts
import * as vscode from 'vscode';

export class StatusBar {
  private statusBarItem: vscode.StatusBarItem;

  constructor() {
    this.statusBarItem = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Right,
      100
    );
    this.statusBarItem.command = 'dsl-schema.showStatus';
    this.statusBarItem.show();
  }

  updateStatus(schema: Schema): void {
    const status = this.getSchemaStatus(schema);
    this.statusBarItem.text = `$(check) Schema: ${status}`;
    this.statusBarItem.tooltip = `Schema validation status: ${status}`;
  }

  private getSchemaStatus(schema: Schema): string {
    // 计算Schema状态
    return 'Valid';
  }
}
```

### 5.3 侧边栏

**侧边栏实现**：

```typescript
// src/sidebar.ts
import * as vscode from 'vscode';

export class SchemaExplorerProvider
  implements vscode.TreeDataProvider<SchemaNode> {

  getTreeItem(element: SchemaNode): vscode.TreeItem {
    return element;
  }

  getChildren(element?: SchemaNode): Thenable<SchemaNode[]> {
    if (!element) {
      // 根节点
      return Promise.resolve(this.getRootNodes());
    }
    return Promise.resolve(this.getChildNodes(element));
  }

  private getRootNodes(): SchemaNode[] {
    // 返回根节点列表
    return [];
  }

  private getChildNodes(node: SchemaNode): SchemaNode[] {
    // 返回子节点列表
    return [];
  }
}
```

---

## 6. 扩展性设计

### 6.1 插件扩展点

**扩展点定义**：

```json
// package.json
{
  "contributes": {
    "extensionPoints": {
      "transformers": {
        "description": "Register custom transformers"
      },
      "validators": {
        "description": "Register custom validators"
      }
    }
  }
}
```

### 6.2 自定义转换器

**转换器接口**：

```typescript
// src/api/transformer.ts
export interface Transformer {
  name: string;
  transform(schema: Schema): Promise<TransformationResult>;
  validate(schema: Schema): ValidationResult;
}

// 自定义转换器示例
export class CustomTransformer implements Transformer {
  name = 'custom-format';

  async transform(schema: Schema): Promise<TransformationResult> {
    // 自定义转换逻辑
    return {};
  }

  validate(schema: Schema): ValidationResult {
    // 自定义验证逻辑
    return { valid: true, errors: [] };
  }
}
```

### 6.3 主题定制

**主题配置**：

```json
// package.json
{
  "contributes": {
    "themes": [{
      "label": "DSL Schema Theme",
      "uiTheme": "vs-dark",
      "path": "./themes/dsl-schema-color-theme.json"
    }]
  }
}
```

---

## 7. 性能优化

### 7.1 延迟加载

**延迟加载实现**：

```typescript
// src/extension.ts
export function activate(context: vscode.ExtensionContext) {
  // 延迟加载转换器
  const transformerLoader = new LazyLoader(() => {
    return import('./transformers/registry');
  });

  // 延迟加载验证器
  const validatorLoader = new LazyLoader(() => {
    return import('./validators/registry');
  });
}
```

### 7.2 缓存机制

**缓存实现**：

```typescript
// src/cache.ts
export class TransformationCache {
  private cache: Map<string, TransformationResult> = new Map();

  get(key: string): TransformationResult | null {
    return this.cache.get(key) || null;
  }

  set(key: string, result: TransformationResult): void {
    this.cache.set(key, result);
  }

  invalidate(pattern: string): void {
    for (const key of this.cache.keys()) {
      if (key.includes(pattern)) {
        this.cache.delete(key);
      }
    }
  }
}
```

### 7.3 异步处理

**异步处理**：

- 使用Web Workers处理大型转换
- 异步加载资源
- 非阻塞UI操作

---

## 8. 测试与发布

### 8.1 单元测试

**测试示例**：

```typescript
// src/test/completion.test.ts
import * as assert from 'assert';
import { provideCompletionItems } from '../completion';

suite('Completion Tests', () => {
  test('should provide schema keyword completion', () => {
    const completions = provideCompletionItems(mockDocument, mockPosition);
    assert.ok(completions.some(c => c.label === 'schema'));
  });
});
```

### 8.2 集成测试

**集成测试**：

```typescript
// src/test/integration.test.ts
import * as vscode from 'vscode';

suite('Integration Tests', () => {
  test('should transform schema', async () => {
    const result = await transformCommand(mockContext);
    assert.ok(result);
  });
});
```

### 8.3 发布流程

**发布步骤**：

1. **构建**：`npm run build`
2. **打包**：`vsce package`
3. **测试**：本地测试
4. **发布**：`vsce publish`

---

**参考文档**：

- `tools/vscode-extension/` - VS Code插件代码实现
- `tools/vscode-extension/README.md` - 插件使用文档

**创建时间**：2025-01-21
**最后更新**：2025-01-21

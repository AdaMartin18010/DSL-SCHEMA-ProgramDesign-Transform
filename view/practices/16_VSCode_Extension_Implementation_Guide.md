# VS Code插件实施指南

## 📑 目录

- [VS Code插件实施指南](#vs-code插件实施指南)
  - [📑 目录](#-目录)
  - [1. 实施概述](#1-实施概述)
    - [1.1 实施目标](#11-实施目标)
    - [1.2 实施步骤](#12-实施步骤)
  - [2. 项目初始化](#2-项目初始化)
    - [2.1 项目结构](#21-项目结构)
    - [2.2 依赖安装](#22-依赖安装)
    - [2.3 配置设置](#23-配置设置)
  - [3. 核心功能实现](#3-核心功能实现)
    - [3.1 Schema编辑器实现](#31-schema编辑器实现)
    - [3.2 转换功能实现](#32-转换功能实现)
    - [3.3 验证功能实现](#33-验证功能实现)
  - [4. 用户界面实现](#4-用户界面实现)
    - [4.1 命令面板实现](#41-命令面板实现)
    - [4.2 状态栏实现](#42-状态栏实现)
    - [4.3 侧边栏实现](#43-侧边栏实现)
  - [5. 测试实现](#5-测试实现)
    - [5.1 单元测试](#51-单元测试)
    - [5.2 集成测试](#52-集成测试)
    - [5.3 端到端测试](#53-端到端测试)
  - [6. 打包与发布](#6-打包与发布)
    - [6.1 打包配置](#61-打包配置)
    - [6.2 发布准备](#62-发布准备)
    - [6.3 发布流程](#63-发布流程)
  - [7. 维护与更新](#7-维护与更新)
    - [7.1 版本管理](#71-版本管理)
    - [7.2 更新策略](#72-更新策略)
    - [7.3 用户反馈](#73-用户反馈)

---

## 1. 实施概述

### 1.1 实施目标

**实施目标**：

1. **功能完整**：实现所有核心功能
2. **性能优化**：响应速度快，资源占用低
3. **用户体验**：界面友好，操作直观
4. **稳定性**：稳定可靠，错误处理完善

### 1.2 实施步骤

**实施阶段**：

1. **阶段1**：项目初始化（Week 1）
2. **阶段2**：核心功能实现（Week 1-2）
3. **阶段3**：用户界面实现（Week 2）
4. **阶段4**：测试实现（Week 2-3）
5. **阶段5**：打包发布（Week 3）
6. **阶段6**：维护更新（持续）

---

## 2. 项目初始化

### 2.1 项目结构

**目录结构**：

```text
tools/vscode-extension/
├── src/
│   ├── extension.ts          # 插件入口
│   ├── completion.ts         # 自动补全
│   ├── diagnostics.ts        # 错误检查
│   ├── commands/             # 命令实现
│   ├── transformers/         # 转换器
│   ├── validators/           # 验证器
│   └── ui/                   # UI组件
├── syntaxes/
│   └── dsl.tmLanguage.json   # 语法定义
├── themes/
│   └── dsl-schema-color-theme.json
├── test/
│   ├── suite/
│   └── integration/
├── package.json
├── tsconfig.json
└── README.md
```

### 2.2 依赖安装

**package.json**：

```json
{
  "name": "dsl-schema-transformer",
  "displayName": "DSL Schema Transformer",
  "version": "1.0.0",
  "engines": {
    "vscode": "^1.80.0"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0"
  },
  "devDependencies": {
    "@types/vscode": "^1.80.0",
    "@types/node": "^18.0.0",
    "typescript": "^5.0.0",
    "@vscode/test-electron": "^2.0.0"
  }
}
```

### 2.3 配置设置

**tsconfig.json**：

```json
{
  "compilerOptions": {
    "module": "commonjs",
    "target": "ES2020",
    "outDir": "out",
    "lib": ["ES2020"],
    "sourceMap": true,
    "rootDir": "src",
    "strict": true
  },
  "exclude": ["node_modules", ".vscode-test"]
}
```

---

## 3. 核心功能实现

### 3.1 Schema编辑器实现

**编辑器激活**：

```typescript
// src/extension.ts
import * as vscode from 'vscode';
import { provideCompletionItems } from './completion';
import { validateDocument } from './diagnostics';

export function activate(context: vscode.ExtensionContext) {
  // 注册自动补全
  context.subscriptions.push(
    vscode.languages.registerCompletionItemProvider(
      'dsl-schema',
      { provideCompletionItems },
      '.'
    )
  );

  // 注册错误检查
  const diagnosticCollection = vscode.languages.createDiagnosticCollection('dsl-schema');
  context.subscriptions.push(diagnosticCollection);

  vscode.workspace.onDidChangeTextDocument(e => {
    if (e.document.languageId === 'dsl-schema') {
      const diagnostics = validateDocument(e.document);
      diagnosticCollection.set(e.document.uri, diagnostics);
    }
  });
}
```

### 3.2 转换功能实现

**转换命令注册**：

```typescript
// src/commands/transform.ts
import * as vscode from 'vscode';
import { TransformerRegistry } from '../transformers/registry';

export function registerTransformCommand(
  context: vscode.ExtensionContext
): void {
  const command = vscode.commands.registerCommand(
    'dsl-schema.transform',
    async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) {
        vscode.window.showErrorMessage('No active editor');
        return;
      }

      const formats = ['openapi', 'json-schema', 'asyncapi'];
      const selected = await vscode.window.showQuickPick(formats, {
        placeHolder: 'Select target format'
      });

      if (!selected) return;

      try {
        const schema = parseSchema(editor.document.getText());
        const transformer = TransformerRegistry.get(selected);
        const result = await transformer.transform(schema);

        const doc = await vscode.workspace.openTextDocument({
          content: JSON.stringify(result, null, 2),
          language: 'json'
        });

        await vscode.window.showTextDocument(doc);
      } catch (error) {
        vscode.window.showErrorMessage(`Transformation failed: ${error.message}`);
      }
    }
  );

  context.subscriptions.push(command);
}
```

### 3.3 验证功能实现

**验证实现**：

```typescript
// src/validators/schema-validator.ts
export class SchemaValidator {
  validate(schema: Schema): ValidationResult {
    const errors: ValidationError[] = [];

    // 验证Schema结构
    if (!schema.name) {
      errors.push({
        message: 'Schema name is required',
        severity: 'error'
      });
    }

    // 验证类型定义
    schema.types?.forEach(type => {
      const typeErrors = this.validateType(type);
      errors.push(...typeErrors);
    });

    return {
      valid: errors.length === 0,
      errors
    };
  }
}
```

---

## 4. 用户界面实现

### 4.1 命令面板实现

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
    ],
    "menus": {
      "commandPalette": [
        {
          "command": "dsl-schema.transform",
          "when": "editorLangId == dsl-schema"
        }
      ]
    }
  }
}
```

### 4.2 状态栏实现

**状态栏代码**：

```typescript
// src/ui/statusbar.ts
export class StatusBar {
  private statusBarItem: vscode.StatusBarItem;

  constructor() {
    this.statusBarItem = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Right,
      100
    );
    this.statusBarItem.command = 'dsl-schema.showStatus';
  }

  update(schema: Schema): void {
    const status = this.getStatus(schema);
    this.statusBarItem.text = `$(check) ${status}`;
    this.statusBarItem.show();
  }
}
```

### 4.3 侧边栏实现

**侧边栏代码**：

```typescript
// src/ui/sidebar.ts
export class SchemaExplorerProvider
  implements vscode.TreeDataProvider<SchemaNode> {

  private _onDidChangeTreeData = new vscode.EventEmitter<SchemaNode | undefined>();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  refresh(): void {
    this._onDidChangeTreeData.fire(undefined);
  }

  getTreeItem(element: SchemaNode): vscode.TreeItem {
    return element;
  }

  getChildren(element?: SchemaNode): Thenable<SchemaNode[]> {
    // 实现树节点获取逻辑
    return Promise.resolve([]);
  }
}
```

---

## 5. 测试实现

### 5.1 单元测试

**测试示例**：

```typescript
// src/test/completion.test.ts
import * as assert from 'assert';
import * as vscode from 'vscode';
import { provideCompletionItems } from '../completion';

suite('Completion Provider Tests', () => {
  test('should provide schema keyword', () => {
    const document = createMockDocument('sc');
    const position = new vscode.Position(0, 2);

    const completions = provideCompletionItems(document, position);

    assert.ok(completions.some(c => c.label === 'schema'));
  });
});
```

### 5.2 集成测试

**集成测试**：

```typescript
// src/test/integration.test.ts
import * as assert from 'assert';
import * as vscode from 'vscode';

suite('Extension Integration Tests', () => {
  test('should activate extension', async () => {
    const extension = vscode.extensions.getExtension('your-extension-id');
    assert.ok(extension);
    await extension.activate();
    assert.ok(extension.isActive);
  });
});
```

### 5.3 端到端测试

**E2E测试**：

```typescript
// src/test/e2e.test.ts
import * as assert from 'assert';
import * as vscode from 'vscode';

suite('E2E Tests', () => {
  test('should transform schema end-to-end', async () => {
    // 打开Schema文件
    const doc = await vscode.workspace.openTextDocument('test.dsl');
    await vscode.window.showTextDocument(doc);

    // 执行转换命令
    await vscode.commands.executeCommand('dsl-schema.transform');

    // 验证结果
    // ...
  });
});
```

---

## 6. 打包与发布

### 6.1 打包配置

**打包脚本**：

```json
// package.json
{
  "scripts": {
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./",
    "package": "vsce package",
    "publish": "vsce publish"
  }
}
```

### 6.2 发布准备

**发布检查清单**：

- [ ] 代码编译通过
- [ ] 所有测试通过
- [ ] 文档完整
- [ ] 版本号更新
- [ ] CHANGELOG更新

### 6.3 发布流程

**发布步骤**：

1. **构建**：`npm run compile`
2. **测试**：运行所有测试
3. **打包**：`npm run package`
4. **验证**：本地安装测试
5. **发布**：`npm run publish`

---

## 7. 维护与更新

### 7.1 版本管理

**版本策略**：

- **主版本号**：不兼容的API修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

### 7.2 更新策略

**更新机制**：

- 自动更新检查
- 用户通知
- 更新日志

### 7.3 用户反馈

**反馈渠道**：

- GitHub Issues
- 用户评价
- 功能请求

---

**参考文档**：

- `analysis/13_VSCode_Extension_Architecture.md` - 插件架构设计
- `tools/vscode-extension/` - 插件代码实现

**创建时间**：2025-01-21
**最后更新**：2025-01-21

/**
 * schemaEditor.ts
 * 
 * DSL Schema Transform - Schema Editor Module
 * 
 * This module provides a custom webview-based editor for DSL schema files.
 * It allows users to edit schema definitions with visual assistance,
 * syntax highlighting, and real-time validation.
 * 
 * @module schemaEditor
 * @author DSL Schema Team
 * @version 0.1.0
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

/**
 * SchemaEditorProvider class
 * 
 * Manages the custom webview editor for DSL schema files.
 * Handles file opening, editing, saving, and provides a rich UI
 * for schema manipulation.
 */
export class SchemaEditorProvider {
    /**
     * Reference to the extension context
     */
    private context: vscode.ExtensionContext;

    /**
     * Output channel for logging
     */
    private outputChannel: vscode.OutputChannel;

    /**
     * Map of active webview panels
     */
    private activePanels: Map<string, vscode.WebviewPanel>;

    /**
     * Current editor theme
     */
    private theme: string;

    /**
     * Create a new SchemaEditorProvider instance
     * 
     * @param context - The VS Code extension context
     * @param outputChannel - The output channel for logging
     */
    constructor(
        context: vscode.ExtensionContext,
        outputChannel: vscode.OutputChannel
    ) {
        this.context = context;
        this.outputChannel = outputChannel;
        this.activePanels = new Map();
        this.theme = 'default';

        // Load initial settings
        this.reloadSettings();

        this.outputChannel.appendLine('SchemaEditorProvider initialized');
    }

    /**
     * Dispose of resources when the extension is deactivated
     */
    public dispose(): void {
        // Dispose all active panels
        this.activePanels.forEach((panel) => {
            panel.dispose();
        });
        this.activePanels.clear();

        this.outputChannel.appendLine('SchemaEditorProvider disposed');
    }

    /**
     * Reload settings from VS Code configuration
     */
    public reloadSettings(): void {
        const config = vscode.workspace.getConfiguration('dslSchemaTransform');
        this.theme = config.get<string>('editor.theme', 'default');
        this.outputChannel.appendLine(`Schema editor theme set to: ${this.theme}`);
    }

    /**
     * Open a schema file in the custom editor
     * 
     * @param uri - Optional URI of the file to open. If not provided, uses the active editor
     * @returns Promise that resolves when the editor is opened
     */
    public async openEditor(uri?: vscode.Uri): Promise<void> {
        // Get the target URI
        const targetUri = await this.getTargetUri(uri);
        if (!targetUri) {
            throw new Error('No file selected to open');
        }

        // Check if file is already open
        const filePath = targetUri.fsPath;
        if (this.activePanels.has(filePath)) {
            // Reveal existing panel
            const existingPanel = this.activePanels.get(filePath)!;
            existingPanel.reveal(vscode.ViewColumn.One);
            this.outputChannel.appendLine(`Revealed existing editor for: ${filePath}`);
            return;
        }

        // Load file content
        const content = await this.loadFileContent(targetUri);

        // Create and configure webview panel
        const panel = this.createWebviewPanel(targetUri);

        // Set initial HTML content
        panel.webview.html = this.getEditorHtml(panel.webview, content, filePath);

        // Set up message handling
        this.setupMessageHandling(panel, targetUri);

        // Store panel reference
        this.activePanels.set(filePath, panel);

        // Handle panel disposal
        panel.onDidDispose(() => {
            this.activePanels.delete(filePath);
            this.outputChannel.appendLine(`Closed editor for: ${filePath}`);
        });

        this.outputChannel.appendLine(`Opened schema editor for: ${filePath}`);
    }

    /**
     * Get the target URI from parameter or active editor
     * 
     * @param uri - Optional URI
     * @returns The target URI or undefined
     */
    private async getTargetUri(uri?: vscode.Uri): Promise<vscode.Uri | undefined> {
        if (uri) {
            return uri;
        }

        // Try to get from active editor
        const activeEditor = vscode.window.activeTextEditor;
        if (activeEditor) {
            return activeEditor.document.uri;
        }

        // Show file picker
        const selectedFiles = await vscode.window.showOpenDialog({
            canSelectFiles: true,
            canSelectFolders: false,
            canSelectMany: false,
            filters: {
                'Schema Files': ['dsl', 'schema', 'json'],
                'All Files': ['*']
            },
            openLabel: 'Open Schema'
        });

        return selectedFiles?.[0];
    }

    /**
     * Load content from a file URI
     * 
     * @param uri - The file URI
     * @returns The file content as string
     */
    private async loadFileContent(uri: vscode.Uri): Promise<string> {
        try {
            const document = await vscode.workspace.openTextDocument(uri);
            return document.getText();
        } catch (error) {
            this.outputChannel.appendLine(`Error loading file: ${error}`);
            return '{}';
        }
    }

    /**
     * Create a new webview panel for the schema editor
     * 
     * @param uri - The URI of the file being edited
     * @returns The created webview panel
     */
    private createWebviewPanel(uri: vscode.Uri): vscode.WebviewPanel {
        const fileName = path.basename(uri.fsPath);

        return vscode.window.createWebviewPanel(
            'dslSchemaEditor',
            `Schema Editor: ${fileName}`,
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: [
                    vscode.Uri.file(path.join(this.context.extensionPath, 'media'))
                ],
                enableCommandUris: true
            }
        );
    }

    /**
     * Set up message handling between webview and extension
     * 
     * @param panel - The webview panel
     * @param uri - The URI of the file being edited
     */
    private setupMessageHandling(
        panel: vscode.WebviewPanel,
        uri: vscode.Uri
    ): void {
        panel.webview.onDidReceiveMessage(
            async (message) => {
                switch (message.command) {
                    case 'save':
                        await this.handleSave(message.content, uri);
                        break;

                    case 'validate':
                        await this.handleValidate(message.content);
                        break;

                    case 'transform':
                        await this.handleTransform(message.content);
                        break;

                    case 'updateTheme':
                        this.handleThemeUpdate(message.theme);
                        break;

                    case 'log':
                        this.outputChannel.appendLine(`[Webview] ${message.message}`);
                        break;

                    case 'error':
                        this.outputChannel.appendLine(`[Webview Error] ${message.message}`);
                        vscode.window.showErrorMessage(message.message);
                        break;

                    case 'getSchemaTemplate':
                        await this.sendSchemaTemplate(panel);
                        break;

                    case 'addNode':
                        await this.handleAddNode(message.nodeType, panel);
                        break;

                    case 'deleteNode':
                        await this.handleDeleteNode(message.nodeId, panel);
                        break;

                    default:
                        this.outputChannel.appendLine(`Unknown command: ${message.command}`);
                }
            },
            undefined,
            this.context.subscriptions
        );
    }

    /**
     * Handle save command from webview
     * 
     * @param content - The content to save
     * @param uri - The target file URI
     */
    private async handleSave(content: string, uri: vscode.Uri): Promise<void> {
        try {
            const edit = new vscode.WorkspaceEdit();
            const document = await vscode.workspace.openTextDocument(uri);

            // Replace entire document content
            const fullRange = new vscode.Range(
                document.positionAt(0),
                document.positionAt(document.getText().length)
            );

            edit.replace(uri, fullRange, content);
            await vscode.workspace.applyEdit(edit);
            await document.save();

            vscode.window.showInformationMessage('Schema saved successfully');
            this.outputChannel.appendLine(`Saved: ${uri.fsPath}`);
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            vscode.window.showErrorMessage(`Failed to save: ${errorMessage}`);
            this.outputChannel.appendLine(`Save error: ${errorMessage}`);
        }
    }

    /**
     * Handle validate command from webview
     * 
     * @param content - The schema content to validate
     */
    private async handleValidate(content: string): Promise<void> {
        try {
            const schema = JSON.parse(content);
            // Perform validation logic here
            // This is a placeholder - actual validation would use AJV or similar
            const isValid = this.validateSchemaStructure(schema);

            if (isValid) {
                vscode.window.showInformationMessage('Schema is valid');
            } else {
                vscode.window.showWarningMessage('Schema has validation warnings');
            }
        } catch (error) {
            vscode.window.showErrorMessage('Invalid JSON format');
        }
    }

    /**
     * Handle transform command from webview
     * 
     * @param content - The schema content to transform
     */
    private async handleTransform(content: string): Promise<void> {
        try {
            // Trigger transformation via command
            await vscode.commands.executeCommand('dslSchemaTransform.transformProgram');
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            vscode.window.showErrorMessage(`Transform failed: ${errorMessage}`);
        }
    }

    /**
     * Handle theme update from webview
     * 
     * @param theme - The new theme name
     */
    private handleThemeUpdate(theme: string): void {
        this.theme = theme;
        const config = vscode.workspace.getConfiguration('dslSchemaTransform');
        config.update('editor.theme', theme, true);
    }

    /**
     * Send a schema template to the webview
     * 
     * @param panel - The webview panel
     */
    private async sendSchemaTemplate(panel: vscode.WebviewPanel): Promise<void> {
        const template = this.getSchemaTemplate();
        panel.webview.postMessage({
            command: 'schemaTemplate',
            template: template
        });
    }

    /**
     * Handle add node command
     * 
     * @param nodeType - The type of node to add
     * @param panel - The webview panel
     */
    private async handleAddNode(
        nodeType: string,
        panel: vscode.WebviewPanel
    ): Promise<void> {
        const nodeTemplate = this.getNodeTemplate(nodeType);
        panel.webview.postMessage({
            command: 'addNodeResponse',
            node: nodeTemplate
        });
    }

    /**
     * Handle delete node command
     * 
     * @param nodeId - The ID of the node to delete
     * @param panel - The webview panel
     */
    private async handleDeleteNode(
        nodeId: string,
        panel: vscode.WebviewPanel
    ): Promise<void> {
        // Node deletion is handled in the webview
        this.outputChannel.appendLine(`Deleting node: ${nodeId}`);
    }

    /**
     * Validate schema structure
     * 
     * @param schema - The schema object to validate
     * @returns True if valid
     */
    private validateSchemaStructure(schema: unknown): boolean {
        // Basic structure validation
        if (typeof schema !== 'object' || schema === null) {
            return false;
        }

        const schemaObj = schema as Record<string, unknown>;

        // Check required fields
        if (!schemaObj.name || typeof schemaObj.name !== 'string') {
            return false;
        }

        return true;
    }

    /**
     * Get a schema template
     * @returns The template object
     */
    private getSchemaTemplate(): Record<string, unknown> {
        return {
            name: 'NewSchema',
            version: '1.0.0',
            description: 'Schema description',
            nodes: [],
            edges: [],
            metadata: {
                created: new Date().toISOString(),
                author: 'DSL Schema Editor'
            }
        };
    }

    /**
     * Get a node template by type
     * 
     * @param nodeType - The type of node
     * @returns The node template
     */
    private getNodeTemplate(nodeType: string): Record<string, unknown> {
        const templates: Record<string, Record<string, unknown>> = {
            'process': {
                id: `node_${Date.now()}`,
                type: 'process',
                name: 'New Process',
                inputs: [],
                outputs: [],
                properties: {}
            },
            'data': {
                id: `node_${Date.now()}`,
                type: 'data',
                name: 'New Data',
                schema: {},
                properties: {}
            },
            'control': {
                id: `node_${Date.now()}`,
                type: 'control',
                name: 'New Control',
                condition: '',
                properties: {}
            },
            'default': {
                id: `node_${Date.now()}`,
                type: 'default',
                name: 'New Node',
                properties: {}
            }
        };

        return templates[nodeType] || templates['default'];
    }

    /**
     * Generate the HTML for the schema editor
     * 
     * @param webview - The webview instance
     * @param content - The initial content
     * @param filePath - The file path
     * @returns The HTML string
     */
    private getEditorHtml(
        webview: vscode.Webview,
        content: string,
        filePath: string
    ): string {
        // Get CSP source
        const cspSource = webview.cspSource;

        // Get theme CSS
        const themeCss = this.getThemeCss();

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="
        default-src 'none';
        style-src ${cspSource} 'unsafe-inline';
        script-src ${cspSource} 'unsafe-inline';
        connect-src ${cspSource};
    ">
    <title>DSL Schema Editor</title>
    <style>
        ${themeCss}
    </style>
</head>
<body>
    <div id="app">
        <header class="editor-header">
            <h1>Schema Editor</h1>
            <div class="toolbar">
                <button id="btnSave" class="btn btn-primary">Save</button>
                <button id="btnValidate" class="btn btn-secondary">Validate</button>
                <button id="btnTransform" class="btn btn-secondary">Transform</button>
                <select id="themeSelect" class="select">
                    <option value="default" ${this.theme === 'default' ? 'selected' : ''}>Default</option>
                    <option value="dark" ${this.theme === 'dark' ? 'selected' : ''}>Dark</option>
                    <option value="light" ${this.theme === 'light' ? 'selected' : ''}>Light</option>
                </select>
            </div>
        </header>

        <div class="editor-container">
            <aside class="sidebar">
                <h3>Node Types</h3>
                <div class="node-palette">
                    <div class="node-item" data-type="process">Process</div>
                    <div class="node-item" data-type="data">Data</div>
                    <div class="node-item" data-type="control">Control</div>
                </div>
                <h3>Properties</h3>
                <div id="propertiesPanel" class="properties-panel">
                    <p>Select a node to edit properties</p>
                </div>
            </aside>

            <main class="editor-main">
                <div class="tabs">
                    <button class="tab active" data-tab="visual">Visual</button>
                    <button class="tab" data-tab="json">JSON</button>
                </div>

                <div id="visualTab" class="tab-content active">
                    <div id="canvas" class="canvas">
                        <div class="canvas-placeholder">
                            Drag nodes here or add from palette
                        </div>
                    </div>
                </div>

                <div id="jsonTab" class="tab-content">
                    <textarea id="jsonEditor" class="json-editor" spellcheck="false">${this.escapeHtml(content)}</textarea>
                </div>
            </main>
        </div>

        <footer class="editor-footer">
            <span id="statusText">Ready</span>
            <span id="filePath">${this.escapeHtml(filePath)}</span>
        </footer>
    </div>

    <script>
        (function() {
            const vscode = acquireVsCodeApi();
            let currentContent = ${JSON.stringify(content)};
            let isDirty = false;

            // Initialize
            document.addEventListener('DOMContentLoaded', () => {
                initializeEditor();
            });

            function initializeEditor() {
                // Save button
                document.getElementById('btnSave').addEventListener('click', () => {
                    saveContent();
                });

                // Validate button
                document.getElementById('btnValidate').addEventListener('click', () => {
                    validateContent();
                });

                // Transform button
                document.getElementById('btnTransform').addEventListener('click', () => {
                    transformContent();
                });

                // Theme selector
                document.getElementById('themeSelect').addEventListener('change', (e) => {
                    updateTheme(e.target.value);
                });

                // Tab switching
                document.querySelectorAll('.tab').forEach(tab => {
                    tab.addEventListener('click', () => {
                        switchTab(tab.dataset.tab);
                    });
                });

                // Node palette items
                document.querySelectorAll('.node-item').forEach(item => {
                    item.addEventListener('click', () => {
                        addNode(item.dataset.type);
                    });
                });

                // JSON editor changes
                document.getElementById('jsonEditor').addEventListener('input', (e) => {
                    currentContent = e.target.value;
                    isDirty = true;
                    updateStatus('Modified');
                });

                // Listen for messages from extension
                window.addEventListener('message', (event) => {
                    const message = event.data;
                    switch (message.command) {
                        case 'schemaTemplate':
                            loadTemplate(message.template);
                            break;
                        case 'addNodeResponse':
                            addNodeToCanvas(message.node);
                            break;
                    }
                });

                updateStatus('Ready');
            }

            function saveContent() {
                try {
                    // Validate JSON before saving
                    JSON.parse(currentContent);
                    vscode.postMessage({
                        command: 'save',
                        content: currentContent
                    });
                    isDirty = false;
                    updateStatus('Saved');
                } catch (error) {
                    showError('Invalid JSON: ' + error.message);
                }
            }

            function validateContent() {
                vscode.postMessage({
                    command: 'validate',
                    content: currentContent
                });
                updateStatus('Validating...');
            }

            function transformContent() {
                vscode.postMessage({
                    command: 'transform',
                    content: currentContent
                });
                updateStatus('Transforming...');
            }

            function updateTheme(theme) {
                vscode.postMessage({
                    command: 'updateTheme',
                    theme: theme
                });
                document.body.className = 'theme-' + theme;
            }

            function switchTab(tabName) {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
                
                document.querySelector('[data-tab="' + tabName + '"]').classList.add('active');
                document.getElementById(tabName + 'Tab').classList.add('active');
            }

            function addNode(nodeType) {
                vscode.postMessage({
                    command: 'addNode',
                    nodeType: nodeType
                });
            }

            function addNodeToCanvas(node) {
                const canvas = document.getElementById('canvas');
                const placeholder = canvas.querySelector('.canvas-placeholder');
                if (placeholder) {
                    placeholder.remove();
                }

                const nodeEl = document.createElement('div');
                nodeEl.className = 'canvas-node';
                nodeEl.innerHTML = '<strong>' + node.name + '</strong><br><small>' + node.type + '</small>';
                nodeEl.style.left = '50px';
                nodeEl.style.top = '50px';
                
                // Make draggable (simplified)
                nodeEl.draggable = true;
                
                canvas.appendChild(nodeEl);
                updateStatus('Node added: ' + node.name);
            }

            function loadTemplate(template) {
                currentContent = JSON.stringify(template, null, 2);
                document.getElementById('jsonEditor').value = currentContent;
                isDirty = true;
                updateStatus('Template loaded');
            }

            function updateStatus(text) {
                document.getElementById('statusText').textContent = text + (isDirty ? ' (modified)' : '');
            }

            function showError(message) {
                vscode.postMessage({
                    command: 'error',
                    message: message
                });
            }

            // Auto-save on Ctrl+S
            document.addEventListener('keydown', (e) => {
                if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                    e.preventDefault();
                    saveContent();
                }
            });
        })();
    </script>
</body>
</html>`;
    }

    /**
     * Get theme CSS based on current theme setting
     * @returns CSS string
     */
    private getThemeCss(): string {
        const baseCss = `
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: var(--vscode-font-family, -apple-system, sans-serif);
                font-size: var(--vscode-font-size, 13px);
                color: var(--vscode-foreground, #333);
                background: var(--vscode-editor-background, #fff);
                height: 100vh;
                overflow: hidden;
            }
            #app { display: flex; flex-direction: column; height: 100vh; }
            .editor-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px 15px;
                background: var(--vscode-titleBar-activeBackground, #f0f0f0);
                border-bottom: 1px solid var(--vscode-panel-border, #ddd);
            }
            .editor-header h1 { font-size: 14px; font-weight: 600; }
            .toolbar { display: flex; gap: 8px; align-items: center; }
            .btn {
                padding: 6px 12px;
                border: none;
                border-radius: 3px;
                cursor: pointer;
                font-size: 12px;
                font-weight: 500;
                transition: opacity 0.2s;
            }
            .btn:hover { opacity: 0.8; }
            .btn-primary {
                background: var(--vscode-button-background, #007acc);
                color: var(--vscode-button-foreground, #fff);
            }
            .btn-secondary {
                background: var(--vscode-button-secondaryBackground, #5a5a5a);
                color: var(--vscode-button-secondaryForeground, #fff);
            }
            .select {
                padding: 5px 10px;
                border: 1px solid var(--vscode-dropdown-border, #ddd);
                border-radius: 3px;
                background: var(--vscode-dropdown-background, #fff);
                color: var(--vscode-dropdown-foreground, #333);
                font-size: 12px;
            }
            .editor-container {
                flex: 1;
                display: flex;
                overflow: hidden;
            }
            .sidebar {
                width: 200px;
                background: var(--vscode-sideBar-background, #f5f5f5);
                border-right: 1px solid var(--vscode-panel-border, #ddd);
                padding: 15px;
                overflow-y: auto;
            }
            .sidebar h3 {
                font-size: 11px;
                text-transform: uppercase;
                color: var(--vscode-sideBarSectionHeader-foreground, #666);
                margin: 15px 0 10px;
                padding-bottom: 5px;
                border-bottom: 1px solid var(--vscode-panel-border, #ddd);
            }
            .sidebar h3:first-child { margin-top: 0; }
            .node-palette { display: flex; flex-direction: column; gap: 8px; }
            .node-item {
                padding: 10px;
                background: var(--vscode-button-secondaryBackground, #e0e0e0);
                border-radius: 4px;
                cursor: pointer;
                text-align: center;
                font-size: 12px;
                transition: all 0.2s;
            }
            .node-item:hover {
                background: var(--vscode-button-background, #007acc);
                color: var(--vscode-button-foreground, #fff);
            }
            .properties-panel {
                padding: 10px;
                background: var(--vscode-input-background, #fff);
                border: 1px solid var(--vscode-input-border, #ddd);
                border-radius: 4px;
                font-size: 12px;
                min-height: 100px;
            }
            .editor-main {
                flex: 1;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            .tabs {
                display: flex;
                background: var(--vscode-tab-inactiveBackground, #f0f0f0);
                border-bottom: 1px solid var(--vscode-panel-border, #ddd);
            }
            .tab {
                padding: 8px 20px;
                border: none;
                background: transparent;
                cursor: pointer;
                font-size: 12px;
                color: var(--vscode-tab-inactiveForeground, #666);
                border-bottom: 2px solid transparent;
            }
            .tab.active {
                color: var(--vscode-tab-activeForeground, #333);
                background: var(--vscode-tab-activeBackground, #fff);
                border-bottom-color: var(--vscode-tab-activeForeground, #007acc);
            }
            .tab-content {
                flex: 1;
                display: none;
                overflow: hidden;
            }
            .tab-content.active { display: flex; }
            .canvas {
                flex: 1;
                position: relative;
                background: var(--vscode-editor-background, #fff);
                background-image: 
                    linear-gradient(var(--vscode-panel-border, #eee) 1px, transparent 1px),
                    linear-gradient(90deg, var(--vscode-panel-border, #eee) 1px, transparent 1px);
                background-size: 20px 20px;
            }
            .canvas-placeholder {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: var(--vscode-descriptionForeground, #999);
                font-size: 14px;
            }
            .canvas-node {
                position: absolute;
                padding: 10px 15px;
                background: var(--vscode-button-background, #007acc);
                color: var(--vscode-button-foreground, #fff);
                border-radius: 6px;
                cursor: move;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                user-select: none;
            }
            .json-editor {
                flex: 1;
                width: 100%;
                border: none;
                padding: 15px;
                font-family: var(--vscode-editor-font-family, 'Consolas', monospace);
                font-size: var(--vscode-editor-font-size, 13px);
                line-height: 1.5;
                background: var(--vscode-editor-background, #fff);
                color: var(--vscode-editor-foreground, #333);
                resize: none;
                outline: none;
            }
            .editor-footer {
                display: flex;
                justify-content: space-between;
                padding: 5px 15px;
                background: var(--vscode-statusBar-background, #007acc);
                color: var(--vscode-statusBar-foreground, #fff);
                font-size: 11px;
            }
        `;

        // Theme-specific overrides
        const darkTheme = `
            .theme-dark .sidebar { background: #252526; }
            .theme-dark .canvas { background: #1e1e1e; }
            .theme-dark .json-editor { background: #1e1e1e; color: #d4d4d4; }
        `;

        const lightTheme = `
            .theme-light .sidebar { background: #f3f3f3; }
            .theme-light .canvas { background: #ffffff; }
            .theme-light .json-editor { background: #ffffff; color: #333333; }
        `;

        return baseCss + darkTheme + lightTheme;
    }

    /**
     * Escape HTML special characters
     * 
     * @param text - The text to escape
     * @returns Escaped text
     */
    private escapeHtml(text: string): string {
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
}

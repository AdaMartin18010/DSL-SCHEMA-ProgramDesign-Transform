/**
 * transformCommands.ts
 * 
 * DSL Schema Transform - Transform Commands Module
 * 
 * This module provides commands for transforming DSL schema files into
 * various target formats and languages. It includes validation, code
 * generation, and preview functionality.
 * 
 * @module transformCommands
 * @author DSL Schema Team
 * @version 0.1.0
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

/**
 * Interface for transformation options
 */
interface TransformOptions {
    /** Target language for code generation */
    targetLanguage: string;
    /** Whether to auto-format the output */
    autoFormat: boolean;
    /** Output directory path */
    outputDir?: string;
    /** Strict validation mode */
    strictMode: boolean;
}

/**
 * Interface for schema validation result
 */
interface ValidationResult {
    /** Whether the schema is valid */
    valid: boolean;
    /** Array of validation errors */
    errors: ValidationError[];
    /** Array of validation warnings */
    warnings: ValidationError[];
}

/**
 * Interface for validation error/warning
 */
interface ValidationError {
    /** Error message */
    message: string;
    /** Path to the error location */
    path: string;
    /** Severity level */
    severity: 'error' | 'warning';
    /** Line number if available */
    line?: number;
    /** Column number if available */
    column?: number;
}

/**
 * Interface for transformation result
 */
interface TransformResult {
    /** Whether transformation succeeded */
    success: boolean;
    /** Generated output content */
    output?: string;
    /** Error message if failed */
    error?: string;
    /** Output file path */
    outputPath?: string;
}

/**
 * TransformCommands class
 * 
 * Handles all transformation-related commands including validation,
 * code generation, and preview generation for DSL schema files.
 */
export class TransformCommands {
    /**
     * Reference to the extension context
     */
    private context: vscode.ExtensionContext;

    /**
     * Output channel for logging
     */
    private outputChannel: vscode.OutputChannel;

    /**
     * Current transformation options
     */
    private options: TransformOptions;

    /**
     * Preview content cache
     */
    private previewCache: Map<string, string>;

    /**
     * Diagnostic collection for validation errors
     */
    private diagnosticCollection: vscode.DiagnosticCollection;

    /**
     * Create a new TransformCommands instance
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
        this.previewCache = new Map();
        this.diagnosticCollection = vscode.languages.createDiagnosticCollection('dslSchema');
        
        // Load initial settings
        this.reloadSettings();

        this.outputChannel.appendLine('TransformCommands initialized');
    }

    /**
     * Dispose of resources when the extension is deactivated
     */
    public dispose(): void {
        this.diagnosticCollection.dispose();
        this.previewCache.clear();
        this.outputChannel.appendLine('TransformCommands disposed');
    }

    /**
     * Reload settings from VS Code configuration
     */
    public reloadSettings(): void {
        const config = vscode.workspace.getConfiguration('dslSchemaTransform');
        
        this.options = {
            targetLanguage: config.get<string>('output.targetLanguage', 'typescript'),
            autoFormat: config.get<boolean>('transform.autoFormat', true),
            strictMode: config.get<boolean>('schemaValidation.strictMode', false)
        };

        this.outputChannel.appendLine(`Transform settings loaded: ${JSON.stringify(this.options)}`);
    }

    /**
     * Execute the main transform command
     * 
     * @param uri - Optional URI of the file to transform
     */
    public async executeTransform(uri?: vscode.Uri): Promise<void> {
        const targetUri = await this.getTargetUri(uri);
        if (!targetUri) {
            vscode.window.showWarningMessage('No file selected for transformation');
            return;
        }

        this.outputChannel.appendLine(`Starting transformation for: ${targetUri.fsPath}`);

        try {
            // Read and parse the schema file
            const content = await this.readFileContent(targetUri);
            const schema = this.parseSchema(content);

            // Validate before transformation
            const validationResult = await this.validateSchemaInternal(schema);
            if (!validationResult.valid && this.options.strictMode) {
                this.showValidationErrors(validationResult);
                throw new Error('Schema validation failed. Fix errors before transforming.');
            }

            // Ask user for target language if not configured
            const targetLanguage = await this.selectTargetLanguage();
            if (!targetLanguage) {
                return; // User cancelled
            }

            // Ask for output location
            const outputUri = await this.selectOutputLocation(targetUri, targetLanguage);
            if (!outputUri) {
                return; // User cancelled
            }

            // Perform transformation
            const result = await this.transformSchema(schema, targetLanguage);

            if (result.success && result.output) {
                // Write output file
                await this.writeOutputFile(outputUri, result.output);
                
                // Show success message
                const openFile = await vscode.window.showInformationMessage(
                    `Transformation complete! Output saved to: ${path.basename(outputUri.fsPath)}`,
                    'Open File',
                    'Open Folder'
                );

                if (openFile === 'Open File') {
                    const doc = await vscode.workspace.openTextDocument(outputUri);
                    await vscode.window.showTextDocument(doc);
                } else if (openFile === 'Open Folder') {
                    vscode.commands.executeCommand('revealFileInOS', outputUri);
                }

                this.outputChannel.appendLine(`Transformation successful: ${outputUri.fsPath}`);
            } else {
                throw new Error(result.error || 'Transformation failed');
            }
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            this.outputChannel.appendLine(`Transformation error: ${errorMessage}`);
            vscode.window.showErrorMessage(`Transformation failed: ${errorMessage}`);
        }
    }

    /**
     * Validate a schema file
     * 
     * @param uri - Optional URI of the file to validate
     */
    public async validateSchema(uri?: vscode.Uri): Promise<void> {
        const targetUri = await this.getTargetUri(uri);
        if (!targetUri) {
            vscode.window.showWarningMessage('No file selected for validation');
            return;
        }

        this.outputChannel.appendLine(`Validating: ${targetUri.fsPath}`);

        try {
            const content = await this.readFileContent(targetUri);
            const schema = this.parseSchema(content);
            const result = await this.validateSchemaInternal(schema);

            // Clear previous diagnostics for this file
            this.diagnosticCollection.delete(targetUri);

            if (result.valid && result.warnings.length === 0) {
                vscode.window.showInformationMessage('✅ Schema is valid!');
            } else {
                this.showValidationErrors(result);
                
                // Set diagnostics for the file
                const diagnostics = this.createDiagnostics(result);
                this.diagnosticCollection.set(targetUri, diagnostics);

                if (result.valid) {
                    vscode.window.showWarningMessage(
                        `⚠️ Schema is valid but has ${result.warnings.length} warning(s)`
                    );
                } else {
                    vscode.window.showErrorMessage(
                        `❌ Schema has ${result.errors.length} error(s)`
                    );
                }
            }

            this.outputChannel.appendLine(
                `Validation complete: ${result.errors.length} errors, ${result.warnings.length} warnings`
            );
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            this.outputChannel.appendLine(`Validation error: ${errorMessage}`);
            vscode.window.showErrorMessage(`Validation failed: ${errorMessage}`);
        }
    }

    /**
     * Generate a preview of the transformation
     * 
     * @param uri - Optional URI of the file to preview
     */
    public async previewTransformation(uri?: vscode.Uri): Promise<void> {
        const targetUri = await this.getTargetUri(uri);
        if (!targetUri) {
            return;
        }

        try {
            const content = await this.readFileContent(targetUri);
            const schema = this.parseSchema(content);

            // Generate preview in a new untitled document
            const result = await this.transformSchema(schema, this.options.targetLanguage);

            if (result.success && result.output) {
                // Create a preview URI
                const previewUri = vscode.Uri.parse(
                    `dsl-schema-preview:${targetUri.path}.preview`
                );
                
                // Cache the preview content
                this.previewCache.set(previewUri.toString(), result.output);

                // Open the preview document
                const doc = await vscode.workspace.openTextDocument(previewUri);
                await vscode.window.showTextDocument(doc, {
                    preview: true,
                    viewColumn: vscode.ViewColumn.Two
                });

                this.outputChannel.appendLine(`Preview generated for: ${targetUri.fsPath}`);
            }
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            vscode.window.showErrorMessage(`Preview generation failed: ${errorMessage}`);
        }
    }

    /**
     * Generate code from schema
     * 
     * @param uri - Optional URI of the file to generate code from
     */
    public async generateCode(uri?: vscode.Uri): Promise<void> {
        const targetUri = await this.getTargetUri(uri);
        if (!targetUri) {
            return;
        }

        // Show quick pick for code generation options
        const options = [
            { label: '$(file-code) TypeScript', language: 'typescript', description: 'Generate TypeScript code' },
            { label: '$(file-code) JavaScript', language: 'javascript', description: 'Generate JavaScript code' },
            { label: '$(file-code) Python', language: 'python', description: 'Generate Python code' },
            { label: '$(file-code) Java', language: 'java', description: 'Generate Java code' },
            { label: '$(file-code) C++', language: 'cpp', description: 'Generate C++ code' }
        ];

        const selected = await vscode.window.showQuickPick(options, {
            placeHolder: 'Select target language for code generation'
        });

        if (!selected) {
            return;
        }

        try {
            const content = await this.readFileContent(targetUri);
            const schema = this.parseSchema(content);
            const result = await this.transformSchema(schema, selected.language);

            if (result.success && result.output) {
                // Create output file path
                const ext = this.getFileExtension(selected.language);
                const outputPath = targetUri.fsPath.replace(/\.\w+$/, `.generated.${ext}`);
                const outputUri = vscode.Uri.file(outputPath);

                await this.writeOutputFile(outputUri, result.output);

                const action = await vscode.window.showInformationMessage(
                    `Code generated: ${path.basename(outputPath)}`,
                    'Open',
                    'Open Folder'
                );

                if (action === 'Open') {
                    const doc = await vscode.workspace.openTextDocument(outputUri);
                    await vscode.window.showTextDocument(doc);
                } else if (action === 'Open Folder') {
                    vscode.commands.executeCommand('revealFileInOS', outputUri);
                }
            }
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            vscode.window.showErrorMessage(`Code generation failed: ${errorMessage}`);
        }
    }

    /**
     * Get preview content for a URI
     * Used by the preview content provider
     * 
     * @param uri - The preview URI
     * @returns The preview content
     */
    public getPreviewContent(uri: vscode.Uri): string {
        const cached = this.previewCache.get(uri.toString());
        return cached || '// No preview available';
    }

    /**
     * Get the target URI from parameter or active editor
     */
    private async getTargetUri(uri?: vscode.Uri): Promise<vscode.Uri | undefined> {
        if (uri) {
            return uri;
        }

        const activeEditor = vscode.window.activeTextEditor;
        if (activeEditor) {
            return activeEditor.document.uri;
        }

        const files = await vscode.window.showOpenDialog({
            canSelectFiles: true,
            canSelectFolders: false,
            canSelectMany: false,
            filters: {
                'Schema Files': ['dsl', 'schema', 'json'],
                'All Files': ['*']
            }
        });

        return files?.[0];
    }

    /**
     * Read file content from URI
     */
    private async readFileContent(uri: vscode.Uri): Promise<string> {
        const document = await vscode.workspace.openTextDocument(uri);
        return document.getText();
    }

    /**
     * Parse schema content (JSON or YAML)
     */
    private parseSchema(content: string): unknown {
        try {
            // Try JSON first
            return JSON.parse(content);
        } catch {
            // If JSON fails, it might be YAML
            // In a real implementation, use a YAML parser
            throw new Error('Invalid schema format. Expected valid JSON.');
        }
    }

    /**
     * Validate schema internally
     */
    private async validateSchemaInternal(schema: unknown): Promise<ValidationResult> {
        const result: ValidationResult = {
            valid: true,
            errors: [],
            warnings: []
        };

        // Check if schema is an object
        if (typeof schema !== 'object' || schema === null) {
            result.valid = false;
            result.errors.push({
                message: 'Schema must be an object',
                path: '',
                severity: 'error'
            });
            return result;
        }

        const schemaObj = schema as Record<string, unknown>;

        // Check required fields
        if (!schemaObj.name) {
            result.errors.push({
                message: 'Schema must have a "name" field',
                path: '/name',
                severity: 'error'
            });
            result.valid = false;
        }

        // Check version format
        if (schemaObj.version && typeof schemaObj.version !== 'string') {
            result.errors.push({
                message: 'Version must be a string',
                path: '/version',
                severity: 'error'
            });
            result.valid = false;
        }

        // Validate nodes array
        if (schemaObj.nodes) {
            if (!Array.isArray(schemaObj.nodes)) {
                result.errors.push({
                    message: '"nodes" must be an array',
                    path: '/nodes',
                    severity: 'error'
                });
                result.valid = false;
            } else {
                // Validate each node
                schemaObj.nodes.forEach((node: unknown, index: number) => {
                    if (typeof node !== 'object' || node === null) {
                        result.errors.push({
                            message: `Node at index ${index} must be an object`,
                            path: `/nodes/${index}`,
                            severity: 'error'
                        });
                    }
                });
            }
        }

        // Add warnings for optional but recommended fields
        if (!schemaObj.description) {
            result.warnings.push({
                message: 'Schema should have a "description" field',
                path: '/description',
                severity: 'warning'
            });
        }

        return result;
    }

    /**
     * Show validation errors to the user
     */
    private showValidationErrors(result: ValidationResult): void {
        if (result.errors.length > 0) {
            this.outputChannel.appendLine('\n❌ Validation Errors:');
            result.errors.forEach(error => {
                this.outputChannel.appendLine(`  [${error.path}] ${error.message}`);
            });
        }

        if (result.warnings.length > 0) {
            this.outputChannel.appendLine('\n⚠️ Validation Warnings:');
            result.warnings.forEach(warning => {
                this.outputChannel.appendLine(`  [${warning.path}] ${warning.message}`);
            });
        }

        this.outputChannel.show();
    }

    /**
     * Create VS Code diagnostics from validation result
     */
    private createDiagnostics(result: ValidationResult): vscode.Diagnostic[] {
        const diagnostics: vscode.Diagnostic[] = [];

        [...result.errors, ...result.warnings].forEach(issue => {
            const range = issue.line !== undefined
                ? new vscode.Range(issue.line - 1, issue.column || 0, issue.line - 1, 100)
                : new vscode.Range(0, 0, 0, 100);

            const diagnostic = new vscode.Diagnostic(
                range,
                issue.message,
                issue.severity === 'error' 
                    ? vscode.DiagnosticSeverity.Error 
                    : vscode.DiagnosticSeverity.Warning
            );
            diagnostic.source = 'DSL Schema';
            diagnostics.push(diagnostic);
        });

        return diagnostics;
    }

    /**
     * Select target language for transformation
     */
    private async selectTargetLanguage(): Promise<string | undefined> {
        const languages = [
            { label: 'TypeScript', value: 'typescript' },
            { label: 'JavaScript', value: 'javascript' },
            { label: 'Python', value: 'python' },
            { label: 'Java', value: 'java' },
            { label: 'C++', value: 'cpp' }
        ];

        const selected = await vscode.window.showQuickPick(
            languages.map(l => ({
                label: l.label,
                description: `Generate ${l.label} code`,
                value: l.value
            })),
            { placeHolder: 'Select target language' }
        );

        return selected?.value;
    }

    /**
     * Select output location for transformed file
     */
    private async selectOutputLocation(
        inputUri: vscode.Uri,
        targetLanguage: string
    ): Promise<vscode.Uri | undefined> {
        const ext = this.getFileExtension(targetLanguage);
        const defaultName = path.basename(inputUri.fsPath, path.extname(inputUri.fsPath)) + `.${ext}`;

        const saveUri = await vscode.window.showSaveDialog({
            defaultUri: vscode.Uri.file(path.join(path.dirname(inputUri.fsPath), defaultName)),
            filters: {
                'Generated Code': [ext],
                'All Files': ['*']
            }
        });

        return saveUri;
    }

    /**
     * Transform schema to target language
     */
    private async transformSchema(
        schema: unknown,
        targetLanguage: string
    ): Promise<TransformResult> {
        try {
            const schemaObj = schema as Record<string, unknown>;
            
            // Generate code based on target language
            let output = '';
            
            switch (targetLanguage) {
                case 'typescript':
                    output = this.generateTypeScript(schemaObj);
                    break;
                case 'javascript':
                    output = this.generateJavaScript(schemaObj);
                    break;
                case 'python':
                    output = this.generatePython(schemaObj);
                    break;
                case 'java':
                    output = this.generateJava(schemaObj);
                    break;
                case 'cpp':
                    output = this.generateCpp(schemaObj);
                    break;
                default:
                    throw new Error(`Unsupported target language: ${targetLanguage}`);
            }

            return {
                success: true,
                output
            };
        } catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : String(error)
            };
        }
    }

    /**
     * Generate TypeScript code from schema
     */
    private generateTypeScript(schema: Record<string, unknown>): string {
        const name = (schema.name as string) || 'Generated';
        const className = this.toPascalCase(name);
        
        let code = `// Generated from DSL Schema: ${name}\n`;
        code += `// Generated at: ${new Date().toISOString()}\n\n`;
        code += `/**\n`;
        code += ` * ${schema.description || `${className} class generated from schema`}\n`;
        code += ` */\n`;
        code += `export class ${className} {\n`;
        code += `    private metadata: Record<string, unknown>;\n\n`;
        
        // Generate properties from nodes
        const nodes = schema.nodes as Array<Record<string, unknown>> || [];
        nodes.forEach((node: Record<string, unknown>) => {
            const nodeName = (node.name as string) || 'unnamed';
            const nodeType = (node.type as string) || 'any';
            code += `    public ${nodeName}: ${this.mapToTypeScriptType(nodeType)};\n`;
        });
        
        code += `\n    constructor() {\n`;
        code += `        this.metadata = ${JSON.stringify(schema.metadata || {})};\n`;
        nodes.forEach((node: Record<string, unknown>) => {
            const nodeName = (node.name as string) || 'unnamed';
            code += `        this.${nodeName} = ${this.getDefaultValue(node.type as string)};\n`;
        });
        code += `    }\n`;
        code += `}\n`;

        return code;
    }

    /**
     * Generate JavaScript code from schema
     */
    private generateJavaScript(schema: Record<string, unknown>): string {
        const name = (schema.name as string) || 'Generated';
        const className = this.toPascalCase(name);
        
        let code = `// Generated from DSL Schema: ${name}\n`;
        code += `// Generated at: ${new Date().toISOString()}\n\n`;
        code += `/**\n`;
        code += ` * ${schema.description || `${className} class generated from schema`}\n`;
        code += ` */\n`;
        code += `class ${className} {\n`;
        code += `    constructor() {\n`;
        code += `        this.metadata = ${JSON.stringify(schema.metadata || {}, null, 8)};\n`;
        
        const nodes = schema.nodes as Array<Record<string, unknown>> || [];
        nodes.forEach((node: Record<string, unknown>) => {
            const nodeName = (node.name as string) || 'unnamed';
            code += `        this.${nodeName} = ${this.getDefaultValue(node.type as string)};\n`;
        });
        
        code += `    }\n`;
        code += `}\n\n`;
        code += `module.exports = { ${className} };\n`;

        return code;
    }

    /**
     * Generate Python code from schema
     */
    private generatePython(schema: Record<string, unknown>): string {
        const name = (schema.name as string) || 'generated';
        const className = this.toPascalCase(name);
        
        let code = `# Generated from DSL Schema: ${name}\n`;
        code += `# Generated at: ${new Date().toISOString()}\n\n`;
        code += `class ${className}:\n`;
        code += `    """${schema.description || `${className} class generated from schema`}"""\n\n`;
        code += `    def __init__(self):\n`;
        code += `        self.metadata = ${JSON.stringify(schema.metadata || {})}\n`;
        
        const nodes = schema.nodes as Array<Record<string, unknown>> || [];
        nodes.forEach((node: Record<string, unknown>) => {
            const nodeName = (node.name as string) || 'unnamed';
            code += `        self.${nodeName} = ${this.getPythonDefaultValue(node.type as string)}\n`;
        });

        return code;
    }

    /**
     * Generate Java code from schema
     */
    private generateJava(schema: Record<string, unknown>): string {
        const name = (schema.name as string) || 'Generated';
        const className = this.toPascalCase(name);
        
        let code = `// Generated from DSL Schema: ${name}\n`;
        code += `// Generated at: ${new Date().toISOString()}\n\n`;
        code += `import java.util.Map;\n`;
        code += `import java.util.HashMap;\n\n`;
        code += `/**\n`;
        code += ` * ${schema.description || `${className} class generated from schema`}\n`;
        code += ` */\n`;
        code += `public class ${className} {\n`;
        code += `    private Map<String, Object> metadata;\n`;
        
        const nodes = schema.nodes as Array<Record<string, unknown>> || [];
        nodes.forEach((node: Record<string, unknown>) => {
            const nodeName = (node.name as string) || 'unnamed';
            const nodeType = (node.type as string) || 'Object';
            code += `    private ${this.mapToJavaType(nodeType)} ${nodeName};\n`;
        });
        
        code += `\n    public ${className}() {\n`;
        code += `        this.metadata = new HashMap<>();\n`;
        nodes.forEach((node: Record<string, unknown>) => {
            const nodeName = (node.name as string) || 'unnamed';
            code += `        this.${nodeName} = ${this.getJavaDefaultValue(node.type as string)};\n`;
        });
        code += `    }\n`;
        code += `}\n`;

        return code;
    }

    /**
     * Generate C++ code from schema
     */
    private generateCpp(schema: Record<string, unknown>): string {
        const name = (schema.name as string) || 'generated';
        const className = this.toPascalCase(name);
        
        let code = `// Generated from DSL Schema: ${name}\n`;
        code += `// Generated at: ${new Date().toISOString()}\n\n`;
        code += `#include <string>\n`;
        code += `#include <map>\n\n`;
        code += `/**\n`;
        code += ` * ${schema.description || `${className} class generated from schema`}\n`;
        code += ` */\n`;
        code += `class ${className} {\n`;
        code += `private:\n`;
        code += `    std::map<std::string, std::string> metadata;\n`;
        
        const nodes = schema.nodes as Array<Record<string, unknown>> || [];
        nodes.forEach((node: Record<string, unknown>) => {
            const nodeName = (node.name as string) || 'unnamed';
            const nodeType = (node.type as string) || 'string';
            code += `    ${this.mapToCppType(nodeType)} ${nodeName};\n`;
        });
        
        code += `\npublic:\n`;
        code += `    ${className}() {\n`;
        nodes.forEach((node: Record<string, unknown>) => {
            const nodeName = (node.name as string) || 'unnamed';
            code += `        ${nodeName} = ${this.getCppDefaultValue(node.type as string)};\n`;
        });
        code += `    }\n`;
        code += `};\n`;

        return code;
    }

    /**
     * Write output file
     */
    private async writeOutputFile(uri: vscode.Uri, content: string): Promise<void> {
        const encoder = new TextEncoder();
        await vscode.workspace.fs.writeFile(uri, encoder.encode(content));
    }

    /**
     * Get file extension for target language
     */
    private getFileExtension(language: string): string {
        const extensions: Record<string, string> = {
            'typescript': 'ts',
            'javascript': 'js',
            'python': 'py',
            'java': 'java',
            'cpp': 'cpp'
        };
        return extensions[language] || 'txt';
    }

    /**
     * Convert string to PascalCase
     */
    private toPascalCase(str: string): string {
        return str
            .replace(/(?:^|[-_])(\w)/g, (_, c) => c ? c.toUpperCase() : '')
            .replace(/[^a-zA-Z0-9]/g, '');
    }

    /**
     * Map DSL type to TypeScript type
     */
    private mapToTypeScriptType(type: string): string {
        const typeMap: Record<string, string> = {
            'string': 'string',
            'number': 'number',
            'boolean': 'boolean',
            'array': 'any[]',
            'object': 'Record<string, unknown>',
            'any': 'any'
        };
        return typeMap[type] || 'any';
    }

    /**
     * Map DSL type to Java type
     */
    private mapToJavaType(type: string): string {
        const typeMap: Record<string, string> = {
            'string': 'String',
            'number': 'Double',
            'boolean': 'Boolean',
            'array': 'List<Object>',
            'object': 'Map<String, Object>',
            'any': 'Object'
        };
        return typeMap[type] || 'Object';
    }

    /**
     * Map DSL type to C++ type
     */
    private mapToCppType(type: string): string {
        const typeMap: Record<string, string> = {
            'string': 'std::string',
            'number': 'double',
            'boolean': 'bool',
            'array': 'std::vector<std::string>',
            'object': 'std::map<std::string, std::string>',
            'any': 'std::string'
        };
        return typeMap[type] || 'std::string';
    }

    /**
     * Get default value for a type
     */
    private getDefaultValue(type: string): string {
        const defaults: Record<string, string> = {
            'string': '""',
            'number': '0',
            'boolean': 'false',
            'array': '[]',
            'object': '{}',
            'any': 'null'
        };
        return defaults[type] || 'null';
    }

    /**
     * Get Python default value for a type
     */
    private getPythonDefaultValue(type: string): string {
        const defaults: Record<string, string> = {
            'string': '""',
            'number': '0',
            'boolean': 'False',
            'array': '[]',
            'object': '{}',
            'any': 'None'
        };
        return defaults[type] || 'None';
    }

    /**
     * Get Java default value for a type
     */
    private getJavaDefaultValue(type: string): string {
        const defaults: Record<string, string> = {
            'string': '""',
            'number': '0.0',
            'boolean': 'false',
            'array': 'new ArrayList<>()',
            'object': 'new HashMap<>()',
            'any': 'null'
        };
        return defaults[type] || 'null';
    }

    /**
     * Get C++ default value for a type
     */
    private getCppDefaultValue(type: string): string {
        const defaults: Record<string, string> = {
            'string': '""',
            'number': '0.0',
            'boolean': 'false',
            'array': '{}',
            'object': '{}',
            'any': '""'
        };
        return defaults[type] || '""';
    }
}

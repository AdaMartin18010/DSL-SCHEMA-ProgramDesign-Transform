/**
 * extension.ts
 * 
 * DSL Schema Transform - VS Code Extension Main Entry Point
 * 
 * This file serves as the main entry point for the VS Code extension.
 * It handles extension activation, deactivation, and coordinates between
 * different modules like the schema editor and transform commands.
 * 
 * @module extension
 * @author DSL Schema Team
 * @version 0.1.0
 */

import * as vscode from 'vscode';
import { SchemaEditorProvider } from './schemaEditor';
import { TransformCommands } from './transformCommands';

/**
 * Extension context - stores references to disposables and global state
 */
let extensionContext: vscode.ExtensionContext;

/**
 * Output channel for logging extension activities
 */
let outputChannel: vscode.OutputChannel;

/**
 * Status bar item for showing extension status
 */
let statusBarItem: vscode.StatusBarItem;

/**
 * Schema editor provider instance
 */
let schemaEditorProvider: SchemaEditorProvider;

/**
 * Transform commands handler instance
 */
let transformCommands: TransformCommands;

/**
 * Extension activation entry point
 * 
 * This function is called when the extension is activated.
 * It initializes all components, registers commands, and sets up event listeners.
 * 
 * @param context - The extension context provided by VS Code
 */
export function activate(context: vscode.ExtensionContext): void {
    // Store the extension context for global access
    extensionContext = context;

    // Initialize output channel for logging
    outputChannel = vscode.window.createOutputChannel('DSL Schema Transform');
    outputChannel.appendLine('DSL Schema Transform extension is activating...');

    // Initialize status bar item
    initializeStatusBar();

    // Initialize module instances
    schemaEditorProvider = new SchemaEditorProvider(context, outputChannel);
    transformCommands = new TransformCommands(context, outputChannel);

    // Register all extension components
    registerCommands(context);
    registerEventListeners(context);
    registerProviders(context);

    // Show welcome message
    showWelcomeMessage();

    // Update status bar
    updateStatusBar('DSL Schema Transform: Ready', 'check');

    outputChannel.appendLine('DSL Schema Transform extension activated successfully!');
}

/**
 * Extension deactivation cleanup
 * 
 * This function is called when the extension is deactivated.
 * It performs cleanup operations like disposing resources.
 */
export function deactivate(): void {
    outputChannel?.appendLine('DSL Schema Transform extension is deactivating...');

    // Dispose of the status bar item
    statusBarItem?.dispose();

    // Clean up module instances
    schemaEditorProvider?.dispose();
    transformCommands?.dispose();

    outputChannel?.appendLine('DSL Schema Transform extension deactivated.');
}

/**
 * Initialize the status bar item
 */
function initializeStatusBar(): void {
    statusBarItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Right,
        100
    );
    statusBarItem.command = 'dslSchemaTransform.openSchemaEditor';
    statusBarItem.tooltip = 'Click to open DSL Schema Editor';
    statusBarItem.show();
}

/**
 * Update the status bar with a message and icon
 * 
 * @param message - The message to display
 * @param icon - The icon to show (VS Code icon name)
 */
function updateStatusBar(message: string, icon: string): void {
    if (statusBarItem) {
        statusBarItem.text = `$(${icon}) ${message}`;
    }
}

/**
 * Register all extension commands
 * 
 * @param context - The extension context
 */
function registerCommands(context: vscode.ExtensionContext): void {
    const disposables: vscode.Disposable[] = [
        // Command: Open Schema Editor
        vscode.commands.registerCommand(
            'dslSchemaTransform.openSchemaEditor',
            async (uri?: vscode.Uri) => {
                try {
                    updateStatusBar('Opening Schema Editor...', 'loading~spin');
                    await schemaEditorProvider.openEditor(uri);
                    updateStatusBar('Schema Editor Opened', 'edit');
                } catch (error) {
                    handleError('Failed to open schema editor', error);
                }
            }
        ),

        // Command: Transform Program
        vscode.commands.registerCommand(
            'dslSchemaTransform.transformProgram',
            async (uri?: vscode.Uri) => {
                try {
                    updateStatusBar('Transforming...', 'loading~spin');
                    await transformCommands.executeTransform(uri);
                    updateStatusBar('Transform Complete', 'check');
                } catch (error) {
                    handleError('Transformation failed', error);
                }
            }
        ),

        // Command: Validate Schema
        vscode.commands.registerCommand(
            'dslSchemaTransform.validateSchema',
            async (uri?: vscode.Uri) => {
                try {
                    updateStatusBar('Validating...', 'loading~spin');
                    await transformCommands.validateSchema(uri);
                    updateStatusBar('Validation Complete', 'check');
                } catch (error) {
                    handleError('Validation failed', error);
                }
            }
        ),

        // Command: Preview Transformation
        vscode.commands.registerCommand(
            'dslSchemaTransform.previewTransformation',
            async (uri?: vscode.Uri) => {
                try {
                    updateStatusBar('Generating Preview...', 'loading~spin');
                    await transformCommands.previewTransformation(uri);
                    updateStatusBar('Preview Ready', 'preview');
                } catch (error) {
                    handleError('Preview generation failed', error);
                }
            }
        ),

        // Command: Generate Code
        vscode.commands.registerCommand(
            'dslSchemaTransform.generateCode',
            async (uri?: vscode.Uri) => {
                try {
                    updateStatusBar('Generating Code...', 'loading~spin');
                    await transformCommands.generateCode(uri);
                    updateStatusBar('Code Generated', 'code');
                } catch (error) {
                    handleError('Code generation failed', error);
                }
            }
        ),

        // Command: Show Extension Info
        vscode.commands.registerCommand(
            'dslSchemaTransform.showInfo',
            () => {
                vscode.window.showInformationMessage(
                    'DSL Schema Transform v0.1.0 - Use Ctrl+Shift+E to open the schema editor',
                    'OK'
                );
            }
        )
    ];

    // Add all disposables to extension context
    disposables.forEach(disposable => context.subscriptions.push(disposable));
}

/**
 * Register event listeners for file operations and editor events
 * 
 * @param context - The extension context
 */
function registerEventListeners(context: vscode.ExtensionContext): void {
    // Listen for configuration changes
    const configChangeDisposable = vscode.workspace.onDidChangeConfiguration(
        (event) => {
            if (event.affectsConfiguration('dslSchemaTransform')) {
                outputChannel.appendLine('Configuration changed, reloading settings...');
                // Reload settings in modules
                schemaEditorProvider.reloadSettings();
                transformCommands.reloadSettings();
            }
        }
    );

    // Listen for file save events to trigger validation
    const saveDisposable = vscode.workspace.onDidSaveTextDocument(
        async (document) => {
            const config = vscode.workspace.getConfiguration('dslSchemaTransform');
            const validationEnabled = config.get<boolean>('schemaValidation.enabled', true);

            if (validationEnabled && isSchemaFile(document)) {
                outputChannel.appendLine(`Auto-validating: ${document.fileName}`);
                await transformCommands.validateSchema(document.uri);
            }
        }
    );

    // Listen for active editor changes
    const editorChangeDisposable = vscode.window.onDidChangeActiveTextEditor(
        (editor) => {
            if (editor && isSchemaFile(editor.document)) {
                updateStatusBar('DSL Schema File Active', 'file');
            } else {
                updateStatusBar('DSL Schema Transform: Ready', 'check');
            }
        }
    );

    // Add disposables to context
    context.subscriptions.push(
        configChangeDisposable,
        saveDisposable,
        editorChangeDisposable
    );
}

/**
 * Register file system providers and other VS Code providers
 * 
 * @param context - The extension context
 */
function registerProviders(context: vscode.ExtensionContext): void {
    // Register custom text document content provider for previews
    const previewProvider = vscode.workspace.registerTextDocumentContentProvider(
        'dsl-schema-preview',
        {
            provideTextDocumentContent(uri: vscode.Uri): string {
                return transformCommands.getPreviewContent(uri);
            }
        }
    );

    context.subscriptions.push(previewProvider);
}

/**
 * Check if a document is a schema file
 * 
 * @param document - The text document to check
 * @returns True if the document is a schema file
 */
function isSchemaFile(document: vscode.TextDocument): boolean {
    const schemaExtensions = ['.dsl', '.schema', '.json'];
    const fileName = document.fileName.toLowerCase();
    return schemaExtensions.some(ext => fileName.endsWith(ext));
}

/**
 * Handle errors consistently across the extension
 * 
 * @param message - The error message prefix
 * @param error - The error object
 */
function handleError(message: string, error: unknown): void {
    const errorMessage = error instanceof Error ? error.message : String(error);
    const fullMessage = `${message}: ${errorMessage}`;

    // Log to output channel
    outputChannel.appendLine(`[ERROR] ${fullMessage}`);

    // Show error message to user
    vscode.window.showErrorMessage(fullMessage, 'Show Output').then((selection) => {
        if (selection === 'Show Output') {
            outputChannel.show();
        }
    });

    // Update status bar
    updateStatusBar('Error occurred', 'error');
}

/**
 * Show welcome message on first activation
 */
function showWelcomeMessage(): void {
    const hasShownWelcome = extensionContext.globalState.get<boolean>(
        'dslSchemaTransform.welcomeShown',
        false
    );

    if (!hasShownWelcome) {
        vscode.window.showInformationMessage(
            'Welcome to DSL Schema Transform! Use Ctrl+Shift+E to open the schema editor.',
            'Open Settings',
            'View Documentation'
        ).then((selection) => {
            if (selection === 'Open Settings') {
                vscode.commands.executeCommand(
                    'workbench.action.openSettings',
                    'dslSchemaTransform'
                );
            } else if (selection === 'View Documentation') {
                vscode.env.openExternal(
                    vscode.Uri.parse('https://github.com/your-org/dsl-schema-transform#readme')
                );
            }
        });

        // Mark welcome as shown
        extensionContext.globalState.update('dslSchemaTransform.welcomeShown', true);
    }
}

/**
 * Get the extension output channel
 * @returns The output channel instance
 */
export function getOutputChannel(): vscode.OutputChannel {
    return outputChannel;
}

/**
 * Get the extension context
 * @returns The extension context
 */
export function getExtensionContext(): vscode.ExtensionContext {
    return extensionContext;
}

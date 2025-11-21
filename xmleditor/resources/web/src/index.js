/**
 * Monaco Editor + Y.js Bundle Entry Point
 * This file bundles all JavaScript dependencies for the XML editor
 */

// Import Monaco Editor
import * as monaco from 'monaco-editor';

// Import Y.js for CRDT synchronization
import * as Y from 'yjs';
import { WebsocketProvider } from 'y-websocket';
import { MonacoBinding } from 'y-monaco';

// Export to window for Python integration
window.monaco = monaco;
window.Y = Y;
window.WebsocketProvider = WebsocketProvider;
window.MonacoBinding = MonacoBinding;

// Mark bundle as loaded
window.monacoBundleLoaded = true;

console.log('[Bundle] Monaco Editor and Y.js loaded successfully');

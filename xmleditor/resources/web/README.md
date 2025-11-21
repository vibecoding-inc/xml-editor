# Monaco Editor Web Bundle

This directory contains the webpack configuration for bundling Monaco Editor and Y.js dependencies.

## Building

```bash
npm install
npm run build
```

This creates a `dist/` folder with:
- `bundle.js` - Main bundle containing Monaco Editor, Y.js, y-websocket, and y-monaco
- Worker files for Monaco (css.worker.js, html.worker.js, json.worker.js, etc.)
- Font files and other assets

## Integration

The built bundle is:
1. Copied to `../dist/` by the `compile_resources.py` script
2. Loaded from the local filesystem in `monaco_editor_bundled.html`
3. Exposed to Python via the `window` object

## Nix Build

The Nix flake builds this bundle automatically using `buildNpmPackage` and copies it into the Python package resources during the build phase.

##Dependencies

- **monaco-editor** (0.45.0) - Code editor
- **yjs** (13.6.10) - CRDT for synchronization
- **y-websocket** (1.5.0) - WebSocket provider for Y.js
- **y-monaco** (0.1.6) - Monaco binding for Y.js
- **webpack** + plugins - Build toolchain

## Development

For development with hot reload:
```bash
npm run build:dev
```

## File Size

The production build is approximately 6.7MB total:
- bundle.js: 3.35 MB (main bundle)
- css.worker.js: 990 KB
- html.worker.js: 661 KB  
- json.worker.js: 359 KB
- Additional workers and assets: ~1.4 MB

These files are NOT committed to git (see `.gitignore`) but are built during the Nix build process or manually for development.

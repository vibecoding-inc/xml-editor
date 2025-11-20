# Multiplayer Collaborative Editing

The XML Editor now supports real-time collaborative editing, allowing multiple users to work on the same XML document simultaneously.

## Overview

Multiplayer editing is powered by:
- **Monaco Editor**: A modern web-based code editor
- **Y.js (Yjs)**: Conflict-free Replicated Data Type (CRDT) library for synchronization
- **Cloudflare Workers**: WebSocket relay service for message passing

## Features

- **Real-time synchronization**: Changes appear instantly for all connected users
- **Conflict resolution**: Y.js automatically resolves concurrent edits
- **Easy session management**: Host or join sessions with simple dialogs
- **No data loss**: CRDT ensures all changes are preserved

## Getting Started

### 1. Deploy the Cloudflare Worker

Before using collaborative features, you need to deploy the WebSocket relay worker:

1. **Install Wrangler CLI**:
   ```bash
   npm install -g wrangler
   ```

2. **Authenticate with Cloudflare**:
   ```bash
   wrangler login
   ```

3. **Deploy the worker**:
   ```bash
   cd cloudflare-worker
   wrangler deploy
   ```

4. **Note your worker URL** (e.g., `https://xml-editor-collab.your-subdomain.workers.dev`)

See `cloudflare-worker/README.md` for detailed deployment instructions.

### 2. Using Collaborative Editing

#### Hosting a Session

1. Open a document in XML Editor
2. Go to **Collaboration → Host Session...**
3. Enter your Cloudflare Worker URL (with `wss://` instead of `https://`)
4. Enter a room name (or use the auto-generated one)
5. Click **Host Session**
6. Share the room name with collaborators

#### Joining a Session

1. Open XML Editor (save any unsaved work first!)
2. Go to **Collaboration → Join Session...**
3. Enter the server URL provided by the host
4. Enter the room name provided by the host
5. Click **Join Session**
6. Your document will be synchronized with the shared session

#### Disconnecting

- Go to **Collaboration → Disconnect** to leave the session
- Your local copy remains, but changes won't sync anymore

## Editor Modes

The XML Editor supports two editor modes:

### Monaco Editor (Default)
- Modern web-based editor
- Supports collaborative editing
- Runs in QWebEngineView
- Slightly different keyboard shortcuts

### QScintilla Editor (Legacy)
- Traditional desktop editor
- Does NOT support collaboration
- Native Qt widget
- Existing keyboard shortcuts

You can switch between editors by changing the `use_monaco_editor` setting.

## How It Works

### Architecture

```
┌─────────────┐       WebSocket        ┌─────────────────┐       WebSocket        ┌─────────────┐
│  Client A   │◄──────────────────────►│ Cloudflare      │◄──────────────────────►│  Client B   │
│ (XML Editor)│                         │ Worker          │                         │ (XML Editor)│
└─────────────┘                         │ (Message Broker)│                         └─────────────┘
     ▲ │                                └─────────────────┘                              ▲ │
     │ │                                                                                  │ │
     │ └─ Y.js updates ───────────────────────────────────────────────── Y.js updates ───┘ │
     │                                                                                      │
     └────────────────────────────── CRDT Synchronization ─────────────────────────────────┘
```

### Synchronization Process

1. **User makes an edit** in Monaco editor
2. **Y.js captures the change** as a CRDT operation
3. **Change is sent** via WebSocket to Cloudflare Worker
4. **Worker broadcasts** the change to all other clients in the room
5. **Other clients receive** the change and apply it via Y.js
6. **Documents stay in sync** without conflicts

### Conflict Resolution

Y.js uses CRDTs which means:
- **No locks needed**: Multiple users can edit simultaneously
- **Automatic merging**: Conflicts are resolved deterministically
- **No lost updates**: All changes are preserved
- **Eventual consistency**: All clients converge to the same state

## Room Management

### Room Names

- Rooms are identified by name (e.g., "my-project-file")
- Anyone with the room name can join
- Rooms are created on-demand when first client connects
- No authentication by default (see Security Considerations)

### Persistence

⚠️ **Important**: The basic worker implementation does NOT persist data.
- Messages are only relayed, not stored
- If all clients disconnect, the document state is lost
- Always save your work locally using File → Save

## Security Considerations

The default implementation has **no authentication or authorization**:
- Anyone with the room name can join and edit
- No encryption beyond WebSocket TLS
- No user identity tracking

For production use, consider:
- Adding authentication (API keys, OAuth, etc.)
- Implementing per-room passwords
- Using Cloudflare Access for enterprise SSO
- Rate limiting by IP address
- Logging and audit trails

## Keyboard Shortcuts

When using Monaco editor:
- **Host Session**: `Ctrl+Shift+H`
- **Join Session**: `Ctrl+Shift+J`
- **Disconnect**: `Ctrl+Shift+D`

## Troubleshooting

### "Connection Failed" Error

**Causes**:
- Worker not deployed or URL incorrect
- Firewall blocking WebSocket connections
- Using `ws://` instead of `wss://`

**Solutions**:
- Verify worker deployment: `wrangler deployments list`
- Check URL format: must start with `wss://`
- Test WebSocket from browser console
- Check firewall/proxy settings

### "Changes Not Syncing"

**Causes**:
- Network interruption
- WebSocket connection dropped
- Durable Objects not enabled

**Solutions**:
- Check connection status in status bar
- Disconnect and reconnect
- Verify Durable Objects enabled in Cloudflare dashboard
- Check browser console for errors

### "Room Already In Use"

This is normal - you're joining an existing session. The document will sync with other users.

## Cost Considerations

Cloudflare offers generous free tiers:
- **Workers**: 100,000 requests/day
- **Durable Objects**: 1 million requests/month
- **WebSocket**: Included in Durable Objects

For small teams and occasional use, the free tier is usually sufficient.

For heavy usage:
- ~$5/month for 10 million requests
- ~$0.15 per GB of WebSocket data

## Advanced Usage

### Custom Worker Domain

To use your own domain:

1. Add domain in Cloudflare dashboard
2. Update wrangler.toml:
   ```toml
   route = "collab.yourdomain.com/*"
   ```
3. Redeploy with `wrangler deploy`

### Production Enhancements

For production deployments, consider:

1. **Using y-durable-objects library**:
   ```bash
   npm install y-durable-objects
   ```
   Provides built-in Y.js protocol handling

2. **Adding authentication**:
   - JWT tokens in WebSocket handshake
   - Cloudflare Access integration
   - Custom authentication logic

3. **Message persistence**:
   - Store document snapshots in Durable Object storage
   - Periodic backups to R2 storage
   - Event sourcing for full history

4. **Monitoring**:
   - Cloudflare Analytics
   - Custom logging with Workers Analytics Engine
   - Error tracking with Sentry

## Limitations

- **No offline mode**: Requires active internet connection
- **No conflict notification**: Changes merge silently
- **No user cursors**: Can't see where others are typing
- **No presence awareness**: Can't see who's connected
- **Memory-only**: No persistent storage in basic implementation

For enhanced features, consider using a dedicated collaboration backend like Liveblocks, PartyKit, or implementing your own with the y-durable-objects library.

## FAQ

**Q: Can I use this without deploying a worker?**
A: No, a WebSocket relay is required for synchronization.

**Q: Is my data secure?**
A: Data is encrypted in transit (TLS) but stored in memory only. The basic implementation has no authentication. For sensitive data, add your own auth layer.

**Q: How many users can collaborate simultaneously?**
A: Cloudflare Durable Objects can handle hundreds of connections per room. Practical limit depends on your usage patterns and Cloudflare plan.

**Q: Can I use this with XML files larger than 1MB?**
A: Yes, but large files may have slower initial sync. Y.js is optimized for frequent small changes.

**Q: Does this work across different networks/firewalls?**
A: Usually yes, as it uses standard WebSocket (wss://) which typically works through corporate firewalls. Some restrictive networks may block it.

**Q: Can I see who else is editing?**
A: Not in the basic implementation. This would require adding presence awareness features.

## Related Documentation

- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)
- [Durable Objects Guide](https://developers.cloudflare.com/workers/learning/using-durable-objects/)
- [Y.js Documentation](https://docs.yjs.dev/)
- [Monaco Editor API](https://microsoft.github.io/monaco-editor/)

## Future Enhancements

Potential future improvements:
- User presence indicators (colored cursors)
- User list showing who's connected
- Chat/comments feature
- Version history with snapshots
- Permissions (read-only vs read-write)
- Document templates for common XML types
- Integration with Git for persistence

# XML Editor Collaboration Worker

This Cloudflare Worker acts as a WebSocket relay/message broker for real-time collaborative editing in the XML Editor.

## Overview

The worker uses Cloudflare Durable Objects to create isolated rooms for document collaboration. Each room maintains WebSocket connections for all connected clients and relays Y.js CRDT synchronization messages between them.

## Architecture

- **Main Worker**: Routes incoming WebSocket requests to the appropriate DocumentRoom
- **DocumentRoom Durable Object**: Manages WebSocket connections for a specific room and broadcasts messages

## Deployment

### Prerequisites

1. A Cloudflare account (free tier works fine)
2. Wrangler CLI installed: `npm install -g wrangler`
3. Authenticated with Cloudflare: `wrangler login`

### Steps

1. Navigate to this directory:
   ```bash
   cd cloudflare-worker
   ```

2. Deploy the worker:
   ```bash
   wrangler deploy
   ```

3. Note the deployed URL (e.g., `https://xml-editor-collab.your-subdomain.workers.dev`)

4. Use this URL in the XML Editor's collaboration dialogs

## Usage

### Room Names

Rooms are identified by the URL path. For example:
- `wss://your-worker.workers.dev/my-document` → Room: "my-document"
- `wss://your-worker.workers.dev/project/file` → Room: "project/file"

### Testing

You can test the WebSocket connection using a WebSocket client:

```javascript
const ws = new WebSocket('wss://your-worker.workers.dev/test-room');

ws.onopen = () => {
  console.log('Connected');
  ws.send('Hello from client 1');
};

ws.onmessage = (event) => {
  console.log('Received:', event.data);
};
```

## How It Works

1. Client connects via WebSocket to a specific room URL
2. Worker creates/retrieves a Durable Object for that room
3. Durable Object accepts the WebSocket and adds it to the room's session list
4. When a client sends a message (Y.js sync data), the Durable Object broadcasts it to all other connected clients
5. Y.js on each client uses these messages to synchronize document state

## Limitations

- This is a basic relay implementation
- No message persistence (messages are only relayed, not stored)
- No authentication (anyone with the room name can join)
- For production use, consider adding:
  - Authentication/authorization
  - Message validation
  - Rate limiting
  - Logging and monitoring

## Advanced: Using y-durable-objects

For a more robust implementation, you can use the `y-durable-objects` library which provides built-in Y.js integration:

```bash
npm install y-durable-objects
```

Then modify `src/index.js` to use the library's implementation instead of the basic relay.

## Cost

Cloudflare Workers and Durable Objects have generous free tiers:
- Workers: 100,000 requests/day
- Durable Objects: 1 million requests/month

For typical use (small teams, occasional collaboration), the free tier should be sufficient.

## Troubleshooting

### Connection Fails

- Check that your worker is deployed: `wrangler deployments list`
- Verify WebSocket support is enabled in your Cloudflare dashboard
- Ensure the URL scheme is `wss://` (not `ws://` or `https://`)

### Messages Not Relaying

- Check browser console for WebSocket errors
- Verify Durable Objects are enabled for your account
- Check Cloudflare dashboard logs for errors

## Security Notes

⚠️ **This implementation has no authentication.** Anyone with the room name can join and edit.

For production use, consider:
- Adding API key authentication
- Implementing per-room passwords
- Using Cloudflare Access for authentication
- Rate limiting connections per IP

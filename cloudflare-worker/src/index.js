/**
 * Cloudflare Worker for XML Editor Collaboration
 * 
 * This worker acts as a WebSocket relay/message broker for real-time
 * collaborative editing using Y.js CRDT synchronization.
 */

import { DurableObject } from "cloudflare:workers";

/**
 * DocumentRoom Durable Object
 * 
 * Each room represents a shared document session.
 * Multiple clients can connect to the same room to collaboratively edit.
 */
export class DocumentRoom extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.ctx = ctx;
    this.storage = ctx.storage;
    this.sessions = new Set();
  }

  /**
   * Handle incoming requests (WebSocket upgrades)
   */
  async fetch(request) {
    // Only accept WebSocket upgrade requests
    if (request.headers.get("Upgrade") !== "websocket") {
      return new Response("Expected WebSocket", { status: 426 });
    }

    // Create a WebSocket pair
    const pair = new WebSocketPair();
    const [client, server] = Object.values(pair);
    
    // Accept the WebSocket connection
    this.ctx.acceptWebSocket(server);
    this.sessions.add(server);

    // Set up event handlers for this WebSocket
    server.addEventListener('message', async (event) => {
      // Broadcast the message to all other clients in the room
      // This is a simple relay - Y.js handles the actual CRDT logic
      this.broadcast(event.data, server);
    });

    server.addEventListener('close', () => {
      // Remove the session when client disconnects
      this.sessions.delete(server);
    });

    server.addEventListener('error', (event) => {
      console.error('WebSocket error:', event);
      this.sessions.delete(server);
    });

    // Return the client side of the WebSocket pair
    return new Response(null, {
      status: 101,
      webSocket: client,
    });
  }

  /**
   * Broadcast a message to all connected clients except the sender
   */
  broadcast(message, sender) {
    this.sessions.forEach(session => {
      if (session !== sender && session.readyState === 1) {
        try {
          session.send(message);
        } catch (error) {
          console.error('Failed to send message:', error);
          // Remove dead connections
          this.sessions.delete(session);
        }
      }
    });
  }

  /**
   * Handle WebSocket close event
   */
  async webSocketClose(ws, code, reason, wasClean) {
    this.sessions.delete(ws);
  }

  /**
   * Handle WebSocket error event
   */
  async webSocketError(ws, error) {
    console.error('WebSocket error in room:', error);
    this.sessions.delete(ws);
  }
}

/**
 * Main Worker
 * 
 * Routes incoming requests to the appropriate DocumentRoom
 */
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    // Handle CORS preflight requests
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Upgrade',
        },
      });
    }

    // Extract room name from URL path
    // Example: wss://worker.dev/room-name or wss://worker.dev/path/to/room
    const roomName = url.pathname.slice(1) || 'default-room';
    
    // Get or create a Durable Object instance for this room
    const id = env.DOC_ROOM.idFromName(roomName);
    const stub = env.DOC_ROOM.get(id);
    
    // Forward the request to the Durable Object
    return stub.fetch(request);
  },
};

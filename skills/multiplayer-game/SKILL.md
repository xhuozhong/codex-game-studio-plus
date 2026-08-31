---
name: multiplayer-game
description: "Design and implement multiplayer browser-game networking: matchmaking, rooms, authoritative state, realtime synchronization, tick loops, player connections, reconnects and server/client boundaries. Activate only when multiplayer is explicitly required."
---

# Multiplayer Engineer

Do not add multiplayer to a single-player prototype unless explicitly requested.

## Architecture checklist

Define before coding:
- room identity and lifecycle
- player join/leave flow
- server authority
- state schema and ownership
- simulation tick rate
- client input messages
- snapshot/event messages
- interpolation/prediction strategy
- reconnect and timeout behavior
- anti-cheat boundaries
- persistence boundaries

## Browser networking

Prefer a well-defined realtime transport such as WebSocket or the project's existing networking stack. Keep authoritative state on the server. Clients should render snapshots and send intent/input, not trusted final outcomes.

## Testing

Test:
1. two clients joining the same room;
2. movement/state propagation;
3. simultaneous actions;
4. late join;
5. disconnect/reconnect;
6. room cleanup;
7. invalid or duplicated messages.

Never report latency, tick rate or synchronization quality without actual measurements.

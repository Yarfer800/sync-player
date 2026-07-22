import { getInitData } from '../utils/telegram';

export function createRoomSocket(roomId, onMessage, onClose) {
  const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
  const initData = getInitData();
  const url = `${protocol}//${location.host}/api/ws/rooms/${roomId}?init_data=${encodeURIComponent(initData)}`;

  const ws = new WebSocket(url);

  ws.onopen = () => {
    console.log(`[WS] Connected to room ${roomId}`);
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (e) {
      console.error('[WS] Failed to parse message:', e);
    }
  };

  ws.onclose = (event) => {
    console.log(`[WS] Disconnected from room ${roomId}:`, event.code, event.reason);
    if (onClose) onClose(event);
  };

  ws.onerror = (error) => {
    console.error('[WS] Error:', error);
  };

  const send = (action, payload) => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ action, payload }));
    }
  };

  const close = () => {
    ws.close();
  };

  return { ws, send, close };
}

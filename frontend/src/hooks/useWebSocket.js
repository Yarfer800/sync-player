import { useEffect, useRef, useCallback } from 'react';
import { createRoomSocket } from '../api/ws';

export function useWebSocket(roomId, onMessage) {
  const socketRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  useEffect(() => {
    if (!roomId) return;

    const connect = () => {
      const { ws, send, close } = createRoomSocket(
        roomId,
        (data) => {
          if (onMessage) onMessage(data);
        },
        (event) => {
          if (event.code !== 1000) {
            reconnectTimeoutRef.current = setTimeout(connect, 3000);
          }
        }
      );
      socketRef.current = { ws, send, close };
    };

    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [roomId]);

  const sendMessage = useCallback((action, payload) => {
    if (socketRef.current) {
      socketRef.current.send(action, payload);
    }
  }, []);

  return { sendMessage };
}

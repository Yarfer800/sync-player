import { useState, useEffect, useCallback, useRef } from 'react';
import { api } from '../api/client';

export function useMessages(roomId) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const bottomRef = useRef(null);

  const fetchMessages = useCallback(async () => {
    if (!roomId) return;
    try {
      setLoading(true);
      const data = await api(`/rooms/${roomId}/messages`);
      setMessages(data);
    } catch (err) {
      console.error('Failed to fetch messages:', err);
    } finally {
      setLoading(false);
    }
  }, [roomId]);

  useEffect(() => {
    fetchMessages();
  }, [fetchMessages]);

  const addMessage = useCallback((message) => {
    setMessages((prev) => {
      if (prev.some((m) => m.id === message.id)) return prev;
      return [...prev, message];
    });
  }, []);

  const removeMessage = useCallback((messageId) => {
    setMessages((prev) => prev.filter((m) => m.id !== messageId));
  }, []);

  const scrollToBottom = useCallback(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  return { messages, loading, addMessage, removeMessage, scrollToBottom, bottomRef, refetch: fetchMessages };
}

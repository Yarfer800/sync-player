import { useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';

export function usePlayerState(roomId) {
  const [playerState, setPlayerState] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchState = useCallback(async () => {
    if (!roomId) return;
    try {
      const data = await api(`/rooms/${roomId}/player/state`);
      setPlayerState(data);
    } catch (err) {
      console.error('Failed to fetch player state:', err);
    } finally {
      setLoading(false);
    }
  }, [roomId]);

  useEffect(() => {
    fetchState();
  }, [fetchState]);

  const updateDesync = useCallback((desyncData) => {
    setPlayerState((prev) => ({
      ...prev,
      current_timecode: desyncData.room_timecode,
    }));
  }, []);

  return { playerState, setPlayerState, loading, refetch: fetchState, updateDesync };
}

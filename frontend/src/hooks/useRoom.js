import { useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';

export function useRoom(roomId) {
  const [room, setRoom] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchRoom = useCallback(async () => {
    if (!roomId) return;
    try {
      setLoading(true);
      const data = await api(`/rooms/${roomId}`);
      setRoom(data);
      setParticipants(data.participants || []);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [roomId]);

  useEffect(() => {
    fetchRoom();
  }, [fetchRoom]);

  return { room, participants, loading, error, refetch: fetchRoom };
}

export function useRooms() {
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchRooms = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api('/rooms');
      setRooms(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRooms();
  }, [fetchRooms]);

  return { rooms, loading, error, refetch: fetchRooms };
}

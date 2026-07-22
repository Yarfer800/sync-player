import { useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useRoom } from '../hooks/useRoom';
import { useMessages } from '../hooks/useMessages';
import { usePlayerState } from '../hooks/usePlayerState';
import { useWebSocket } from '../hooks/useWebSocket';
import { api } from '../api/client';
import PageShell from '../components/layout/PageShell';
import SectionDivider from '../components/layout/SectionDivider';
import ChatPanel from '../components/room/ChatPanel';
import PlayerPanel from '../components/room/PlayerPanel';
import ParticipantList from '../components/room/ParticipantList';
import InviteButton from '../components/room/InviteButton';
import GhostButton from '../components/ui/GhostButton';
import PillButton from '../components/ui/PillButton';
import Spinner from '../components/ui/Spinner';
import SearchModal from '../components/room/SearchModal';

export default function RoomPage() {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { room, participants, loading: roomLoading } = useRoom(roomId);
  const { messages, loading: msgsLoading, addMessage, removeMessage, bottomRef } = useMessages(roomId);
  const { playerState, setPlayerState, loading: playerLoading, updateDesync, refetch: refetchPlayer } = usePlayerState(roomId);
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  const isOwner = participants.some(
    (p) => p.user_id === user?.user_id && p.role === 'owner'
  );

  const handleWsMessage = useCallback((data) => {
    if (data.type === 'new_message' && data.message) {
      addMessage(data.message);
    } else if (data.type === 'desync_result' && data.payload) {
      updateDesync(data.payload);
    } else if (data.type === 'player_state_updated' && data.payload) {
      if (!isOwner) {
        setPlayerState(data.payload);
      }
    }
  }, [addMessage, updateDesync, isOwner, setPlayerState]);

  const { sendMessage: wsSend } = useWebSocket(roomId, handleWsMessage);

  const handleSendMessage = (text) => {
    wsSend('send_message', { text });
  };

  const handleDeleteMessage = async (messageId) => {
    try {
      await api(`/rooms/${roomId}/messages/${messageId}`, { method: 'DELETE' });
      removeMessage(messageId);
    } catch (err) {
      console.error('Failed to delete message:', err);
    }
  };

  const handleLeave = async () => {
    try {
      await api(`/rooms/${roomId}/leave`, { method: 'POST' });
      navigate('/');
    } catch (err) {
      console.error('Failed to leave room:', err);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Delete this room permanently?')) return;
    try {
      await api(`/rooms/${roomId}`, { method: 'DELETE' });
      navigate('/');
    } catch (err) {
      console.error('Failed to delete room:', err);
    }
  };

  if (roomLoading) {
    return (
      <PageShell>
        <Spinner size={32} />
      </PageShell>
    );
  }

  if (!room) {
    return (
      <PageShell>
        <div className="room-error">
          <p>Room not found.</p>
          <GhostButton onClick={() => navigate('/')}>BACK TO LOBBY</GhostButton>
        </div>
      </PageShell>
    );
  }

  return (
    <PageShell className="room-page">
      <div className="room-page__header">
        <div className="room-page__info">
          <h2 className="room-page__title">{room.title || room.content_title}</h2>
          <span className="room-page__content-title">{room.content_title}</span>
        </div>
      </div>

      <PlayerPanel 
        playerState={playerState} 
        loading={playerLoading} 
        isOwner={isOwner}
        onUpdateState={(newState) => {
          setPlayerState(newState); // Optimistic update
          api(`/rooms/${roomId}/player/state`, { method: 'PUT', body: newState }).catch(e => console.error(e));
        }}
      />
      
      {isOwner && (
        <div style={{ marginTop: '16px', marginBottom: '8px' }}>
          <PillButton onClick={() => setIsSearchOpen(true)}>LOAD VIDEO ↗</PillButton>
        </div>
      )}

      <SectionDivider />

      <div className="room-page__body">
        <div className="room-page__chat">
          <ChatPanel
            messages={messages}
            onSendMessage={handleSendMessage}
            onDeleteMessage={handleDeleteMessage}
            currentUserId={user?.user_id}
            bottomRef={bottomRef}
            loading={msgsLoading}
          />
        </div>
        <div className="room-page__sidebar">
          <ParticipantList participants={participants} />
          <SectionDivider />
          {isOwner && (
            <div className="room-page__owner-actions">
              <InviteButton roomId={parseInt(roomId)} />
              <GhostButton onClick={handleDelete} className="ghost-button--danger">
                DELETE ROOM
              </GhostButton>
            </div>
          )}
          <GhostButton onClick={handleLeave}>LEAVE ROOM</GhostButton>
        </div>
      </div>

      <SearchModal 
        isOpen={isSearchOpen} 
        onClose={() => setIsSearchOpen(false)} 
        roomId={roomId}
        onVideoSelect={refetchPlayer}
      />
    </PageShell>
  );
}

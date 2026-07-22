import { useState } from 'react';
import { useRooms } from '../hooks/useRoom';
import PageShell from '../components/layout/PageShell';
import SectionDivider from '../components/layout/SectionDivider';
import RoomCard from '../components/lobby/RoomCard';
import CreateRoomModal from '../components/lobby/CreateRoomModal';
import JoinByInviteModal from '../components/lobby/JoinByInviteModal';
import StatusBadge from '../components/ui/StatusBadge';
import PillButton from '../components/ui/PillButton';
import GhostButton from '../components/ui/GhostButton';
import Spinner from '../components/ui/Spinner';

export default function LobbyPage() {
  const { rooms, loading, refetch } = useRooms();
  const [showCreate, setShowCreate] = useState(false);
  const [showInvite, setShowInvite] = useState(false);

  return (
    <PageShell>
      <div className="lobby">
        <div className="lobby__header">
          <h1 className="lobby__title">SYNC PLAYER</h1>
          <p className="lobby__subtitle">Watch together, stay in sync.</p>
          <StatusBadge>{rooms.length} {rooms.length === 1 ? 'ROOM' : 'ROOMS'} ACTIVE</StatusBadge>
        </div>

        <SectionDivider />

        <div className="lobby__actions">
          <PillButton onClick={() => setShowCreate(true)}>CREATE ROOM ↗</PillButton>
          <GhostButton onClick={() => setShowInvite(true)}>JOIN BY INVITE</GhostButton>
        </div>

        <SectionDivider />

        {loading ? (
          <Spinner size={32} />
        ) : rooms.length === 0 ? (
          <div className="lobby__empty">
            <p className="lobby__empty-text">No rooms yet. Create one to get started.</p>
          </div>
        ) : (
          <div className="lobby__grid">
            {rooms.map((room, i) => (
              <RoomCard key={room.room_id} room={room} index={i} />
            ))}
          </div>
        )}
      </div>

      <CreateRoomModal
        isOpen={showCreate}
        onClose={() => setShowCreate(false)}
        onCreated={(room) => {
          refetch();
        }}
      />
      <JoinByInviteModal
        isOpen={showInvite}
        onClose={() => setShowInvite(false)}
      />
    </PageShell>
  );
}

import { useState } from 'react';
import Modal from '../ui/Modal';
import Input from '../ui/Input';
import PillButton from '../ui/PillButton';
import { api } from '../../api/client';
import { useNavigate } from 'react-router-dom';

export default function JoinByInviteModal({ isOpen, onClose }) {
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!code.trim()) return;

    try {
      setLoading(true);
      setError(null);
      const room = await api('/rooms/join/invite', {
        method: 'POST',
        body: { invite_code: code.trim() },
      });
      navigate(`/room/${room.room_id}`);
      onClose();
      setCode('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="JOIN BY INVITE">
      <form onSubmit={handleSubmit} className="join-invite-form">
        <Input
          label="INVITE CODE"
          placeholder="Paste invite code"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          required
        />
        {error && <p className="form-error">{error}</p>}
        <PillButton type="submit" disabled={loading}>
          {loading ? 'JOINING...' : 'JOIN ROOM ↗'}
        </PillButton>
      </form>
    </Modal>
  );
}

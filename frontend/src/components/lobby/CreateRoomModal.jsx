import { useState } from 'react';
import Modal from '../ui/Modal';
import Input from '../ui/Input';
import PillButton from '../ui/PillButton';
import { api } from '../../api/client';

export default function CreateRoomModal({ isOpen, onClose, onCreated }) {
  const [title, setTitle] = useState('');
  const [contentTitle, setContentTitle] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!contentTitle.trim()) {
      setError('Content title is required');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const room = await api('/rooms', {
        method: 'POST',
        body: {
          content_title: contentTitle.trim(),
          title: title.trim() || null,
          password: password.trim() || null,
        },
      });
      onCreated(room);
      onClose();
      setTitle('');
      setContentTitle('');
      setPassword('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="CREATE ROOM">
      <form onSubmit={handleSubmit} className="create-room-form">
        <Input
          label="CONTENT TITLE"
          placeholder="What are we watching?"
          value={contentTitle}
          onChange={(e) => setContentTitle(e.target.value)}
          required
        />
        <Input
          label="ROOM NAME"
          placeholder="Optional room name"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <Input
          label="PASSWORD"
          placeholder="Optional password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        {error && <p className="form-error">{error}</p>}
        <PillButton type="submit" disabled={loading}>
          {loading ? 'CREATING...' : 'CREATE ROOM ↗'}
        </PillButton>
      </form>
    </Modal>
  );
}

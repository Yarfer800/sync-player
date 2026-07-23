import { useState } from 'react';
import GhostButton from '../ui/GhostButton';
import { api } from '../../api/client';
import { hapticFeedback } from '../../utils/telegram';

export default function InviteButton({ roomId }) {
  const [inviteCode, setInviteCode] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleGenerate = async () => {
    try {
      setLoading(true);
      const data = await api(`/rooms/${roomId}/invite`, { method: 'POST' });
      setInviteCode(data.invite_code);
      hapticFeedback('medium');
    } catch (err) {
      console.error('Failed to generate invite:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    if (!inviteCode) return;
    try {
      await navigator.clipboard.writeText(inviteCode);
      setCopied(true);
      hapticFeedback('light');
      setTimeout(() => setCopied(false), 2000);
    } catch {
      const textarea = document.createElement('textarea');
      textarea.value = inviteCode;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (inviteCode) {
    return (
      <div className="invite-section">
        <div className="invite-code">
          <span className="invite-code__label">INVITE CODE</span>
          <code className="invite-code__value">{inviteCode}</code>
        </div>
        <GhostButton onClick={handleCopy}>
          {copied ? 'COPIED ✓' : 'COPY CODE'}
        </GhostButton>
      </div>
    );
  }

  return (
    <GhostButton onClick={handleGenerate} disabled={loading}>
      {loading ? 'GENERATING...' : 'GENERATE INVITE'}
    </GhostButton>
  );
}

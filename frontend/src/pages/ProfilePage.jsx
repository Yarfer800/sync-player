import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import PageShell from '../components/layout/PageShell';
import SectionDivider from '../components/layout/SectionDivider';
import Input from '../components/ui/Input';
import PillButton from '../components/ui/PillButton';
import Spinner from '../components/ui/Spinner';
import { api } from '../api/client';
import { hapticFeedback } from '../utils/telegram';

export default function ProfilePage() {
  const { user, updateUser, loading: authLoading } = useAuth();
  const [username, setUsername] = useState(user?.username || '');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      setSaving(true);
      const updated = await api('/users/me', {
        method: 'PATCH',
        body: { username: username.trim() || null },
      });
      updateUser(updated);
      setSaved(true);
      hapticFeedback('medium');
      setTimeout(() => setSaved(false), 2000);
    } catch (err) {
      console.error('Failed to update profile:', err);
    } finally {
      setSaving(false);
    }
  };

  if (authLoading) return <PageShell><Spinner size={32} /></PageShell>;

  return (
    <PageShell>
      <div className="profile-page">
        <h1 className="profile-page__title">PROFILE</h1>
        <p className="profile-page__subtitle">Your identity in Sync Player.</p>

        <SectionDivider />

        <div className="profile-page__info">
          <div className="profile-page__field">
            <span className="profile-page__label">USER ID</span>
            <span className="profile-page__value">{user?.user_id}</span>
          </div>
          <div className="profile-page__field">
            <span className="profile-page__label">JOINED</span>
            <span className="profile-page__value">
              {user?.created_at ? new Date(user.created_at).toLocaleDateString() : '—'}
            </span>
          </div>
          {user?.in_room && (
            <div className="profile-page__field">
              <span className="profile-page__label">CURRENT ROOM</span>
              <span className="profile-page__value">Room #{user.in_room}</span>
            </div>
          )}
        </div>

        <SectionDivider />

        <form className="profile-page__form" onSubmit={handleSave}>
          <Input
            label="USERNAME"
            placeholder="Enter your username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <PillButton type="submit" disabled={saving}>
            {saving ? 'SAVING...' : saved ? 'SAVED ✓' : 'SAVE CHANGES ↗'}
          </PillButton>
        </form>
      </div>
    </PageShell>
  );
}

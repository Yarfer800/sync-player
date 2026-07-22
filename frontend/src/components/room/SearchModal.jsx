import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import Modal from '../ui/Modal';
import Spinner from '../ui/Spinner';
import { api } from '../../api/client';

export default function SearchModal({ isOpen, onClose, roomId, onVideoSelect }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [saving, setSaving] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    const q = query.trim();
    if (!q) return;

    if (q.startsWith('http://') || q.startsWith('https://')) {
      return handleSelect({ url: q, title: "Direct Link", description: "Loaded from direct URL" });
    }

    try {
      setLoading(true);
      setSearched(true);
      const data = await api('/search', { params: { query: q } });
      setResults(data);
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = async (result) => {
    try {
      setSaving(true);
      // We assume video_source_link is updated in player state
      const newState = {
        room_id: parseInt(roomId),
        current_timecode: 0.0,
        video_source_link: result.url,
        is_paused: true
      };
      
      await api(`/rooms/${roomId}/player/state`, {
        method: 'PUT',
        body: newState
      });
      
      onVideoSelect();
      onClose();
    } catch (err) {
      console.error('Failed to set video:', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="LOAD VIDEO">
      <form className="search-page__form" onSubmit={handleSearch} style={{ marginBottom: '24px' }}>
        <input
          className="search-page__input"
          type="text"
          placeholder="Search YouTube or Paste URL..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          autoComplete="off"
        />
        <motion.button
          className="pill-button"
          type="submit"
          disabled={loading || saving || !query.trim()}
          whileTap={{ scale: 0.97 }}
        >
          {loading ? '...' : 'SEARCH ↗'}
        </motion.button>
      </form>

      {loading ? (
        <Spinner size={32} />
      ) : (
        <AnimatePresence>
          {results.length > 0 && (
            <div className="search-results" style={{ maxHeight: '50vh', overflowY: 'auto', paddingRight: '8px' }}>
              {results.map((result, i) => (
                <motion.div
                  key={result.url}
                  className="search-result"
                  onClick={() => handleSelect(result)}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.35, delay: i * 0.05, ease: [0.16, 1, 0.3, 1] }}
                  style={{ cursor: saving ? 'not-allowed' : 'pointer', opacity: saving ? 0.5 : 1 }}
                >
                  <h3 className="search-result__title">{result.title}</h3>
                  <p className="search-result__description">{result.description}</p>
                  <span className="search-result__url">{result.url}</span>
                </motion.div>
              ))}
            </div>
          )}
          {searched && !loading && results.length === 0 && (
            <motion.p
              className="search-page__empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              No videos found.
            </motion.p>
          )}
        </AnimatePresence>
      )}
    </Modal>
  );
}

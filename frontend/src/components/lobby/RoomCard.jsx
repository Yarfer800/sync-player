import { motion } from 'motion/react';
import { useNavigate } from 'react-router-dom';

export default function RoomCard({ room, index }) {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/room/${room.room_id}`);
  };

  return (
    <motion.div
      className="room-card"
      onClick={handleClick}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.06, ease: [0.16, 1, 0.3, 1] }}
      whileHover={{ borderColor: 'var(--color-iron)' }}
    >
      <div className="room-card__header">
        <h3 className="room-card__title">{room.title || room.content_title}</h3>
        {room.is_private && <span className="room-card__lock">🔒</span>}
      </div>
      <p className="room-card__content">{room.content_title}</p>
      <div className="room-card__footer">
        <span className="room-card__meta">
          {room.participant_count} {room.participant_count === 1 ? 'viewer' : 'viewers'}
        </span>
        <span className="room-card__meta">
          {new Date(room.created_at).toLocaleDateString()}
        </span>
      </div>
    </motion.div>
  );
}

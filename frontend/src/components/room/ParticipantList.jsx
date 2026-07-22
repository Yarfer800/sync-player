import { motion } from 'motion/react';

export default function ParticipantList({ participants }) {
  if (!participants || participants.length === 0) return null;

  return (
    <div className="participant-list">
      <h4 className="participant-list__title">PARTICIPANTS</h4>
      <div className="participant-list__items">
        {participants.map((p, i) => (
          <motion.div
            key={p.id}
            className="participant-item"
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: i * 0.05 }}
          >
            <span className="participant-item__name">
              {p.username || `User ${p.user_id}`}
            </span>
            <span className={`participant-item__role participant-item__role--${p.role}`}>
              {p.role.toUpperCase()}
            </span>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

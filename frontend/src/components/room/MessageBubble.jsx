import { motion } from 'motion/react';

export default function MessageBubble({ message, isOwn, onDelete, index }) {
  const time = message.created_at
    ? new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : '';

  return (
    <motion.div
      className={`message ${isOwn ? 'message--own' : ''}`}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: Math.min(index * 0.03, 0.3), ease: [0.16, 1, 0.3, 1] }}
    >
      <div className="message__header">
        <span className="message__username">{message.username || `User ${message.user_id}`}</span>
        <span className="message__time">{time}</span>
      </div>
      <p className="message__text">{message.text}</p>
      {message.image && (
        <img className="message__image" src={message.image} alt="" />
      )}
      {isOwn && (
        <button
          className="message__delete"
          onClick={() => onDelete(message.id)}
          title="Delete message"
        >
          ×
        </button>
      )}
    </motion.div>
  );
}

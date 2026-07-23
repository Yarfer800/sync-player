import { useState, useEffect, useRef } from 'react';
import { motion } from 'motion/react';
import MessageBubble from './MessageBubble';
import { hapticFeedback } from '../../utils/telegram';

export default function ChatPanel({ messages, onSendMessage, onDeleteMessage, currentUserId, bottomRef, loading }) {
  const [text, setText] = useState('');
  const containerRef = useRef(null);

  useEffect(() => {
    if (bottomRef?.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, bottomRef]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    onSendMessage(text.trim());
    setText('');
    hapticFeedback('light');
  };

  return (
    <div className="chat-panel">
      <div className="chat-panel__messages" ref={containerRef}>
        {loading ? (
          <div className="chat-panel__empty">
            <span className="chat-panel__empty-text">Loading messages...</span>
          </div>
        ) : messages.length === 0 ? (
          <div className="chat-panel__empty">
            <span className="chat-panel__empty-text">No messages yet. Start the conversation.</span>
          </div>
        ) : (
          messages.map((msg, i) => (
            <MessageBubble
              key={msg.id}
              message={msg}
              isOwn={msg.user_id === currentUserId}
              onDelete={onDeleteMessage}
              index={i}
            />
          ))
        )}
        <div ref={bottomRef} />
      </div>
      <form className="chat-panel__input-bar" onSubmit={handleSubmit}>
        <input
          className="chat-panel__input"
          type="text"
          placeholder="Type a message..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          autoComplete="off"
        />
        <motion.button
          className="chat-panel__send"
          type="submit"
          disabled={!text.trim()}
          whileTap={{ scale: 0.95 }}
        >
          ↗
        </motion.button>
      </form>
    </div>
  );
}

import { motion } from 'motion/react';

export default function PillButton({ children, onClick, disabled, className = '', type = 'button' }) {
  return (
    <motion.button
      type={type}
      className={`pill-button ${className}`}
      onClick={onClick}
      disabled={disabled}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.97 }}
    >
      {children}
    </motion.button>
  );
}

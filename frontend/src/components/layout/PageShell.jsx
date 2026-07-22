import { motion } from 'motion/react';

export default function PageShell({ children, className = '' }) {
  return (
    <motion.main
      className={`page-shell ${className}`}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -16 }}
      transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
    >
      {children}
    </motion.main>
  );
}

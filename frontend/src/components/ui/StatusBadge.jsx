export default function StatusBadge({ children }) {
  return (
    <span className="status-badge">
      <span className="status-badge__dot" />
      {children}
    </span>
  );
}

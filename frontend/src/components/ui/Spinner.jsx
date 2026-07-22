export default function Spinner({ size = 24 }) {
  return (
    <div className="spinner-container">
      <svg
        className="spinner"
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill="none"
      >
        <circle
          cx="12"
          cy="12"
          r="10"
          stroke="var(--color-graphite)"
          strokeWidth="2"
        />
        <path
          d="M12 2a10 10 0 0 1 10 10"
          stroke="var(--color-chalk)"
          strokeWidth="2"
          strokeLinecap="round"
        />
      </svg>
    </div>
  );
}

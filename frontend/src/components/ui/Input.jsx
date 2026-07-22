import { forwardRef } from 'react';

const Input = forwardRef(function Input({ label, error, className = '', ...props }, ref) {
  return (
    <div className={`input-group ${className}`}>
      {label && <label className="input-label">{label}</label>}
      <input ref={ref} className={`input-field ${error ? 'input-field--error' : ''}`} {...props} />
      {error && <span className="input-error">{error}</span>}
    </div>
  );
});

export default Input;

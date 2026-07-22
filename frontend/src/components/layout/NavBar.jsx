import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'motion/react';

export default function NavBar() {
  const navigate = useNavigate();
  const location = useLocation();
  const isLobby = location.pathname === '/';

  return (
    <nav className="navbar">
      <div className="navbar__inner">
        <div className="navbar__left">
          {!isLobby && (
            <motion.button
              className="navbar__back"
              onClick={() => navigate('/')}
              whileTap={{ scale: 0.95 }}
            >
              ← BACK
            </motion.button>
          )}
          {isLobby && (
            <span className="navbar__brand">SYNC PLAYER</span>
          )}
        </div>
        <div className="navbar__links">
          <button
            className={`navbar__link ${location.pathname === '/' ? 'navbar__link--active' : ''}`}
            onClick={() => navigate('/')}
          >
            ROOMS
          </button>
          <button
            className={`navbar__link ${location.pathname === '/profile' ? 'navbar__link--active' : ''}`}
            onClick={() => navigate('/profile')}
          >
            PROFILE
          </button>
        </div>
      </div>
    </nav>
  );
}

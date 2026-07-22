import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'motion/react';
import { AuthProvider } from './context/AuthContext';
import NavBar from './components/layout/NavBar';
import LobbyPage from './pages/LobbyPage';
import RoomPage from './pages/RoomPage';
import ProfilePage from './pages/ProfilePage';

function AnimatedRoutes() {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<LobbyPage />} />
        <Route path="/room/:roomId" element={<RoomPage />} />
        <Route path="/profile" element={<ProfilePage />} />
      </Routes>
    </AnimatePresence>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <NavBar />
        <AnimatedRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}

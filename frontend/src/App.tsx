import { Routes, Route } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import Home from './routes/Home'
import Login from './routes/Login'
import Register from './routes/Register'
import Profile from './routes/Profile'
import LobbyList from './routes/LobbyList'
import LobbyRoom from './routes/LobbyRoom'
import Game from './routes/Game'
import GameResult from './routes/GameResult'
import SoloPlay from './routes/SoloPlay'
import Rulebook from './routes/Rulebook'
import NotFound from './routes/NotFound'

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <div className="min-h-screen bg-hanyang-cream">
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/profile" element={isAuthenticated ? <Profile /> : <Login />} />
        <Route path="/lobbies" element={<LobbyList />} />
        <Route path="/solo" element={<SoloPlay />} />
        <Route path="/docs/rulebook" element={<Rulebook />} />
        <Route path="/lobby/:id" element={<LobbyRoom />} />
        <Route path="/game/:id" element={<Game />} />
        <Route path="/game/:id/result" element={<GameResult />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </div>
  )
}

export default App

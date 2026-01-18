import { Routes, Route } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import Home from './routes/Home'
import Login from './routes/Login'
import Register from './routes/Register'
import Profile from './routes/Profile'
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
        <Route path="*" element={<NotFound />} />
      </Routes>
    </div>
  )
}

export default App

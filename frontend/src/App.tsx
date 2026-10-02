import { Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Header from './components/Header'
import ProtectedRoute from './components/ProtectedRoute'
import GuestRoute from './components/GuestRoute'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Admin from './pages/Admin'
import Forbidden from './pages/Forbidden'

function RootRedirect() {
  const { user, loading } = useAuth()
  if (loading) return <div className="loading">Loading…</div>
  if (!user) return <Navigate to="/login" replace />
  return <Navigate to={user.role === 'admin' ? '/admin' : '/dashboard'} replace />
}

export default function App() {
  return (
    <AuthProvider>
      <Header />
      <Routes>
        <Route path="/login" element={<GuestRoute><Login /></GuestRoute>} />
        <Route path="/dashboard" element={
          <ProtectedRoute roles={['member']}><Dashboard /></ProtectedRoute>
        } />
        <Route path="/admin" element={
          <ProtectedRoute roles={['admin']}><Admin /></ProtectedRoute>
        } />
        <Route path="/forbidden" element={<Forbidden />} />
        <Route path="*" element={<RootRedirect />} />
      </Routes>
    </AuthProvider>
  )
}

import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import type { ReactNode } from 'react'

export default function GuestRoute({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth()

  if (loading) return <div className="loading">Loading…</div>

  if (user)
    return <Navigate to={user.role === 'admin' ? '/admin' : '/dashboard'} replace />

  return <>{children}</>
}

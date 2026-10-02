import { Navigate, useLocation } from 'react-router-dom'
import { useAuth, type User } from '../context/AuthContext'
import type { ReactNode } from 'react'

interface Props {
  roles?: User['role'][]
  children: ReactNode
}

export default function ProtectedRoute({ roles, children }: Props) {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) return <div className="loading">Loading…</div>

  if (!user)
    return <Navigate to={`/login?returnTo=${encodeURIComponent(location.pathname)}`} replace />

  if (roles && !roles.includes(user.role))
    return <Navigate to="/forbidden" replace />

  return <>{children}</>
}

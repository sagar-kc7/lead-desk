import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import api, { setOnAuthFailure } from '../api'

export interface User {
  id: number
  name: string
  email: string
  role: 'admin' | 'member'
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<User>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [serverError, setServerError] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    setOnAuthFailure(() => {
      setUser(null)
      navigate('/login', { replace: true })
    })
    return () => setOnAuthFailure(null)
  }, [navigate])

  const restore = useCallback(() => {
    setLoading(true)
    setServerError(false)
    api.get('/auth/me')
      .then(res => setUser(res.data))
      .catch(err => {
        if (err.response?.status === 401) {
          setUser(null)
        } else {
          setServerError(true)
        }
      })
      .finally(() => setLoading(false))
  }, [])

  useEffect(restore, [restore])

  const login = async (email: string, password: string): Promise<User> => {
    const { data } = await api.post('/auth/login', { email, password })
    setUser(data)
    return data
  }

  const logout = async () => {
    try {
      await api.post('/auth/logout')
    } finally {
      setUser(null)
    }
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {serverError ? (
        <div className="loading">
          <div style={{ textAlign: 'center' }}>
            <p style={{ marginBottom: '1rem' }}>Can&apos;t reach the server.</p>
            <button className="btn btn-primary" onClick={restore}>Retry</button>
          </div>
        </div>
      ) : (
        children
      )}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be inside AuthProvider')
  return ctx
}

import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Forbidden() {
  const { user } = useAuth()
  const home = user?.role === 'admin' ? '/admin' : '/dashboard'

  return (
    <div className="page centered">
      <h2>403 — Forbidden</h2>
      <p>You don't have access to this page.</p>
      {user
        ? <Link to={home} className="btn btn-primary" style={{ marginTop: '1rem', display: 'inline-block' }}>
            Go Home
          </Link>
        : <Link to="/login" className="btn btn-primary" style={{ marginTop: '1rem', display: 'inline-block' }}>
            Go to Login
          </Link>
      }
    </div>
  )
}

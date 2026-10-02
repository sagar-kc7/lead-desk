import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Header() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  if (!user) return null

  const handleLogout = async () => {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <header className="header">
      <h1>Lead Desk</h1>
      <div className="header-right">
        <span className="header-name">{user.name}</span>
        <button className="btn btn-logout" onClick={handleLogout}>
          Logout
        </button>
      </div>
    </header>
  )
}

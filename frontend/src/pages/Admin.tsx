import { useAuth } from '../context/AuthContext'

export default function Admin() {
  const { user } = useAuth()
  return (
    <div className="page">
      <h2>Admin Panel</h2>
      <p>Welcome, {user?.name}. All leads and users will appear here.</p>
    </div>
  )
}

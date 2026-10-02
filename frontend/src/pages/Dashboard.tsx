import { useAuth } from '../context/AuthContext'

export default function Dashboard() {
  const { user } = useAuth()
  return (
    <div className="page">
      <h2>Dashboard</h2>
      <p>Welcome, {user?.name}. Your leads will appear here.</p>
    </div>
  )
}

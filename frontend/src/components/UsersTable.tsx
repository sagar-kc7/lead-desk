import type { UserInfo } from '../types'

interface Props {
  users: UserInfo[]
  loading: boolean
  error: string
  onRetry: () => void
}

export default function UsersTable({ users, loading, error, onRetry }: Props) {
  if (loading) return <p className="state-msg">Loading users…</p>

  if (error)
    return (
      <div className="state-msg">
        <p className="error-text">{error}</p>
        <button className="btn btn-primary" onClick={onRetry}>Retry</button>
      </div>
    )

  if (users.length === 0) return <p className="state-msg">No users found.</p>

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          {users.map(u => (
            <tr key={u.id}>
              <td>{u.name}</td>
              <td>{u.email}</td>
              <td className="capitalize">{u.role}</td>
              <td>{new Date(u.created_at).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

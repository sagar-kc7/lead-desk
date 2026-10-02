import type { Lead } from '../types'

interface Props {
  leads: Lead[]
  loading: boolean
  error: string
  onRetry: () => void
  showOwner?: boolean
}

function StatusBadge({ status }: { status: string }) {
  return <span className={`badge badge-${status}`}>{status}</span>
}

export default function LeadsTable({ leads, loading, error, onRetry, showOwner }: Props) {
  if (loading) return <p className="state-msg">Loading leads…</p>

  if (error)
    return (
      <div className="state-msg">
        <p className="error-text">{error}</p>
        <button className="btn btn-primary" onClick={onRetry}>Retry</button>
      </div>
    )

  if (leads.length === 0) return <p className="state-msg">No leads yet.</p>

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Company</th>
            <th>Status</th>
            {showOwner && <th>Owner</th>}
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          {leads.map(lead => (
            <tr key={lead.id}>
              <td>{lead.name}</td>
              <td>{lead.email}</td>
              <td>{lead.company}</td>
              <td><StatusBadge status={lead.status} /></td>
              {showOwner && <td>{lead.owner_name}</td>}
              <td>{new Date(lead.created_at).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

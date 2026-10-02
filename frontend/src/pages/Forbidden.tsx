import { Link } from 'react-router-dom'

export default function Forbidden() {
  return (
    <div className="page centered">
      <h2>403 — Forbidden</h2>
      <p>You don't have access to this page.</p>
      <Link to="/login" className="btn btn-primary" style={{ marginTop: '1rem', display: 'inline-block' }}>
        Go to Login
      </Link>
    </div>
  )
}

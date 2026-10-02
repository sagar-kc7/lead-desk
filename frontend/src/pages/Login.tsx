import { type FormEvent, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState({ email: '', password: '' })
  const [apiError, setApiError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const validate = () => {
    const e = { email: '', password: '' }
    if (!email) e.email = 'Email is required'
    else if (!EMAIL_RE.test(email)) e.email = 'Invalid email format'
    if (!password) e.password = 'Password is required'
    setErrors(e)
    return !e.email && !e.password
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setApiError('')
    if (!validate()) return

    setSubmitting(true)
    try {
      const user = await login(email, password)
      const returnTo = searchParams.get('returnTo')
      const home = user.role === 'admin' ? '/admin' : '/dashboard'
      navigate(returnTo || home, { replace: true })
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { error?: string } } })?.response?.data?.error
        || 'Login failed'
      setApiError(msg)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <h2>Sign in to Lead Desk</h2>

        {apiError && <div className="api-error">{apiError}</div>}

        <form onSubmit={handleSubmit} noValidate>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              autoComplete="email"
            />
            {errors.email && <p className="field-error">{errors.email}</p>}
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              autoComplete="current-password"
            />
            {errors.password && <p className="field-error">{errors.password}</p>}
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-block"
            disabled={submitting}
          >
            {submitting ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  )
}

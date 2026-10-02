import { type FormEvent, useState } from 'react'
import api from '../api'
import type { Lead } from '../types'

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const STATUSES = ['new', 'contacted', 'qualified', 'lost'] as const

interface Props {
  onLeadAdded: (lead: Lead) => void
}

interface Fields {
  name: string
  email: string
  company: string
  website: string
  status: string
}

const empty: Fields = { name: '', email: '', company: '', website: '', status: 'new' }

export default function AddLeadForm({ onLeadAdded }: Props) {
  const [fields, setFields] = useState<Fields>(empty)
  const [errors, setErrors] = useState<Partial<Fields>>({})
  const [apiError, setApiError] = useState('')
  const [success, setSuccess] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const set = (key: keyof Fields, value: string) =>
    setFields(prev => ({ ...prev, [key]: value }))

  const validate = (): boolean => {
    const e: Partial<Fields> = {}
    if (!fields.name.trim()) e.name = 'Name is required'
    else if (fields.name.trim().length > 100) e.name = 'Max 100 characters'

    if (!fields.email) e.email = 'Email is required'
    else if (!EMAIL_RE.test(fields.email)) e.email = 'Invalid email format'
    else if (fields.email.length > 254) e.email = 'Max 254 characters'

    if (!fields.company.trim()) e.company = 'Company is required'
    else if (fields.company.trim().length > 100) e.company = 'Max 100 characters'

    const w = fields.website.trim()
    if (w) {
      if (!w.startsWith('http://') && !w.startsWith('https://'))
        e.website = 'Must be an http or https URL'
      else if (w.length > 255) e.website = 'Max 255 characters'
    }

    setErrors(e)
    return Object.keys(e).length === 0
  }

  const handleSubmit = async (ev: FormEvent) => {
    ev.preventDefault()
    setApiError('')
    setSuccess('')
    if (!validate()) return

    setSubmitting(true)
    try {
      const body = {
        name: fields.name.trim(),
        email: fields.email.trim(),
        company: fields.company.trim(),
        website: fields.website.trim() || null,
        status: fields.status,
      }
      const { data } = await api.post('/leads', body)
      onLeadAdded(data)
      setFields(empty)
      setSuccess('Lead created!')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { error?: string } } })?.response?.data?.error
        || 'Failed to create lead'
      setApiError(msg)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form className="add-lead-form" onSubmit={handleSubmit} noValidate>
      <h3>Add Lead</h3>

      {apiError && <div className="api-error">{apiError}</div>}
      {success && <div className="success-msg">{success}</div>}

      <div className="form-grid">
        <div className="form-group">
          <label htmlFor="lead-name">Name</label>
          <input id="lead-name" value={fields.name}
            onChange={e => set('name', e.target.value)} />
          {errors.name && <p className="field-error">{errors.name}</p>}
        </div>

        <div className="form-group">
          <label htmlFor="lead-email">Email</label>
          <input id="lead-email" type="email" value={fields.email}
            onChange={e => set('email', e.target.value)} />
          {errors.email && <p className="field-error">{errors.email}</p>}
        </div>

        <div className="form-group">
          <label htmlFor="lead-company">Company</label>
          <input id="lead-company" value={fields.company}
            onChange={e => set('company', e.target.value)} />
          {errors.company && <p className="field-error">{errors.company}</p>}
        </div>

        <div className="form-group">
          <label htmlFor="lead-website">Website</label>
          <input id="lead-website" placeholder="https://example.com" value={fields.website}
            onChange={e => set('website', e.target.value)} />
          {errors.website && <p className="field-error">{errors.website}</p>}
        </div>

        <div className="form-group">
          <label htmlFor="lead-status">Status</label>
          <select id="lead-status" value={fields.status}
            onChange={e => set('status', e.target.value)}>
            {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>

        <div className="form-group form-submit">
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? 'Adding…' : 'Add Lead'}
          </button>
        </div>
      </div>
    </form>
  )
}

import { useCallback, useEffect, useState } from 'react'
import api from '../api'
import LeadsTable from '../components/LeadsTable'
import AddLeadForm from '../components/AddLeadForm'
import type { Lead } from '../types'

export default function Dashboard() {
  const [leads, setLeads] = useState<Lead[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchLeads = useCallback(() => {
    setLoading(true)
    setError('')
    api.get('/leads')
      .then(res => setLeads(res.data))
      .catch(() => setError('Failed to load leads.'))
      .finally(() => setLoading(false))
  }, [])

  useEffect(fetchLeads, [fetchLeads])

  const handleLeadAdded = (lead: Lead) => {
    setLeads(prev => [lead, ...prev])
  }

  return (
    <div className="page">
      <h2>My Leads</h2>
      <AddLeadForm onLeadAdded={handleLeadAdded} />
      <LeadsTable leads={leads} loading={loading} error={error} onRetry={fetchLeads} />
    </div>
  )
}

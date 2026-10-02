import { useCallback, useEffect, useState } from 'react'
import api from '../api'
import LeadsTable from '../components/LeadsTable'
import UsersTable from '../components/UsersTable'
import type { Lead, UserInfo } from '../types'

export default function Admin() {
  const [leads, setLeads] = useState<Lead[]>([])
  const [leadsLoading, setLeadsLoading] = useState(true)
  const [leadsError, setLeadsError] = useState('')

  const [users, setUsers] = useState<UserInfo[]>([])
  const [usersLoading, setUsersLoading] = useState(true)
  const [usersError, setUsersError] = useState('')

  const fetchLeads = useCallback(() => {
    setLeadsLoading(true)
    setLeadsError('')
    api.get('/leads')
      .then(res => setLeads(res.data))
      .catch(() => setLeadsError('Failed to load leads.'))
      .finally(() => setLeadsLoading(false))
  }, [])

  const fetchUsers = useCallback(() => {
    setUsersLoading(true)
    setUsersError('')
    api.get('/admin/users')
      .then(res => setUsers(res.data))
      .catch(() => setUsersError('Failed to load users.'))
      .finally(() => setUsersLoading(false))
  }, [])

  useEffect(fetchLeads, [fetchLeads])
  useEffect(fetchUsers, [fetchUsers])

  return (
    <div className="page">
      <h2>All Leads</h2>
      <LeadsTable
        leads={leads} loading={leadsLoading} error={leadsError}
        onRetry={fetchLeads} showOwner
      />

      <h2 style={{ marginTop: '2.5rem' }}>Users</h2>
      <UsersTable users={users} loading={usersLoading} error={usersError} onRetry={fetchUsers} />
    </div>
  )
}

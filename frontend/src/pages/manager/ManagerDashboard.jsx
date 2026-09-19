import { useEffect, useState } from 'react'
import * as managerApi from '../../api/manager'
import LoadingState from '../../components/common/LoadingState'
import ErrorState from '../../components/common/ErrorState'
import { getErrorMessage } from '../../api/errorMessage'

export default function ManagerDashboard() {
  const [team, setTeam] = useState(null)
  const [error, setError] = useState(null)

  const load = () => {
    setError(null)
    managerApi.getTeamOverview().then(setTeam).catch((err) => setError(getErrorMessage(err)))
  }

  useEffect(load, [])

  if (error) return <ErrorState message={error} onRetry={load} />
  if (!team) return <LoadingState />

  const byRole = team.reduce((acc, m) => ({ ...acc, [m.role]: (acc[m.role] || 0) + 1 }), {})

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-semibold text-slate-900">Manager Dashboard</h1>
      <div className="grid grid-cols-3 gap-4">{Object.entries(byRole).map(([role, count]) => (
        <div key={role} className="bg-white rounded-lg p-5 shadow-sm"><div className="text-sm text-slate-500">{role}</div><div className="text-3xl font-semibold text-slate-900">{count}</div></div>
      ))}</div>
    </div>
  )
}
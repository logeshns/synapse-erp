import { useEffect, useState } from 'react'
import * as managerApi from '../../api/manager'
import LoadingState from '../../components/common/LoadingState'
import ErrorState from '../../components/common/ErrorState'
import { getErrorMessage } from '../../api/errorMessage'
import { useToast } from '../../components/common/Toast'

const METRIC_LABELS = {
  order_requests_submitted: 'Requests Submitted', orders_created: 'Orders Created',
  orders_confirmed: 'Orders Confirmed', orders_rejected: 'Orders Rejected', receipts_generated: 'Receipts Generated',
}

function RatingForm({ employee, onSaved }) {
  const { push } = useToast()
  const [form, setForm] = useState({ period: new Date().toISOString().slice(0, 7), communication: 3, accuracy: 3, order_processing: 3, customer_handling: 3, overall: 3, comments: '' })
  const [submitting, setSubmitting] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await managerApi.addRating({ ...form, employee_id: employee.user_id })
      push(`Rating saved for ${employee.name}.`, 'success')
      onSaved()
    } catch (err) {
      push(getErrorMessage(err), 'error')
    } finally {
      setSubmitting(false)
    }
  }

  const field = (key, label) => (
    <label className="text-xs text-slate-500 flex flex-col gap-1">{label}
      <input type="number" min="1" max="5" value={form[key]} onChange={(e) => setForm((f) => ({ ...f, [key]: Number(e.target.value) }))} className="px-2 py-1 border border-slate-300 rounded text-sm" />
    </label>
  )

  return (
    <form onSubmit={submit} className="grid grid-cols-3 gap-3 p-4 bg-slate-50 rounded-md">
      {field('communication', 'Communication')}{field('accuracy', 'Accuracy')}{field('order_processing', 'Order Processing')}
      {field('customer_handling', 'Customer Handling')}{field('overall', 'Overall')}
      <label className="text-xs text-slate-500 flex flex-col gap-1">Period<input value={form.period} onChange={(e) => setForm((f) => ({ ...f, period: e.target.value }))} className="px-2 py-1 border border-slate-300 rounded text-sm" /></label>
      <textarea placeholder="Comments" value={form.comments} onChange={(e) => setForm((f) => ({ ...f, comments: e.target.value }))} className="col-span-3 px-2 py-1 border border-slate-300 rounded text-sm" rows={2} />
      <button type="submit" disabled={submitting} className="col-span-3 px-4 py-2 bg-slate-900 text-white rounded-md text-sm hover:bg-slate-800 disabled:opacity-50 w-fit">{submitting ? 'Saving…' : 'Save Rating'}</button>
    </form>
  )
}

export default function Team() {
  const [team, setTeam] = useState(null)
  const [error, setError] = useState(null)
  const [rating, setRating] = useState(null)

  const load = () => {
    setError(null)
    managerApi.getTeamOverview().then(setTeam).catch((err) => setError(getErrorMessage(err)))
  }

  useEffect(load, [])

  if (error) return <ErrorState message={error} onRetry={load} />
  if (!team) return <LoadingState />

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-900">Team</h1>
      <div className="space-y-3">{team.map((m) => (
        <div key={m.user_id} className="bg-white rounded-lg shadow-sm p-4">
          <div className="flex justify-between items-center">
            <div><div className="font-medium text-slate-900">{m.name}</div><div className="text-xs text-slate-400">{m.role} — last {m.period_days} days</div></div>
            <div className="flex gap-4 text-sm text-slate-600">
              {Object.entries(METRIC_LABELS).filter(([key]) => m[key] !== undefined && m[key] !== null).map(([key, label]) => (
                <div key={key} className="text-center"><div className="font-semibold text-slate-900">{m[key]}</div><div className="text-xs text-slate-400">{label}</div></div>
              ))}
              <button onClick={() => setRating(rating?.user_id === m.user_id ? null : m)} className="text-slate-600 hover:text-slate-900 font-medium text-sm">{rating?.user_id === m.user_id ? 'Close' : 'Rate →'}</button>
            </div>
          </div>
          {rating?.user_id === m.user_id && <div className="mt-3"><RatingForm employee={m} onSaved={() => { setRating(null); load() }} /></div>}
        </div>
      ))}</div>
    </div>
  )
}
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import * as orderRequestsApi from '../../api/orderRequests'
import LoadingState from '../../components/common/LoadingState'
import ErrorState from '../../components/common/ErrorState'
import EmptyState from '../../components/common/EmptyState'
import StatusBadge from '../../components/common/StatusBadge'
import { getErrorMessage } from '../../api/errorMessage'
import { useToast } from '../../components/common/Toast'

export default function OrderRequests() {
  const { push } = useToast()
  const [requests, setRequests] = useState(null)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ source: 'OFFLINE', raw_text: '' })
  const [submitting, setSubmitting] = useState(false)

  const load = () => {
    setError(null)
    orderRequestsApi.listOrderRequests(filter ? { review_status: filter } : {}).then(setRequests).catch((err) => setError(getErrorMessage(err)))
  }

  useEffect(load, [filter])

  const submitNew = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await orderRequestsApi.createOrderRequest(form)
      push('Order request created.', 'success')
      setShowForm(false)
      setForm({ source: 'OFFLINE', raw_text: '' })
      load()
    } catch (err) {
      push(getErrorMessage(err), 'error')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-slate-900">Order Requests</h1>
        <button onClick={() => setShowForm((s) => !s)} className="px-4 py-2 bg-slate-900 text-white rounded-md text-sm hover:bg-slate-800">+ New Offline Request</button>
      </div>

      {showForm && (
        <form onSubmit={submitNew} className="bg-white rounded-lg shadow-sm p-5 space-y-3">
          <p className="text-sm text-slate-500">Enter what a customer told you by phone, email, or in person. AI will extract the structured order on the next screen.</p>
          <textarea required rows={3} value={form.raw_text} onChange={(e) => setForm((f) => ({ ...f, raw_text: e.target.value }))} placeholder='e.g. "ABC Technologies wants 10 Dell laptops and 20 wireless keyboards"' className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-slate-400" />
          <button type="submit" disabled={submitting} className="px-4 py-2 bg-slate-900 text-white rounded-md text-sm hover:bg-slate-800 disabled:opacity-50">{submitting ? 'Creating…' : 'Create Request'}</button>
        </form>
      )}

      <div className="flex gap-2">
        {['', 'PENDING_REVIEW', 'APPROVED', 'REJECTED'].map((s) => (
          <button key={s} onClick={() => setFilter(s)} className={`px-3 py-1.5 rounded-md text-sm ${filter === s ? 'bg-slate-900 text-white' : 'bg-white text-slate-600 hover:bg-slate-100'}`}>{s || 'All'}</button>
        ))}
      </div>

      {error && <ErrorState message={error} onRetry={load} />}
      {!error && !requests && <LoadingState />}
      {requests && requests.length === 0 && <EmptyState message="No order requests found." />}

      {requests && requests.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-500 text-xs uppercase">
              <tr><th className="px-5 py-3 text-left">Request #</th><th className="px-5 py-3 text-left">Source</th><th className="px-5 py-3 text-left">Preview</th><th className="px-5 py-3 text-left">AI Status</th><th className="px-5 py-3 text-left">Status</th><th className="px-5 py-3"></th></tr>
            </thead>
            <tbody>
              {requests.map((r) => (
                <tr key={r.id} className="border-t border-slate-50 hover:bg-slate-50">
                  <td className="px-5 py-3 font-mono text-xs">{r.request_number}</td>
                  <td className="px-5 py-3">{r.source}</td>
                  <td className="px-5 py-3 text-slate-500">{r.raw_text?.slice(0, 50)}{r.raw_text?.length > 50 ? '…' : ''}</td>
                  <td className="px-5 py-3"><StatusBadge status={r.ai_status} /></td>
                  <td className="px-5 py-3"><StatusBadge status={r.review_status} /></td>
                  <td className="px-5 py-3 text-right"><Link to={`/sales/order-requests/${r.id}`} className="text-slate-600 hover:text-slate-900 font-medium">Review →</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
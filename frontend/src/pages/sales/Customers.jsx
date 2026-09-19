import { useEffect, useState } from 'react'
import * as customersApi from '../../api/customers'
import LoadingState from '../../components/common/LoadingState'
import ErrorState from '../../components/common/ErrorState'
import EmptyState from '../../components/common/EmptyState'
import { getErrorMessage } from '../../api/errorMessage'
import { useToast } from '../../components/common/Toast'

export default function Customers() {
  const { push } = useToast()
  const [customers, setCustomers] = useState(null)
  const [error, setError] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name: '', email: '', phone: '', address: '' })
  const [submitting, setSubmitting] = useState(false)

  const load = () => {
    setError(null)
    customersApi.listCustomers().then(setCustomers).catch((err) => setError(getErrorMessage(err)))
  }

  useEffect(load, [])

  const submit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await customersApi.createCustomer(form)
      push('Customer created.', 'success')
      setShowForm(false)
      setForm({ name: '', email: '', phone: '', address: '' })
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
        <h1 className="text-2xl font-semibold text-slate-900">Customers</h1>
        <button onClick={() => setShowForm((s) => !s)} className="px-4 py-2 bg-slate-900 text-white rounded-md text-sm hover:bg-slate-800">+ New Customer</button>
      </div>
      {showForm && (
        <form onSubmit={submit} className="bg-white rounded-lg shadow-sm p-5 grid grid-cols-2 gap-3">
          <input required placeholder="Name" value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} className="px-3 py-2 border border-slate-300 rounded-md text-sm" />
          <input type="email" placeholder="Email" value={form.email} onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))} className="px-3 py-2 border border-slate-300 rounded-md text-sm" />
          <input placeholder="Phone" value={form.phone} onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))} className="px-3 py-2 border border-slate-300 rounded-md text-sm" />
          <input placeholder="Address" value={form.address} onChange={(e) => setForm((f) => ({ ...f, address: e.target.value }))} className="px-3 py-2 border border-slate-300 rounded-md text-sm" />
          <button type="submit" disabled={submitting} className="col-span-2 px-4 py-2 bg-slate-900 text-white rounded-md text-sm hover:bg-slate-800 disabled:opacity-50 w-fit">{submitting ? 'Saving…' : 'Save'}</button>
        </form>
      )}
      {error && <ErrorState message={error} onRetry={load} />}
      {!error && !customers && <LoadingState />}
      {customers && customers.length === 0 && <EmptyState message="No customers yet." />}
      {customers && customers.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-500 text-xs uppercase"><tr><th className="px-5 py-3 text-left">Name</th><th className="px-5 py-3 text-left">Email</th><th className="px-5 py-3 text-left">Phone</th></tr></thead>
            <tbody>{customers.map((c) => (
              <tr key={c.id} className="border-t border-slate-50">
                <td className="px-5 py-3">{c.name}</td>
                <td className="px-5 py-3 text-slate-500">{c.email || '—'}</td>
                <td className="px-5 py-3 text-slate-500">{c.phone || '—'}</td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      )}
    </div>
  )
}
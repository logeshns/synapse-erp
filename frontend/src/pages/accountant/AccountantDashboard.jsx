import { useEffect, useState } from 'react'
import * as invoicesApi from '../../api/invoices'
import LoadingState from '../../components/common/LoadingState'
import ErrorState from '../../components/common/ErrorState'
import { getErrorMessage } from '../../api/errorMessage'

export default function AccountantDashboard() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  const load = () => {
    setError(null)
    setData(null)
    Promise.all([invoicesApi.listInvoices({ status: 'UNPAID' }), invoicesApi.listInvoices({ status: 'PAID' }), invoicesApi.listInvoices({ status: 'OVERDUE' })])
      .then(([unpaid, paid, overdue]) => setData({ unpaid, paid, overdue }))
      .catch((err) => setError(getErrorMessage(err)))
  }

  useEffect(load, [])

  if (error) return <ErrorState message={error} onRetry={load} />
  if (!data) return <LoadingState />

  const sum = (list) => list.reduce((acc, i) => acc + Number(i.total), 0)

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-semibold text-slate-900">Accountant Dashboard</h1>
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white rounded-lg p-5 shadow-sm"><div className="text-sm text-slate-500">Unpaid</div><div className="text-2xl font-semibold text-amber-600">₹{sum(data.unpaid).toFixed(2)}</div><div className="text-xs text-slate-400">{data.unpaid.length} invoice(s)</div></div>
        <div className="bg-white rounded-lg p-5 shadow-sm"><div className="text-sm text-slate-500">Paid</div><div className="text-2xl font-semibold text-emerald-600">₹{sum(data.paid).toFixed(2)}</div><div className="text-xs text-slate-400">{data.paid.length} invoice(s)</div></div>
        <div className="bg-white rounded-lg p-5 shadow-sm"><div className="text-sm text-slate-500">Overdue</div><div className="text-2xl font-semibold text-red-600">₹{sum(data.overdue).toFixed(2)}</div><div className="text-xs text-slate-400">{data.overdue.length} invoice(s)</div></div>
      </div>
    </div>
  )
}
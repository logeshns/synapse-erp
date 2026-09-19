import { useEffect, useState } from 'react'
import * as invoicesApi from '../../api/invoices'
import LoadingState from '../../components/common/LoadingState'
import ErrorState from '../../components/common/ErrorState'
import EmptyState from '../../components/common/EmptyState'
import StatusBadge from '../../components/common/StatusBadge'
import { getErrorMessage } from '../../api/errorMessage'
import { useToast } from '../../components/common/Toast'

export default function Invoices() {
  const { push } = useToast()
  const [invoices, setInvoices] = useState(null)
  const [error, setError] = useState(null)

  const load = () => {
    setError(null)
    invoicesApi.listInvoices().then(setInvoices).catch((err) => setError(getErrorMessage(err)))
  }

  useEffect(load, [])

  const viewPdf = async (id) => {
    try {
      await invoicesApi.openInvoicePdf(id)
    } catch (err) {
      push(getErrorMessage(err), 'error')
    }
  }

  if (error) return <ErrorState message={error} onRetry={load} />
  if (!invoices) return <LoadingState />

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-900">Invoices</h1>
      {invoices.length === 0 ? <EmptyState message="No invoices yet." /> : (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-500 text-xs uppercase"><tr><th className="px-5 py-3 text-left">Invoice #</th><th className="px-5 py-3 text-left">Total</th><th className="px-5 py-3 text-left">Due</th><th className="px-5 py-3 text-left">Status</th><th className="px-5 py-3"></th></tr></thead>
            <tbody>{invoices.map((inv) => (
              <tr key={inv.id} className="border-t border-slate-50">
                <td className="px-5 py-3 font-mono text-xs">{inv.invoice_number}</td>
                <td className="px-5 py-3">₹{Number(inv.total).toFixed(2)}</td>
                <td className="px-5 py-3 text-slate-500">{inv.due_date}</td>
                <td className="px-5 py-3"><StatusBadge status={inv.status} /></td>
                <td className="px-5 py-3 text-right"><button onClick={() => viewPdf(inv.id)} className="text-slate-600 hover:text-slate-900 font-medium">View PDF →</button></td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      )}
    </div>
  )
}
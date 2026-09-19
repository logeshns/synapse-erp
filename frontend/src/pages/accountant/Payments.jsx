import { useEffect, useState } from 'react'
import * as invoicesApi from '../../api/invoices'
import * as paymentsApi from '../../api/payments'
import LoadingState from '../../components/common/LoadingState'
import ErrorState from '../../components/common/ErrorState'
import EmptyState from '../../components/common/EmptyState'
import StatusBadge from '../../components/common/StatusBadge'
import { getErrorMessage } from '../../api/errorMessage'
import { useToast } from '../../components/common/Toast'

const TABS = ['UNPAID', 'PAID', 'OVERDUE']

export default function Payments() {
  const { push } = useToast()
  const [tab, setTab] = useState('UNPAID')
  const [invoices, setInvoices] = useState(null)
  const [error, setError] = useState(null)
  const [creating, setCreating] = useState(null)

  const load = () => {
    setError(null)
    invoicesApi.listInvoices({ status: tab }).then(setInvoices).catch((err) => setError(getErrorMessage(err)))
  }

  useEffect(load, [tab])

  const createLink = async (invoiceId) => {
    setCreating(invoiceId)
    try {
      const { checkout_url } = await paymentsApi.createCheckout(invoiceId)
      await navigator.clipboard.writeText(checkout_url).catch(() => {})
      push('Payment link created and copied to clipboard.', 'success')
      window.open(checkout_url, '_blank')
    } catch (err) {
      push(getErrorMessage(err), 'error')
    } finally {
      setCreating(null)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-900">Payments</h1>
      <div className="flex gap-2">{TABS.map((t) => <button key={t} onClick={() => setTab(t)} className={`px-3 py-1.5 rounded-md text-sm ${tab === t ? 'bg-slate-900 text-white' : 'bg-white text-slate-600 hover:bg-slate-100'}`}>{t}</button>)}</div>
      {error && <ErrorState message={error} onRetry={load} />}
      {!error && !invoices && <LoadingState />}
      {invoices && invoices.length === 0 && <EmptyState message={`No ${tab.toLowerCase()} invoices.`} />}
      {invoices && invoices.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-500 text-xs uppercase"><tr><th className="px-5 py-3 text-left">Invoice #</th><th className="px-5 py-3 text-left">Total</th><th className="px-5 py-3 text-left">Due</th><th className="px-5 py-3 text-left">Status</th><th className="px-5 py-3"></th></tr></thead>
            <tbody>{invoices.map((inv) => (
              <tr key={inv.id} className="border-t border-slate-50">
                <td className="px-5 py-3 font-mono text-xs">{inv.invoice_number}</td>
                <td className="px-5 py-3">₹{Number(inv.total).toFixed(2)}</td>
                <td className="px-5 py-3 text-slate-500">{inv.due_date}</td>
                <td className="px-5 py-3"><StatusBadge status={inv.status} /></td>
                <td className="px-5 py-3 text-right">{inv.status !== 'PAID' && <button onClick={() => createLink(inv.id)} disabled={creating === inv.id} className="text-slate-600 hover:text-slate-900 font-medium disabled:opacity-50">{creating === inv.id ? 'Creating…' : 'Create Payment Link →'}</button>}</td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      )}
    </div>
  )
}
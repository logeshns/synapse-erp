import { useEffect, useState } from 'react'
import * as paymentsApi from '../../api/payments'
import * as receiptsApi from '../../api/receipts'
import LoadingState from '../../components/common/LoadingState'
import ErrorState from '../../components/common/ErrorState'
import EmptyState from '../../components/common/EmptyState'
import { getErrorMessage } from '../../api/errorMessage'
import { useToast } from '../../components/common/Toast'

export default function Receipts() {
  const { push } = useToast()
  const [payments, setPayments] = useState(null)
  const [error, setError] = useState(null)
  const [busyId, setBusyId] = useState(null)

  const load = () => {
    setError(null)
    paymentsApi.listPayments({ status: 'SUCCEEDED' }).then(setPayments).catch((err) => setError(getErrorMessage(err)))
  }

  useEffect(load, [])

  const generateAndView = async (paymentId) => {
    setBusyId(paymentId)
    try {
      const receipt = await receiptsApi.generateReceipt(paymentId)
      await receiptsApi.openReceiptPdf(receipt.id)
    } catch (err) {
      push(getErrorMessage(err), 'error')
    } finally {
      setBusyId(null)
    }
  }

  if (error) return <ErrorState message={error} onRetry={load} />
  if (!payments) return <LoadingState />

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-900">Payment Receipts</h1>
      {payments.length === 0 ? <EmptyState message="No successful payments yet." /> : (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-500 text-xs uppercase"><tr><th className="px-5 py-3 text-left">Payment Ref</th><th className="px-5 py-3 text-left">Amount</th><th className="px-5 py-3 text-left">Paid At</th><th className="px-5 py-3"></th></tr></thead>
            <tbody>{payments.map((p) => (
              <tr key={p.id} className="border-t border-slate-50">
                <td className="px-5 py-3 font-mono text-xs">{p.provider_reference || '—'}</td>
                <td className="px-5 py-3">₹{Number(p.amount).toFixed(2)}</td>
                <td className="px-5 py-3 text-slate-500">{p.paid_at ? new Date(p.paid_at).toLocaleString() : '—'}</td>
                <td className="px-5 py-3 text-right"><button onClick={() => generateAndView(p.id)} disabled={busyId === p.id} className="text-slate-600 hover:text-slate-900 font-medium disabled:opacity-50">{busyId === p.id ? 'Generating…' : 'Generate & View Receipt →'}</button></td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      )}
    </div>
  )
}
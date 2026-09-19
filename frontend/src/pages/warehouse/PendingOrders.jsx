import { useEffect, useState } from 'react'
import * as ordersApi from '../../api/orders'
import * as invoicesApi from '../../api/invoices'
import * as paymentsApi from '../../api/payments'
import LoadingState from '../../components/common/LoadingState'
import ErrorState from '../../components/common/ErrorState'
import EmptyState from '../../components/common/EmptyState'
import { getErrorMessage } from '../../api/errorMessage'
import { useToast } from '../../components/common/Toast'

const REASON_CODES = ['INSUFFICIENT_STOCK', 'CUSTOMER_REQUEST', 'PRICING_ISSUE', 'OTHER']

function OrderRow({ order, onChanged }) {
  const { push } = useToast()
  const [stock, setStock] = useState(null)
  const [expanded, setExpanded] = useState(false)
  const [busy, setBusy] = useState(false)
  const [reasonCode, setReasonCode] = useState('INSUFFICIENT_STOCK')
  const [details, setDetails] = useState('')
  const [invoice, setInvoice] = useState(null)
  const [paymentLink, setPaymentLink] = useState('')

  const runStockCheck = async () => {
    try {
      const res = await ordersApi.stockCheck(order.id)
      setStock(res)
      return res
    } catch (err) {
      push(getErrorMessage(err), 'error')
      return null
    }
  }

  const toggle = async () => {
    if (!expanded && !stock) {
      await runStockCheck()
    }
    setExpanded((e) => !e)
  }

  const handleGenerateInvoice = async () => {
    setBusy(true)
    try {
      // 1. Confirm the order first so the backend state machine accepts invoice generation
      if (order.status === 'PENDING_WAREHOUSE') {
        await ordersApi.confirmOrder(order.id).catch(() => {})
      }
      // 2. Generate the invoice
      const inv = await invoicesApi.generateInvoice(order.id)
      setInvoice(inv)
      push(`Invoice ${inv.invoice_number} generated successfully!`, 'success')

      // 3. Pre-fetch the Stripe payment checkout URL
      try {
        const checkout = await paymentsApi.createCheckout(inv.id)
        if (checkout?.checkout_url) {
          setPaymentLink(checkout.checkout_url)
        }
      } catch (payErr) {
        console.warn('Payment link pre-fetch notice:', payErr)
      }
    } catch (err) {
      push(getErrorMessage(err), 'error')
    } finally {
      setBusy(false)
    }
  }

  const handleViewPdf = async () => {
    if (!invoice?.id) return
    try {
      await invoicesApi.openInvoicePdf(invoice.id)
    } catch (err) {
      push(getErrorMessage(err), 'error')
    }
  }

  const copyPaymentLink = async () => {
    if (!paymentLink) return
    await navigator.clipboard.writeText(paymentLink).catch(() => {})
    push('Stripe checkout link copied to clipboard!', 'success')
  }

  const reject = async () => {
    if (reasonCode !== 'INSUFFICIENT_STOCK' && !details.trim()) {
      return push('Please provide details for this rejection reason.', 'error')
    }
    setBusy(true)
    try {
      await ordersApi.rejectOrder(order.id, { reason_code: reasonCode, details: details || undefined })
      push(`${order.order_number} rejected.`, 'success')
      onChanged()
    } catch (err) {
      push(getErrorMessage(err), 'error')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
      <button
        onClick={toggle}
        className="w-full flex justify-between items-center px-5 py-4 text-left hover:bg-slate-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="font-mono text-xs font-bold text-slate-800 bg-slate-100 px-2 py-1 rounded">
            {order.order_number}
          </span>
          <span className="text-sm text-slate-700">
            {order.items.length} item(s) — <strong className="text-slate-900">₹{Number(order.total).toFixed(2)}</strong>
          </span>
        </div>
        <div className="flex items-center gap-2">
          {stock && (
            <span
              className={`text-xs px-2.5 py-0.5 rounded-full font-medium ${
                stock.sufficient ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
              }`}
            >
              {stock.sufficient ? 'Stock Verified ✓' : 'Shortage Detected ⚠'}
            </span>
          )}
          <span className="text-slate-400 text-xs">{expanded ? '▲' : '▼'}</span>
        </div>
      </button>

      {expanded && (
        <div className="px-5 pb-5 space-y-4 border-t border-slate-100 pt-4 bg-slate-50/50">
          
          {/* Stock Level Verification Grid */}
          {!stock ? (
            <div className="text-sm text-slate-400 py-2">Querying database inventory levels…</div>
          ) : (
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider">Inventory Stock Verification</h4>
                <button
                  onClick={runStockCheck}
                  className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                >
                  Re-check Stock ↻
                </button>
              </div>

              <div className="border border-slate-200 rounded-lg overflow-hidden bg-white">
                <table className="w-full text-sm">
                  <thead className="text-slate-500 text-xs uppercase bg-slate-50 border-b border-slate-100">
                    <tr>
                      <th className="text-left px-4 py-2">Product</th>
                      <th className="text-left px-4 py-2">Requested</th>
                      <th className="text-left px-4 py-2">Available</th>
                      <th className="text-left px-4 py-2">Shortage</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {stock.items.map((i) => (
                      <tr key={i.product_id} className={i.shortage > 0 ? 'text-red-600 bg-red-50/30' : 'text-slate-700'}>
                        <td className="px-4 py-2 font-medium">{i.product_name}</td>
                        <td className="px-4 py-2">{i.requested}</td>
                        <td className="px-4 py-2">{i.available}</td>
                        <td className="px-4 py-2 font-semibold">{i.shortage > 0 ? `${i.shortage} units` : '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {stock.sufficient ? (
                <div className="text-xs font-semibold text-emerald-800 bg-emerald-50 border border-emerald-200 px-3 py-2 rounded-md">
                  ✓ Database stock check passed: Sufficient inventory is on hand to fulfill this order.
                </div>
              ) : (
                <div className="text-xs font-semibold text-red-800 bg-red-50 border border-red-200 px-3 py-2 rounded-md">
                  ⚠ Stock check failed: Requested quantity exceeds available units. Reject the order below.
                </div>
              )}
            </div>
          )}

          {/* Fulfillment & Invoice Generation Actions */}
          <div className="flex flex-wrap items-center gap-3 pt-2">
            <button
              onClick={handleGenerateInvoice}
              disabled={busy || (stock && !stock.sufficient) || !!invoice}
              className="px-5 py-2.5 bg-blue-600 text-white rounded-md text-sm font-semibold hover:bg-blue-700 disabled:opacity-40 transition-colors shadow-sm"
            >
              {busy ? 'Generating…' : invoice ? 'Invoice Generated ✓' : 'Confirm & Generate Invoice'}
            </button>
          </div>

          {/* Generated Invoice & Payment Console Panel */}
          {invoice && (
            <div className="p-4 bg-white border border-blue-200 rounded-lg shadow-sm space-y-3">
              <div className="flex justify-between items-center">
                <div>
                  <span className="text-xs font-bold text-blue-600 uppercase tracking-wider">ERP Invoice Created</span>
                  <div className="text-base font-bold text-slate-900">{invoice.invoice_number}</div>
                </div>
                <div className="text-right">
                  <div className="text-xs text-slate-400 uppercase">Total Amount</div>
                  <div className="text-base font-bold text-slate-900">₹{Number(invoice.total).toFixed(2)}</div>
                </div>
              </div>

              <div className="flex flex-wrap gap-2 pt-1">
                <button
                  onClick={handleViewPdf}
                  className="px-3.5 py-1.5 bg-slate-900 text-white text-xs font-semibold rounded-md hover:bg-slate-800"
                >
                  View / Download PDF 📄
                </button>
                {paymentLink && (
                  <button
                    onClick={copyPaymentLink}
                    className="px-3.5 py-1.5 bg-emerald-600 text-white text-xs font-semibold rounded-md hover:bg-emerald-700"
                  >
                    Copy Stripe Payment Link 💳
                  </button>
                )}
              </div>

              {paymentLink && (
                <div className="pt-2">
                  <label className="text-[11px] text-slate-500 font-medium block mb-1">
                    Direct Stripe Checkout Session URL (Copy/Paste):
                  </label>
                  <input
                    type="text"
                    readOnly
                    value={paymentLink}
                    className="w-full text-xs font-mono bg-slate-50 border border-slate-200 rounded px-2.5 py-1.5 text-slate-700 select-all"
                  />
                </div>
              )}
            </div>
          )}

          {/* Rejection Handling */}
          <div className="border-t border-slate-200 pt-3 flex flex-wrap gap-2 items-center">
            <span className="text-xs text-slate-500 font-medium">Or reject order:</span>
            <select
              value={reasonCode}
              onChange={(e) => setReasonCode(e.target.value)}
              className="px-3 py-1.5 border border-slate-300 rounded-md text-sm bg-white"
            >
              {REASON_CODES.map((c) => (
                <option key={c} value={c}>{c.replace(/_/g, ' ')}</option>
              ))}
            </select>
            {reasonCode !== 'INSUFFICIENT_STOCK' && (
              <input
                value={details}
                onChange={(e) => setDetails(e.target.value)}
                placeholder="Reason details required"
                className="flex-1 px-3 py-1.5 border border-slate-300 rounded-md text-sm bg-white"
              />
            )}
            <button
              onClick={reject}
              disabled={busy}
              className="px-4 py-1.5 bg-white border border-red-300 text-red-600 rounded-md text-sm font-medium hover:bg-red-50 disabled:opacity-40"
            >
              Reject Order
            </button>
          </div>

        </div>
      )}
    </div>
  )
}

export default function PendingOrders() {
  const [orders, setOrders] = useState(null)
  const [error, setError] = useState(null)

  const load = () => {
    setError(null)
    ordersApi.listOrders({ status: 'PENDING_WAREHOUSE' })
      .then(setOrders)
      .catch((err) => setError(getErrorMessage(err)))
  }

  useEffect(load, [])

  if (error) return <ErrorState message={error} onRetry={load} />
  if (!orders) return <LoadingState />

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Pending Orders & Fulfillment</h1>
        <p className="text-sm text-slate-500 mt-1">Verify stock availability and generate billing invoices for orders received from sales.</p>
      </div>

      {orders.length === 0 ? (
        <EmptyState message="No orders waiting for warehouse review." />
      ) : (
        <div className="space-y-3">
          {orders.map((o) => (
            <OrderRow key={o.id} order={o} onChanged={load} />
          ))}
        </div>
      )}
    </div>
  )
}
import { useEffect, useState } from 'react'
import * as ordersApi from '../../api/orders'
import LoadingState from '../../components/common/LoadingState'
import ErrorState from '../../components/common/ErrorState'
import EmptyState from '../../components/common/EmptyState'
import StatusBadge from '../../components/common/StatusBadge'
import { getErrorMessage } from '../../api/errorMessage'

function OrderRow({ order }) {
  const [expanded, setExpanded] = useState(false)
  const canExpand = order.status === 'REJECTED' && order.rejection

  return (
    <>
      <tr className={`border-t border-slate-50 ${canExpand ? 'cursor-pointer hover:bg-slate-50' : ''}`} onClick={() => canExpand && setExpanded((e) => !e)}>
        <td className="px-5 py-3 font-mono text-xs">{order.order_number}</td>
        <td className="px-5 py-3">{order.source}</td>
        <td className="px-5 py-3">{order.items.length}</td>
        <td className="px-5 py-3">₹{Number(order.total).toFixed(2)}</td>
        <td className="px-5 py-3"><StatusBadge status={order.status} /></td>
      </tr>
      {expanded && (
        <tr className="bg-red-50">
          <td colSpan={5} className="px-5 py-3 text-sm text-red-700">
            <div className="font-medium">Reason: {order.rejection.reason_code.replace(/_/g, ' ')}</div>
            <div className="text-red-600 mt-1">{order.rejection.details}</div>
            {order.rejection.ai_explanation && (
              <div className="mt-2 text-slate-600 bg-white rounded-md p-2 border border-red-100">
                <span className="text-xs uppercase text-slate-400">AI Explanation</span>
                <p>{order.rejection.ai_explanation}</p>
              </div>
            )}
          </td>
        </tr>
      )}
    </>
  )
}

export default function Orders() {
  const [orders, setOrders] = useState(null)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState('')

  const load = () => {
    setError(null)
    ordersApi.listOrders(filter ? { status: filter } : {}).then(setOrders).catch((err) => setError(getErrorMessage(err)))
  }

  useEffect(load, [filter])

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-900">Orders</h1>
      <div className="flex gap-2 flex-wrap">
        {['', 'PENDING_WAREHOUSE', 'CONFIRMED', 'REJECTED', 'INVOICED', 'COMPLETED'].map((s) => (
          <button key={s} onClick={() => setFilter(s)} className={`px-3 py-1.5 rounded-md text-sm ${filter === s ? 'bg-slate-900 text-white' : 'bg-white text-slate-600 hover:bg-slate-100'}`}>{s || 'All'}</button>
        ))}
      </div>
      {error && <ErrorState message={error} onRetry={load} />}
      {!error && !orders && <LoadingState />}
      {orders && orders.length === 0 && <EmptyState message="No orders found." />}
      {orders && orders.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-500 text-xs uppercase">
              <tr><th className="px-5 py-3 text-left">Order #</th><th className="px-5 py-3 text-left">Source</th><th className="px-5 py-3 text-left">Items</th><th className="px-5 py-3 text-left">Total</th><th className="px-5 py-3 text-left">Status</th></tr>
            </thead>
            <tbody>{orders.map((o) => <OrderRow key={o.id} order={o} />)}</tbody>
          </table>
        </div>
      )}
    </div>
  )
}
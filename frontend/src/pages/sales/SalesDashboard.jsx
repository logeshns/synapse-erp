import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import * as orderRequestsApi from '../../api/orderRequests'
import * as ordersApi from '../../api/orders'
import LoadingState from '../../components/common/LoadingState'
import ErrorState from '../../components/common/ErrorState'
import StatusBadge from '../../components/common/StatusBadge'
import { getErrorMessage } from '../../api/errorMessage'

export default function SalesDashboard() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  const load = () => {
    setError(null)
    setData(null)
    Promise.all([orderRequestsApi.listOrderRequests({ review_status: 'PENDING_REVIEW' }), ordersApi.listOrders()])
      .then(([pendingRequests, orders]) => setData({ pendingRequests, orders }))
      .catch((err) => setError(getErrorMessage(err)))
  }

  useEffect(load, [])

  if (error) return <ErrorState message={error} onRetry={load} />
  if (!data) return <LoadingState />

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-semibold text-slate-900">Sales Dashboard</h1>
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white rounded-lg p-5 shadow-sm"><div className="text-sm text-slate-500">Pending Order Requests</div><div className="text-3xl font-semibold text-slate-900">{data.pendingRequests.length}</div></div>
        <div className="bg-white rounded-lg p-5 shadow-sm"><div className="text-sm text-slate-500">Total Orders</div><div className="text-3xl font-semibold text-slate-900">{data.orders.length}</div></div>
        <div className="bg-white rounded-lg p-5 shadow-sm"><div className="text-sm text-slate-500">Awaiting Warehouse</div><div className="text-3xl font-semibold text-slate-900">{data.orders.filter((o) => o.status === 'PENDING_WAREHOUSE').length}</div></div>
      </div>
      <div className="bg-white rounded-lg shadow-sm">
        <div className="px-5 py-3 border-b border-slate-100 flex justify-between items-center">
          <h2 className="font-medium text-slate-900">Incoming Order Requests</h2>
          <Link to="/sales/order-requests" className="text-sm text-slate-500 hover:text-slate-900">View all →</Link>
        </div>
        {data.pendingRequests.length === 0 ? (
          <div className="p-5 text-sm text-slate-400">No pending order requests.</div>
        ) : (
          <table className="w-full text-sm">
            <tbody>
              {data.pendingRequests.slice(0, 5).map((r) => (
                <tr key={r.id} className="border-t border-slate-50">
                  <td className="px-5 py-3 font-mono text-xs text-slate-500">{r.request_number}</td>
                  <td className="px-5 py-3">{r.source}</td>
                  <td className="px-5 py-3">{r.raw_text?.slice(0, 60)}{r.raw_text?.length > 60 ? '…' : ''}</td>
                  <td className="px-5 py-3"><StatusBadge status={r.review_status} /></td>
                  <td className="px-5 py-3 text-right"><Link to={`/sales/order-requests/${r.id}`} className="text-slate-600 hover:text-slate-900 font-medium">Review →</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
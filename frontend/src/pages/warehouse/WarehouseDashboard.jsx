import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import * as ordersApi from '../../api/orders'
import * as inventoryApi from '../../api/inventory'
import LoadingState from '../../components/common/LoadingState'
import ErrorState from '../../components/common/ErrorState'
import { getErrorMessage } from '../../api/errorMessage'

export default function WarehouseDashboard() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  const load = () => {
    setError(null)
    setData(null)
    Promise.all([ordersApi.listOrders({ status: 'PENDING_WAREHOUSE' }), inventoryApi.listLowStock()])
      .then(([pending, lowStock]) => setData({ pending, lowStock }))
      .catch((err) => setError(getErrorMessage(err)))
  }

  useEffect(load, [])

  if (error) return <ErrorState message={error} onRetry={load} />
  if (!data) return <LoadingState />

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-semibold text-slate-900">Warehouse Dashboard</h1>
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white rounded-lg p-5 shadow-sm"><div className="text-sm text-slate-500">Pending Orders</div><div className="text-3xl font-semibold text-slate-900">{data.pending.length}</div></div>
        <div className="bg-white rounded-lg p-5 shadow-sm"><div className="text-sm text-slate-500">Low Stock Products</div><div className="text-3xl font-semibold text-amber-600">{data.lowStock.length}</div></div>
      </div>
      <div className="bg-white rounded-lg shadow-sm">
        <div className="px-5 py-3 border-b border-slate-100 flex justify-between items-center">
          <h2 className="font-medium text-slate-900">Pending Orders</h2>
          <Link to="/warehouse/pending-orders" className="text-sm text-slate-500 hover:text-slate-900">View all →</Link>
        </div>
        {data.pending.length === 0 ? <div className="p-5 text-sm text-slate-400">No orders waiting for warehouse review.</div> : (
          <table className="w-full text-sm"><tbody>{data.pending.slice(0, 5).map((o) => (
            <tr key={o.id} className="border-t border-slate-50">
              <td className="px-5 py-3 font-mono text-xs">{o.order_number}</td>
              <td className="px-5 py-3">{o.items.length} item(s)</td>
              <td className="px-5 py-3">₹{Number(o.total).toFixed(2)}</td>
              <td className="px-5 py-3 text-right"><Link to="/warehouse/pending-orders" className="text-slate-600 hover:text-slate-900 font-medium">Review →</Link></td>
            </tr>
          ))}</tbody></table>
        )}
      </div>
    </div>
  )
}
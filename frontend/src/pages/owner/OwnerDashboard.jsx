import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts'
import { IndianRupee, ShoppingBag, Boxes, Users, AlertTriangle, TrendingDown } from 'lucide-react'
import * as analyticsApi from '../../api/analytics'
import LoadingState from '../../components/common/LoadingState'
import ErrorState from '../../components/common/ErrorState'
import Card from '../../components/common/Card'
import PageHeader from '../../components/common/PageHeader'
import { getErrorMessage } from '../../api/errorMessage'

const CHART_COLORS = ['#7c3aed', '#a78bfa', '#c4b5fd', '#ede9fe']

function Kpi({ icon: Icon, label, value, sub, tone = 'default' }) {
  const toneText = { default: 'text-slate-900', amber: 'text-amber-600', red: 'text-red-600', brand: 'text-brand-600' }
  const iconBg = { default: 'bg-slate-100 text-slate-500', amber: 'bg-amber-50 text-amber-600', red: 'bg-red-50 text-red-600', brand: 'bg-brand-50 text-brand-600' }
  return (
    <Card className="p-5" hover>
      <div className="flex items-start justify-between">
        <div>
          <div className="text-sm text-slate-500">{label}</div>
          <div className={`text-2xl font-bold mt-1 ${toneText[tone]}`}>{value}</div>
          {sub && <div className="text-xs text-slate-400 mt-1">{sub}</div>}
        </div>
        <div className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${iconBg[tone]}`}><Icon className="w-4.5 h-4.5" /></div>
      </div>
    </Card>
  )
}

export default function OwnerDashboard() {
  const [summary, setSummary] = useState(null)
  const [salesByProduct, setSalesByProduct] = useState(null)
  const [onlineOffline, setOnlineOffline] = useState(null)
  const [error, setError] = useState(null)

  const load = () => {
    setError(null); setSummary(null)
    Promise.all([analyticsApi.getSummary(30), analyticsApi.getSalesByProduct(30), analyticsApi.getOnlineOffline(30)])
      .then(([s, sbp, oo]) => { setSummary(s); setSalesByProduct(sbp); setOnlineOffline(oo) })
      .catch((err) => setError(getErrorMessage(err)))
  }

  useEffect(load, [])

  if (error) return <ErrorState message={error} onRetry={load} />
  if (!summary) return <LoadingState />

  const pieData = Object.entries(onlineOffline.by_source).map(([source, v]) => ({ name: source, value: v.orders }))
  const inr = (n) => `₹${Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`

  return (
    <div className="space-y-6">
      <PageHeader title="Owner Dashboard" subtitle="Executive overview — last 30 days" />
      <div className="grid grid-cols-4 gap-4">
        <Kpi icon={IndianRupee} label="Revenue (30d)" value={inr(summary.revenue.total_revenue)} tone="brand" />
        <Kpi icon={ShoppingBag} label="Orders (30d)" value={summary.orders.total} />
        <Kpi icon={Boxes} label="Inventory Value" value={inr(summary.inventory.total_value)} />
        <Kpi icon={Users} label="Active Customers" value={summary.customer_count} />
      </div>
      <div className="grid grid-cols-4 gap-4">
        <Kpi icon={AlertTriangle} label="Unpaid Invoices" value={inr(summary.outstanding_payments.UNPAID)} tone="amber" />
        <Kpi icon={AlertTriangle} label="Overdue Invoices" value={inr(summary.outstanding_payments.OVERDUE)} tone="red" />
        <Kpi icon={Boxes} label="Low Stock Products" value={summary.inventory.low_stock_count} tone="amber" />
        <Kpi icon={TrendingDown} label="Lost Revenue (stockouts)" value={inr(summary.lost_revenue.total_lost_value)} sub={summary.lost_revenue.top_affected_product ? `Top affected: ${summary.lost_revenue.top_affected_product}` : undefined} tone="red" />
      </div>
      <div className="grid grid-cols-2 gap-6">
        <Card className="p-5">
          <h2 className="font-semibold text-slate-900 mb-4">Top Selling Products</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={salesByProduct.slice(0, 6)}>
              <XAxis dataKey="product_name" tick={{ fontSize: 11, fill: '#64748b' }} interval={0} angle={-15} textAnchor="end" height={60} axisLine={{ stroke: '#e2e8f0' }} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
              <Tooltip cursor={{ fill: '#f8fafc' }} contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 13 }} />
              <Bar dataKey="units_sold" fill="#7c3aed" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
        <Card className="p-5">
          <h2 className="font-semibold text-slate-900 mb-4">Online vs Offline Orders</h2>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={55} outerRadius={90} paddingAngle={3}>
                {pieData.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
              </Pie>
              <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 13 }} />
              <Legend iconType="circle" wrapperStyle={{ fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </div>
    </div>
  )
}
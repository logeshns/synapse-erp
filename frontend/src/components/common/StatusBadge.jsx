const CONFIG = {
  PENDING_REVIEW: { c: 'text-amber-700 bg-amber-50 ring-amber-600/20', d: 'bg-amber-500' },
  APPROVED: { c: 'text-emerald-700 bg-emerald-50 ring-emerald-600/20', d: 'bg-emerald-500' },
  REJECTED: { c: 'text-red-700 bg-red-50 ring-red-600/20', d: 'bg-red-500' },
  PENDING_WAREHOUSE: { c: 'text-amber-700 bg-amber-50 ring-amber-600/20', d: 'bg-amber-500' },
  CONFIRMED: { c: 'text-emerald-700 bg-emerald-50 ring-emerald-600/20', d: 'bg-emerald-500' },
  INVOICED: { c: 'text-blue-700 bg-blue-50 ring-blue-600/20', d: 'bg-blue-500' },
  COMPLETED: { c: 'text-emerald-700 bg-emerald-50 ring-emerald-600/20', d: 'bg-emerald-500' },
  UNPAID: { c: 'text-amber-700 bg-amber-50 ring-amber-600/20', d: 'bg-amber-500' },
  PAID: { c: 'text-emerald-700 bg-emerald-50 ring-emerald-600/20', d: 'bg-emerald-500' },
  OVERDUE: { c: 'text-red-700 bg-red-50 ring-red-600/20', d: 'bg-red-500' },
  VOID: { c: 'text-slate-600 bg-slate-100 ring-slate-500/20', d: 'bg-slate-400' },
  SUCCESS: { c: 'text-emerald-700 bg-emerald-50 ring-emerald-600/20', d: 'bg-emerald-500' },
  NEEDS_REVIEW: { c: 'text-amber-700 bg-amber-50 ring-amber-600/20', d: 'bg-amber-500' },
  FAILED: { c: 'text-red-700 bg-red-50 ring-red-600/20', d: 'bg-red-500' },
  NOT_STARTED: { c: 'text-slate-600 bg-slate-100 ring-slate-500/20', d: 'bg-slate-400' },
}

export default function StatusBadge({ status }) {
  const cfg = CONFIG[status] || CONFIG.NOT_STARTED
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ring-1 ring-inset ${cfg.c}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${cfg.d}`} />
      {status?.replace(/_/g, ' ')}
    </span>
  )
}
import { useState } from 'react'

export default function ToolTrace({ trace }) {
  const [open, setOpen] = useState(false)
  if (!trace || trace.length === 0) return null

  return (
    <div className="mt-2 border border-slate-200 rounded-md text-xs">
      <button onClick={() => setOpen((o) => !o)} className="w-full text-left px-3 py-1.5 bg-slate-50 hover:bg-slate-100 rounded-md flex justify-between items-center text-slate-500">
        <span>AI Activity — {trace.length} tool call{trace.length !== 1 ? 's' : ''}</span>
        <span>{open ? '▲' : '▼'}</span>
      </button>
      {open && (
        <div className="p-3 space-y-2">
          {trace.map((t, i) => (
            <div key={i} className="border-l-2 border-slate-300 pl-2">
              <div className="font-mono text-slate-700">
                {t.result?.success === false ? '✕' : '✓'} {t.tool}({Object.entries(t.arguments || {}).map(([k, v]) => `${k}=${v}`).join(', ')})
              </div>
              <div className="text-slate-500">
                {t.result?.success === false ? `ERROR: ${t.result.error_code} — ${t.result.message}` : JSON.stringify(t.result?.result)}
              </div>
              <div className="text-slate-400">{t.latency_ms}ms</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
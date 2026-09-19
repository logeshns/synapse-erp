import { Inbox } from 'lucide-react'

export default function EmptyState({ message = 'Nothing here yet.' }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-3 text-center text-slate-400">
      <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center"><Inbox className="w-5 h-5" /></div>
      <p className="text-sm">{message}</p>
    </div>
  )
}
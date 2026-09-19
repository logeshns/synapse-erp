import { AlertTriangle } from 'lucide-react'
import Button from './Button'

export default function ErrorState({ message, onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-3 text-center">
      <div className="w-10 h-10 rounded-full bg-red-50 flex items-center justify-center"><AlertTriangle className="w-5 h-5 text-red-500" /></div>
      <p className="text-slate-600 text-sm max-w-sm">{message || 'Something went wrong.'}</p>
      {onRetry && <Button variant="secondary" onClick={onRetry}>Retry</Button>}
    </div>
  )
}
import { useState } from 'react'
import { Sparkles, Send } from 'lucide-react'
import ToolTrace from './ToolTrace'
import { getErrorMessage } from '../../api/errorMessage'

export default function AIChat({ onAsk, placeholder = 'Ask a question…', suggestions = [] }) {
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)

  const ask = async (q) => {
    const text = (q ?? question).trim()
    if (!text) return
    setQuestion('')
    setMessages((m) => [...m, { role: 'user', text }])
    setLoading(true)
    try {
      const result = await onAsk(text)
      setMessages((m) => [...m, {
        role: 'assistant',
        text: result.answer || (result.status === 'FAILED' ? 'The AI assistant is temporarily unavailable. Please try again.' : ''),
        trace: result.trace, failed: result.status === 'FAILED',
      }])
    } catch (err) {
      setMessages((m) => [...m, { role: 'assistant', text: getErrorMessage(err), failed: true }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="border border-slate-200/70 rounded-2xl bg-white shadow-soft flex flex-col h-[460px] overflow-hidden">
      <div className="flex items-center gap-2 px-4 py-3 bg-brand-gradient text-white">
        <Sparkles className="w-4 h-4" /><span className="text-sm font-medium">AI Assistant</span>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && suggestions.length > 0 && (
          <div className="space-y-2">
            <p className="text-sm text-slate-400">Try asking:</p>
            {suggestions.map((s) => (
              <button key={s} onClick={() => ask(s)} className="block text-left text-sm px-3.5 py-2.5 bg-slate-50 hover:bg-brand-50 hover:text-brand-700 rounded-lg w-full text-slate-600 transition-colors">{s}</button>
            ))}
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`max-w-[85%] ${m.role === 'user' ? 'ml-auto' : ''}`}>
            <div className={`px-3.5 py-2.5 rounded-xl text-sm ${m.role === 'user' ? 'bg-slate-900 text-white' : m.failed ? 'bg-red-50 text-red-700 border border-red-200' : 'bg-slate-100 text-slate-800'}`}>{m.text}</div>
            {m.trace && <ToolTrace trace={m.trace} />}
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-1.5 px-1">
            <span className="w-1.5 h-1.5 rounded-full bg-brand-400 animate-pulseSoft" />
            <span className="w-1.5 h-1.5 rounded-full bg-brand-400 animate-pulseSoft" style={{ animationDelay: '0.2s' }} />
            <span className="w-1.5 h-1.5 rounded-full bg-brand-400 animate-pulseSoft" style={{ animationDelay: '0.4s' }} />
          </div>
        )}
      </div>
      <form onSubmit={(e) => { e.preventDefault(); ask() }} className="border-t border-slate-100 p-3 flex gap-2">
        <input value={question} onChange={(e) => setQuestion(e.target.value)} placeholder={placeholder} className="flex-1 px-3.5 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent" />
        <button type="submit" disabled={loading} className="w-10 h-10 shrink-0 flex items-center justify-center bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50"><Send className="w-4 h-4" /></button>
      </form>
    </div>
  )
}
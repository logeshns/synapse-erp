import * as aiApi from '../../api/ai'
import AIChat from '../../components/ai/AIChat'

export default function BusinessAnalyst() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-900">Ask Your Business Anything</h1>
      <p className="text-sm text-slate-500">Grounded in live revenue, sales, and rejection data — every number comes from a real query, shown in the AI Activity trace below each answer.</p>
      <AIChat onAsk={aiApi.askBusinessAnalyst} placeholder="e.g. How much revenue did we lose due to stock shortages?" suggestions={['How much revenue did we generate this month?', 'Which product sold the most this month?', 'How much revenue did we lose due to stock shortages?', 'Compare online and offline sales.']} />
    </div>
  )
}
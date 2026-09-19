import * as aiApi from '../../api/ai'
import AIChat from '../../components/ai/AIChat'

export default function InventoryAssistant() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-900">AI Inventory Assistant</h1>
      <p className="text-sm text-slate-500">Ask about stock levels, low-stock products, or recent sales. Every answer is grounded in live database queries — expand "AI Activity" below any response to see exactly what was checked.</p>
      <AIChat onAsk={aiApi.askInventoryAssistant} placeholder="e.g. How many Dell laptops are in stock?" suggestions={['Which products are low in stock?', 'How many units of each product were sold in the last 30 days?', 'What is the total inventory value?']} />
    </div>
  )
}
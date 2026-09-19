import { useEffect, useState } from 'react'
import * as inventoryApi from '../../api/inventory'
import * as productsApi from '../../api/products'
import LoadingState from '../../components/common/LoadingState'
import ErrorState from '../../components/common/ErrorState'
import { getErrorMessage } from '../../api/errorMessage'
import { useToast } from '../../components/common/Toast'

export default function Inventory() {
  const { push } = useToast()
  const [items, setItems] = useState(null)
  const [error, setError] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ sku: '', name: '', category: '', unit_price: '', tax_rate: '0.18', initial_quantity: 0, reorder_point: 0 })
  const [submitting, setSubmitting] = useState(false)
  const [editing, setEditing] = useState(null)

  const load = () => {
    setError(null)
    inventoryApi.listInventory().then(setItems).catch((err) => setError(getErrorMessage(err)))
  }

  useEffect(load, [])

  const submitProduct = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await productsApi.createProduct({ ...form, unit_price: Number(form.unit_price), tax_rate: Number(form.tax_rate), initial_quantity: Number(form.initial_quantity), reorder_point: Number(form.reorder_point) })
      push('Product created.', 'success')
      setShowForm(false)
      setForm({ sku: '', name: '', category: '', unit_price: '', tax_rate: '0.18', initial_quantity: 0, reorder_point: 0 })
      load()
    } catch (err) {
      push(getErrorMessage(err), 'error')
    } finally {
      setSubmitting(false)
    }
  }

  const saveAdjust = async (productId, quantity, reorder) => {
    try {
      await inventoryApi.adjustInventory(productId, { quantity_on_hand: Number(quantity), reorder_point: Number(reorder) })
      push('Inventory updated.', 'success')
      setEditing(null)
      load()
    } catch (err) {
      push(getErrorMessage(err), 'error')
    }
  }

  if (error) return <ErrorState message={error} onRetry={load} />
  if (!items) return <LoadingState />

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-slate-900">Inventory</h1>
        <button onClick={() => setShowForm((s) => !s)} className="px-4 py-2 bg-slate-900 text-white rounded-md text-sm hover:bg-slate-800">+ New Product</button>
      </div>
      {showForm && (
        <form onSubmit={submitProduct} className="bg-white rounded-lg shadow-sm p-5 grid grid-cols-3 gap-3">
          <input required placeholder="SKU" value={form.sku} onChange={(e) => setForm((f) => ({ ...f, sku: e.target.value }))} className="px-3 py-2 border border-slate-300 rounded-md text-sm" />
          <input required placeholder="Name" value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} className="px-3 py-2 border border-slate-300 rounded-md text-sm" />
          <input placeholder="Category" value={form.category} onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))} className="px-3 py-2 border border-slate-300 rounded-md text-sm" />
          <input required type="number" step="0.01" placeholder="Unit Price" value={form.unit_price} onChange={(e) => setForm((f) => ({ ...f, unit_price: e.target.value }))} className="px-3 py-2 border border-slate-300 rounded-md text-sm" />
          <input type="number" placeholder="Initial Qty" value={form.initial_quantity} onChange={(e) => setForm((f) => ({ ...f, initial_quantity: e.target.value }))} className="px-3 py-2 border border-slate-300 rounded-md text-sm" />
          <input type="number" placeholder="Reorder Point" value={form.reorder_point} onChange={(e) => setForm((f) => ({ ...f, reorder_point: e.target.value }))} className="px-3 py-2 border border-slate-300 rounded-md text-sm" />
          <button type="submit" disabled={submitting} className="col-span-3 px-4 py-2 bg-slate-900 text-white rounded-md text-sm hover:bg-slate-800 disabled:opacity-50 w-fit">{submitting ? 'Saving…' : 'Save'}</button>
        </form>
      )}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-slate-500 text-xs uppercase"><tr><th className="px-5 py-3 text-left">SKU</th><th className="px-5 py-3 text-left">Product</th><th className="px-5 py-3 text-left">On Hand</th><th className="px-5 py-3 text-left">Reorder Point</th><th className="px-5 py-3"></th></tr></thead>
          <tbody>{items.map((i) => {
            const low = i.quantity_on_hand <= i.reorder_point
            const isEditing = editing?.product_id === i.product_id
            return (
              <tr key={i.product_id} className={`border-t border-slate-50 ${low ? 'bg-amber-50' : ''}`}>
                <td className="px-5 py-3 font-mono text-xs">{i.sku}</td>
                <td className="px-5 py-3">{i.product_name}</td>
                <td className="px-5 py-3">{isEditing ? <input type="number" value={editing.quantity_on_hand} onChange={(e) => setEditing((s) => ({ ...s, quantity_on_hand: e.target.value }))} className="w-20 px-2 py-1 border border-slate-300 rounded text-sm" /> : <span className={low ? 'text-amber-700 font-medium' : ''}>{i.quantity_on_hand}</span>}</td>
                <td className="px-5 py-3">{isEditing ? <input type="number" value={editing.reorder_point} onChange={(e) => setEditing((s) => ({ ...s, reorder_point: e.target.value }))} className="w-20 px-2 py-1 border border-slate-300 rounded text-sm" /> : i.reorder_point}</td>
                <td className="px-5 py-3 text-right">
                  {isEditing ? (
                    <div className="space-x-2"><button onClick={() => saveAdjust(i.product_id, editing.quantity_on_hand, editing.reorder_point)} className="text-emerald-600 hover:text-emerald-800 font-medium">Save</button><button onClick={() => setEditing(null)} className="text-slate-400 hover:text-slate-600">Cancel</button></div>
                  ) : (
                    <button onClick={() => setEditing({ product_id: i.product_id, quantity_on_hand: i.quantity_on_hand, reorder_point: i.reorder_point })} className="text-slate-600 hover:text-slate-900 font-medium">Adjust</button>
                  )}
                </td>
              </tr>
            )
          })}</tbody>
        </table>
      </div>
    </div>
  )
}
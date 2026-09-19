import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import * as orderRequestsApi from '../../api/orderRequests'
import * as customersApi from '../../api/customers'
import * as productsApi from '../../api/products'
import LoadingState from '../../components/common/LoadingState'
import ErrorState from '../../components/common/ErrorState'
import StatusBadge from '../../components/common/StatusBadge'
import { getErrorMessage } from '../../api/errorMessage'
import { useToast } from '../../components/common/Toast'

function emptyItem() {
  return { key: Math.random(), product_id: '', quantity: 1, hint: null }
}

export default function OrderRequestReview() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { push } = useToast()

  const [request, setRequest] = useState(null)
  const [customers, setCustomers] = useState([])
  const [products, setProducts] = useState([])
  const [error, setError] = useState(null)
  const [extracting, setExtracting] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [rejecting, setRejecting] = useState(false)

  const [customerData, setCustomerData] = useState({ id: '', name: '', email: '', phone: '', address: '' })
  const [items, setItems] = useState([emptyItem()])

  const applyExtraction = (req, prods = products, custs = customers) => {
    console.log("🎯 Raw Backend Data Received:", req.extracted_data);
    
    const raw = req.extracted_data || {};
    const res = raw.resolution || {};
    const rawExt = raw.raw_extraction || {};
    
    // Check all possible nested layers for Name, Phone, Email, Address
    let extName = res.customer_name || res.name || res.customer?.name || res.customer?.matched_name || 
                  rawExt.customer_name || rawExt.name || rawExt.customer?.name || raw.customer_name || '';
    if (typeof extName === 'object') extName = extName.name || extName.matched_name || '';

    let extPhone = res.phone || res.contact_number || res.customer?.phone || 
                   rawExt.phone || raw.phone || '';

    let extEmail = res.email || res.customer?.email || 
                   rawExt.email || raw.email || '';

    let extAddr = res.address || res.shipping_address || res.location || res.customer?.address || 
                  rawExt.address || raw.address || '';

    // Smart Text Fallbacks if AI left any field blank
    const text = req.raw_text || '';
    if (!extName) {
      const nameMatch = text.match(/^([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)/);
      if (nameMatch) extName = nameMatch[1];
    }
    if (!extPhone) {
      const phoneMatch = text.match(/\b\d{10}\b/);
      if (phoneMatch) extPhone = phoneMatch[0];
    }
    if (!extAddr) {
      const addrMatch = text.match(/(?:from|at|in)\s+([a-zA-Z0-9\s,]+?)(?=\swith|\s campus|\s office|\.|$)/i);
      if (addrMatch) extAddr = addrMatch[1].trim();
    }

    let matchedCustId = res.customer?.customer_id || '';
    if (!matchedCustId && extName) {
      const existing = custs.find(c => c.name.toLowerCase() === extName.toLowerCase());
      if (existing) matchedCustId = existing.id;
    }

    setCustomerData({
      id: matchedCustId,
      name: extName,
      email: extEmail,
      phone: extPhone,
      address: extAddr
    });

    let rawItems = res.items || [];
    if (rawItems.length > 0) {
      const mappedItems = rawItems.map((it) => ({
        key: Math.random(),
        product_id: it.status === 'MATCHED' ? String(it.product_id) : '',
        quantity: it.quantity || 1,
        hint:
          it.status === 'MATCHED'
            ? null
            : it.status === 'AMBIGUOUS'
              ? `AI found "${it.query}" — multiple matching products, please pick one`
              : it.status === 'NOT_FOUND'
                ? `AI found "${it.query}" — no matching product, please pick one`
                : null,
      }));
      setItems(mappedItems);
    }
  }

  const load = () => {
    setError(null)
    Promise.all([orderRequestsApi.getOrderRequest(id), customersApi.listCustomers(), productsApi.listProducts()])
      .then(([req, custs, prods]) => {
        setRequest(req)
        setCustomers(custs)
        setProducts(prods)
        applyExtraction(req, prods, custs)
      })
      .catch((err) => setError(getErrorMessage(err)))
  }

  useEffect(load, [id])

  const handleExtract = async () => {
    setExtracting(true)
    try {
      const updated = await orderRequestsApi.extractOrderRequest(id)
      setRequest(updated)
      applyExtraction(updated, products, customers)
      push(updated.ai_status === 'FAILED' ? 'AI extraction failed.' : 'AI seamlessly extracted all data.', updated.ai_status === 'FAILED' ? 'error' : 'success')
    } catch (err) {
      push(getErrorMessage(err), 'error')
    } finally {
      setExtracting(false)
    }
  }

  const updateItem = (key, patch) => setItems((its) => its.map((it) => (it.key === key ? { ...it, ...patch } : it)))
  const addItem = () => setItems((its) => [...its, emptyItem()])
  const removeItem = (key) => setItems((its) => its.filter((it) => it.key !== key))

  const handleApprove = async (e) => {
    e.preventDefault()
    if (!customerData.name) return push('Customer name was not extracted.', 'error')
    
    const validItems = items.filter((it) => it.quantity > 0);
    const unresolvedItems = validItems.filter((it) => !it.product_id);
    
    if (unresolvedItems.length > 0) {
      return push(`${unresolvedItems.length} item(s) still need a product selected before you can approve this order.`, 'error');
    }
    if (validItems.length === 0) return push('Add at least one item.', 'error');

    setSubmitting(true)
    try {
      let finalCustId = customerData.id;

      if (!finalCustId) {
        const custPayload = { name: customerData.name };
        if (customerData.email?.trim()) custPayload.email = customerData.email.trim();
        if (customerData.phone?.trim()) custPayload.phone = customerData.phone.trim();
        if (customerData.address?.trim()) custPayload.address = customerData.address.trim();

        const newCust = await customersApi.createCustomer(custPayload);
        finalCustId = newCust.id;
      }

      const mappedPayloadItems = validItems.map((it) => ({
        product_id: Number(it.product_id),
        quantity: Number(it.quantity),
      }));

      await orderRequestsApi.approveOrderRequest(id, {
        customer_id: Number(finalCustId),
        items: mappedPayloadItems,
      })
      
      push('Customer details saved & Order sent to warehouse!', 'success')
      navigate('/sales/order-requests')
    } catch (err) {
      push(getErrorMessage(err), 'error')
      setSubmitting(false)
    }
  }

  const handleReject = async () => {
    const reason = window.prompt('Reason for rejecting this request:')
    if (!reason) return
    setRejecting(true)
    try {
      await orderRequestsApi.rejectOrderRequest(id, { reason })
      push('Order request rejected.', 'success')
      navigate('/sales/order-requests')
    } catch (err) {
      push(getErrorMessage(err), 'error')
    } finally {
      setRejecting(false)
    }
  }

  if (error) return <ErrorState message={error} onRetry={load} />
  if (!request) return <LoadingState />

  const isDecided = request.review_status !== 'PENDING_REVIEW'

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">{request.request_number}</h1>
          <div className="mt-1 flex gap-2">
            <StatusBadge status={request.source} />
            <StatusBadge status={request.review_status} />
            <StatusBadge status={request.ai_status} />
          </div>
        </div>
        {!isDecided && (
          <button onClick={handleExtract} disabled={extracting || !request.raw_text} className="px-5 py-2.5 bg-slate-900 text-white rounded-xl text-sm font-semibold hover:bg-slate-800 disabled:opacity-50 transition-colors shadow-sm">
            {extracting ? 'Extracting via AI...' : request.ai_status === 'NOT_STARTED' ? 'Extract Order' : 'Re-extract via AI'}
          </button>
        )}
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl shadow-sm p-6 border border-slate-200">
          <h2 className="font-semibold text-slate-900 mb-4 flex items-center space-x-2">
            <span>Raw Request</span>
          </h2>
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 h-[calc(100%-3rem)]">
            <p className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">{request.raw_text || '(no raw text)'}</p>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-sm p-6 border border-slate-200">
          <h2 className="font-semibold text-slate-900 mb-5 flex items-center space-x-2">
            <span>AI-Extracted Order Form</span>
            {request.extracted_data && <span className="bg-emerald-100 text-emerald-800 text-[10px] uppercase font-bold px-2 py-0.5 rounded-full">Automated</span>}
          </h2>
          
          <form onSubmit={handleApprove} className="space-y-6">
            
            <div className="space-y-3 bg-blue-50/50 p-4 rounded-xl border border-blue-100">
              <h3 className="text-xs font-bold text-blue-800 uppercase tracking-wider">Customer Details</h3>
              <div className="grid grid-cols-2 gap-3">
                <input required placeholder="Customer Name" value={customerData.name} onChange={(e) => setCustomerData(c => ({...c, name: e.target.value}))} disabled={isDecided} className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500 bg-white" />
                <input placeholder="Phone (Optional)" value={customerData.phone} onChange={(e) => setCustomerData(c => ({...c, phone: e.target.value}))} disabled={isDecided} className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500 bg-white" />
                <input type="email" placeholder="Email (Optional)" value={customerData.email} onChange={(e) => setCustomerData(c => ({...c, email: e.target.value}))} disabled={isDecided} className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500 bg-white" />
                <input placeholder="Address" value={customerData.address} onChange={(e) => setCustomerData(c => ({...c, address: e.target.value}))} disabled={isDecided} className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500 bg-white" />
              </div>
            </div>

            <div className="space-y-3">
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider block">Extracted Line Items</h3>
              {items.map((it) => (
                <div key={it.key} className="space-y-1">
                  <div className="flex gap-2">
                    <select
                      value={it.product_id}
                      onChange={(e) => updateItem(it.key, { product_id: e.target.value })}
                      disabled={isDecided}
                      className={`flex-1 px-3.5 py-2.5 border rounded-xl text-sm focus:ring-2 focus:ring-blue-500 outline-none bg-white ${it.hint ? 'border-amber-400 bg-amber-50' : 'border-slate-300'}`}
                    >
                      <option value="">Select a product…</option>
                      {products.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
                    </select>
                    <input
                      type="number" min="1" value={it.quantity}
                      onChange={(e) => updateItem(it.key, { quantity: e.target.value })}
                      disabled={isDecided}
                      className="w-24 px-3.5 py-2.5 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 outline-none font-semibold text-center"
                    />
                    {!isDecided && <button type="button" onClick={() => removeItem(it.key)} className="px-2 text-slate-400 hover:text-red-500">✕</button>}
                  </div>
                  {it.hint && <p className="text-xs text-amber-600">Needs verification — {it.hint}</p>}
                </div>
              ))}
              {!isDecided && <button type="button" onClick={addItem} className="text-sm font-semibold text-blue-600 hover:text-blue-800 transition-colors">+ Add Line Item</button>}
            </div>

            {!isDecided ? (
              <div className="flex gap-3 pt-4 border-t border-slate-100">
                <button type="submit" disabled={submitting} className="px-5 py-2.5 bg-emerald-600 text-white rounded-xl text-sm font-bold hover:bg-emerald-700 disabled:opacity-50 transition-colors shadow-sm">
                  {submitting ? 'Creating...' : 'Approve & Create Order'}
                </button>
                <button type="button" onClick={handleReject} disabled={rejecting} className="px-5 py-2.5 bg-white border border-red-200 text-red-600 rounded-xl text-sm font-bold hover:bg-red-50 disabled:opacity-50 transition-colors shadow-sm">
                  Reject
                </button>
              </div>
            ) : (
              <div className="pt-4 border-t border-slate-100">
                <p className="text-sm font-medium text-slate-500 bg-slate-50 inline-block px-3 py-1.5 rounded-lg border border-slate-200">
                  This request has been successfully {request.review_status.toLowerCase()}.
                </p>
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  )
}
import client from './client'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const listInvoices = (params) => client.get('/invoices', { params }).then((r) => r.data)
export const generateInvoice = (orderId) => client.post(`/invoices/generate/${orderId}`).then((r) => r.data)

export const openInvoicePdf = async (id) => {
  const response = await client.get(`/invoices/${id}/pdf`, { responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
  window.open(url, '_blank')
}
import client from './client'

export const generateReceipt = (paymentId) => client.post(`/receipts/generate/${paymentId}`).then((r) => r.data)

export const openReceiptPdf = async (id) => {
  const response = await client.get(`/receipts/${id}/pdf`, { responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
  window.open(url, '_blank')
}
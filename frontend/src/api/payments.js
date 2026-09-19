import client from './client'

export const listPayments = (params) => client.get('/payments', { params }).then((r) => r.data)
export const createCheckout = (invoiceId) => client.post(`/payments/create-checkout/${invoiceId}`).then((r) => r.data)
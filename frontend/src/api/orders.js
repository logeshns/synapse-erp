import client from './client'

export const listOrders = (params) => client.get('/orders', { params }).then((r) => r.data)
export const stockCheck = (id) => client.get(`/orders/${id}/stock-check`).then((r) => r.data)
export const confirmOrder = (id) => client.post(`/orders/${id}/confirm`).then((r) => r.data)
export const rejectOrder = (id, payload) => client.post(`/orders/${id}/reject`, payload).then((r) => r.data)
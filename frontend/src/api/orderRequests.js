import client from './client'

export const listOrderRequests = (params) => client.get('/order-requests', { params }).then((r) => r.data)
export const getOrderRequest = (id) => client.get(`/order-requests/${id}`).then((r) => r.data)
export const createOrderRequest = (payload) => client.post('/order-requests', payload).then((r) => r.data)
export const extractOrderRequest = (id) => client.post(`/order-requests/${id}/extract`).then((r) => r.data)
export const approveOrderRequest = (id, payload) => client.post(`/order-requests/${id}/approve`, payload).then((r) => r.data)
export const rejectOrderRequest = (id, payload) => client.post(`/order-requests/${id}/reject`, payload).then((r) => r.data)
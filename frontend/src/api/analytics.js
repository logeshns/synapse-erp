import client from './client'

export const getSummary = (days = 30) => client.get('/analytics/summary', { params: { days } }).then((r) => r.data)
export const getSalesByProduct = (days = 30) => client.get('/analytics/sales-by-product', { params: { days } }).then((r) => r.data)
export const getOnlineOffline = (days = 30) => client.get('/analytics/online-offline', { params: { days } }).then((r) => r.data)
import client from './client'

export const listInventory = () => client.get('/inventory').then((r) => r.data)
export const listLowStock = () => client.get('/inventory/low-stock').then((r) => r.data)
export const adjustInventory = (productId, payload) => client.patch(`/inventory/${productId}`, payload).then((r) => r.data)
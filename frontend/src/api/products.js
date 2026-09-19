import client from './client'

export const listProducts = () => client.get('/products').then((r) => r.data)
export const createProduct = (payload) => client.post('/products', payload).then((r) => r.data)
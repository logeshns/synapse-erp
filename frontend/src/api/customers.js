import client from './client'

export const listCustomers = () => client.get('/customers').then((r) => r.data)
export const createCustomer = (payload) => client.post('/customers', payload).then((r) => r.data)
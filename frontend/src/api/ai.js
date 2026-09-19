import client from './client'

export const askInventoryAssistant = (question) => client.post('/ai/inventory/ask', { question }).then((r) => r.data)
export const askBusinessAnalyst = (question) => client.post('/ai/business-analyst/ask', { question }).then((r) => r.data)
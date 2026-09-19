import client from './client'

export const getTeamOverview = (days = 30) => client.get('/manager/team', { params: { days } }).then((r) => r.data)
export const addRating = (payload) => client.post('/manager/ratings', payload).then((r) => r.data)
import { createContext, useContext, useEffect, useState } from 'react'
import * as authApi from '../api/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('synapse_user')
    return stored ? JSON.parse(stored) : null
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('synapse_token')
    if (!token) {
      setLoading(false)
      return
    }
    authApi
      .getMe()
      .then((me) => {
        setUser(me)
        localStorage.setItem('synapse_user', JSON.stringify(me))
      })
      .catch(() => {
        localStorage.removeItem('synapse_token')
        localStorage.removeItem('synapse_user')
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [])

  const login = async (email, password) => {
    const { access_token, user: loggedInUser } = await authApi.login(email, password)
    localStorage.setItem('synapse_token', access_token)
    localStorage.setItem('synapse_user', JSON.stringify(loggedInUser))
    setUser(loggedInUser)
    return loggedInUser
  }

  const logout = () => {
    localStorage.removeItem('synapse_token')
    localStorage.removeItem('synapse_user')
    setUser(null)
  }

  return <AuthContext.Provider value={{ user, loading, login, logout }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Sparkles } from 'lucide-react'
import { useAuth } from '../auth/AuthContext'
import { getErrorMessage } from '../api/errorMessage'
import Button from '../components/common/Button'

const HOME_BY_ROLE = { 
  SALES: '/sales', 
  WAREHOUSE: '/warehouse', 
  ACCOUNTANT: '/accountant', 
  MANAGER: '/manager', 
  OWNER: '/owner' 
}

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const user = await login(email, password)
      navigate(HOME_BY_ROLE[user.role] || '/')
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-slate-50 px-4">
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200/70 p-8 w-full max-w-sm space-y-5">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-8 h-8 rounded-lg bg-slate-900 flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <span className="font-semibold text-slate-900">Synapse ERP</span>
        </div>
        <div>
          <h2 className="text-xl font-bold text-slate-900">Welcome back</h2>
          <p className="text-sm text-slate-500 mt-1">Sign in to your workspace</p>
        </div>
        {error && <div className="text-sm text-red-700 bg-red-50 border border-red-100 px-3 py-2 rounded-lg">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-xs font-medium text-slate-600">Email</label>
            <input 
              type="email" 
              value={email} 
              onChange={(e) => setEmail(e.target.value)} 
              required 
              className="mt-1.5 w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent bg-white" 
            />
          </div>
          <div>
            <label className="text-xs font-medium text-slate-600">Password</label>
            <input 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              required 
              className="mt-1.5 w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent bg-white" 
            />
          </div>
          <Button type="submit" disabled={loading} className="w-full justify-center bg-slate-900 hover:bg-slate-800 text-white font-bold py-2.5 rounded-lg transition-colors shadow-sm">
            {loading ? 'Signing in…' : 'Sign in'}
          </Button>
        </form>
        <p className="text-[11px] text-slate-400 text-center leading-relaxed pt-2 border-t border-slate-100">
          Demo: sales@demo.com · warehouse@demo.com · accountant@demo.com · manager@demo.com · owner@demo.com<br />Password: Demo@12345
        </p>
      </div>
    </div>
  )
}
import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from './AuthContext'

export default function RoleRoute({ allowedRoles }) {
  const { user } = useAuth()
  if (!user || !allowedRoles.includes(user.role)) return <Navigate to="/" replace />
  return <Outlet />
}
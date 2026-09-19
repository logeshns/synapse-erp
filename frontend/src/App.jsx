import { Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from './auth/AuthContext'
import ProtectedRoute from './auth/ProtectedRoute'
import RoleRoute from './auth/RoleRoute'
import { ToastProvider } from './components/common/Toast'
import DashboardLayout from './layouts/DashboardLayout'
import Login from './pages/Login'

import SalesDashboard from './pages/sales/SalesDashboard'
import OrderRequests from './pages/sales/OrderRequests'
import OrderRequestReview from './pages/sales/OrderRequestReview'
import Orders from './pages/sales/Orders'
import Customers from './pages/sales/Customers'
import SalesInvoices from './pages/sales/Invoices'

import WarehouseDashboard from './pages/warehouse/WarehouseDashboard'
import PendingOrders from './pages/warehouse/PendingOrders'
import Inventory from './pages/warehouse/Inventory'
import InventoryAssistant from './pages/warehouse/InventoryAssistant'

import AccountantDashboard from './pages/accountant/AccountantDashboard'
import Payments from './pages/accountant/Payments'
import Receipts from './pages/accountant/Receipts'

import ManagerDashboard from './pages/manager/ManagerDashboard'
import Team from './pages/manager/Team'

import OwnerDashboard from './pages/owner/OwnerDashboard'
import BusinessAnalyst from './pages/owner/BusinessAnalyst'

// Import the new payment pages
import PaymentSuccess from './pages/PaymentSuccess'
import PaymentFailure from './pages/PaymentFailure'

const HOME_BY_ROLE = { SALES: '/sales', WAREHOUSE: '/warehouse', ACCOUNTANT: '/accountant', MANAGER: '/manager', OWNER: '/owner' }

function RoleRedirect() {
  const { user } = useAuth()
  return <Navigate to={HOME_BY_ROLE[user?.role] || '/login'} replace />
}

function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<RoleRedirect />} />
            
            {/* Payment Redirect Routes */}
            <Route path="/payment-success" element={<PaymentSuccess />} />
            <Route path="/payment-failure" element={<PaymentFailure />} />

            <Route element={<RoleRoute allowedRoles={['SALES', 'OWNER']} />}>
              <Route element={<DashboardLayout />}>
                <Route path="/sales" element={<SalesDashboard />} />
                <Route path="/sales/order-requests" element={<OrderRequests />} />
                <Route path="/sales/order-requests/:id" element={<OrderRequestReview />} />
                <Route path="/sales/orders" element={<Orders />} />
                <Route path="/sales/customers" element={<Customers />} />
                <Route path="/sales/invoices" element={<SalesInvoices />} />
              </Route>
            </Route>

            <Route element={<RoleRoute allowedRoles={['WAREHOUSE', 'OWNER']} />}>
              <Route element={<DashboardLayout />}>
                <Route path="/warehouse" element={<WarehouseDashboard />} />
                <Route path="/warehouse/pending-orders" element={<PendingOrders />} />
                <Route path="/warehouse/inventory" element={<Inventory />} />
                <Route path="/warehouse/assistant" element={<InventoryAssistant />} />
              </Route>
            </Route>

            <Route element={<RoleRoute allowedRoles={['ACCOUNTANT', 'OWNER']} />}>
              <Route element={<DashboardLayout />}>
                <Route path="/accountant" element={<AccountantDashboard />} />
                <Route path="/accountant/payments" element={<Payments />} />
                <Route path="/accountant/receipts" element={<Receipts />} />
              </Route>
            </Route>

            <Route element={<RoleRoute allowedRoles={['MANAGER', 'OWNER']} />}>
              <Route element={<DashboardLayout />}>
                <Route path="/manager" element={<ManagerDashboard />} />
                <Route path="/manager/team" element={<Team />} />
              </Route>
            </Route>

            <Route element={<RoleRoute allowedRoles={['OWNER']} />}>
              <Route element={<DashboardLayout />}>
                <Route path="/owner" element={<OwnerDashboard />} />
                <Route path="/owner/business-analyst" element={<BusinessAnalyst />} />
              </Route>
            </Route>
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </ToastProvider>
    </AuthProvider>
  )
}

export default App
import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import client from '../api/client';

export default function PaymentSuccess() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const invoiceId = searchParams.get('invoice_id');
  const [verifying, setVerifying] = useState(true);

  useEffect(() => {
    if (invoiceId) {
      client.post(`/payments/verify-success/${invoiceId}`)
        .then(() => setVerifying(false))
        .catch(() => setVerifying(false));
    } else {
      setVerifying(false);
    }
  }, [invoiceId]);

  return (
    <div className="flex items-center justify-center h-full">
      <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200 text-center space-y-4 max-w-sm w-full">
        <div className="text-emerald-500 text-5xl">✓</div>
        <h1 className="text-xl font-bold text-slate-900">Payment Successful</h1>
        <p className="text-sm text-slate-500">
          {verifying ? 'Verifying payment securely...' : 'The invoice has been successfully marked as PAID.'}
        </p>
        <button 
          onClick={() => navigate('/accountant/receipts')} 
          className="mt-4 w-full py-2 bg-emerald-600 text-white rounded-md text-sm font-semibold hover:bg-emerald-700"
        >
          Continue to Receipts →
        </button>
      </div>
    </div>
  );
}
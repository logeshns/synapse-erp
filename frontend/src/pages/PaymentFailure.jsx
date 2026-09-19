import { useNavigate } from 'react-router-dom';

export default function PaymentFailure() {
  const navigate = useNavigate();

  return (
    <div className="flex items-center justify-center h-full">
      <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200 text-center space-y-4 max-w-sm w-full">
        <div className="text-red-500 text-5xl">✕</div>
        <h1 className="text-xl font-bold text-slate-900">Payment Failed</h1>
        <p className="text-sm text-slate-500">
          The checkout session was canceled or the payment failed.
        </p>
        <button 
          onClick={() => navigate(-1)} 
          className="mt-4 w-full py-2 bg-slate-900 text-white rounded-md text-sm font-semibold hover:bg-slate-800"
        >
          Go Back
        </button>
      </div>
    </div>
  );
}
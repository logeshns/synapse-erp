const VARIANTS = {
  primary: 'bg-brand-600 text-white hover:bg-brand-700 shadow-soft',
  dark: 'bg-slate-900 text-white hover:bg-slate-800',
  secondary: 'bg-white text-slate-700 border border-slate-300 hover:bg-slate-50',
  danger: 'bg-white text-red-600 border border-red-300 hover:bg-red-50',
  success: 'bg-emerald-600 text-white hover:bg-emerald-700',
  ghost: 'text-slate-500 hover:text-slate-900 hover:bg-slate-100',
}

export default function Button({ variant = 'primary', className = '', children, ...props }) {
  return (
    <button
      className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${VARIANTS[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}
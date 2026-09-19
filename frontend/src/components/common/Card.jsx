export default function Card({ children, className = '', hover = false, ...props }) {
  return (
    <div className={`bg-white rounded-xl border border-slate-200/70 shadow-soft ${hover ? 'transition-shadow hover:shadow-card-hover' : ''} ${className}`} {...props}>
      {children}
    </div>
  )
}
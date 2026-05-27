import { useState } from 'react'

export default function DisclosureSection({
  title,
  eyebrow,
  summary,
  children,
  defaultOpen = false,
}) {
  const [open, setOpen] = useState(defaultOpen)

  return (
    <section style={{
      background: '#FFFFFF',
      border: '0.5px solid #E5E7EB',
      borderRadius: 12,
      overflow: 'hidden',
    }}>
      <button
        type="button"
        onClick={() => setOpen(v => !v)}
        aria-expanded={open}
        style={{
          width: '100%',
          display: 'grid',
          gridTemplateColumns: '1fr auto',
          gap: 14,
          alignItems: 'center',
          textAlign: 'left',
          padding: '18px 22px',
          background: open ? '#F8FAFC' : '#FFFFFF',
          border: 'none',
          borderBottom: open ? '0.5px solid #E5E7EB' : 'none',
          cursor: 'pointer',
          fontFamily: 'inherit',
        }}
      >
        <span>
          {eyebrow && (
            <span style={{
              display: 'block',
              fontSize: 11,
              fontWeight: 700,
              color: '#185FA5',
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              marginBottom: 5,
            }}>
              {eyebrow}
            </span>
          )}
          <span style={{
            display: 'block',
            fontSize: 15,
            fontWeight: 800,
            color: '#111827',
            lineHeight: 1.25,
          }}>
            {title}
          </span>
          {summary && (
            <span style={{
              display: 'block',
              fontSize: 12,
              color: '#6B7280',
              lineHeight: 1.45,
              marginTop: 5,
              maxWidth: 720,
            }}>
              {summary}
            </span>
          )}
        </span>
        <span style={{
          width: 28,
          height: 28,
          borderRadius: 999,
          border: '0.5px solid #D1D5DB',
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#374151',
          fontSize: 18,
          lineHeight: 1,
          flexShrink: 0,
        }}>
          {open ? '-' : '+'}
        </span>
      </button>

      {open && (
        <div style={{ padding: '20px 24px' }}>
          {children}
        </div>
      )}
    </section>
  )
}

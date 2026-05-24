export default function SensitivityTable({ sensitivity, currentPrice }) {
  const { rows, cols, values, closest_row, closest_col } = sensitivity

  const cellColor = (v) => {
    if (v == null) return { bg: '#F9FAFB', text: '#9CA3AF' }
    const diff = (v - currentPrice) / currentPrice
    if (diff > 0.08)  return { bg: '#EAF3DE', text: '#3B6D11' }
    if (diff > 0.02)  return { bg: '#F0F9E8', text: '#4A7E1C' }
    if (diff < -0.08) return { bg: '#FCEBEB', text: '#A32D2D' }
    if (diff < -0.02) return { bg: '#FEF2F2', text: '#C23B3B' }
    return { bg: '#FEFCE8', text: '#854D0E' }
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
        <thead>
          <tr>
            <th style={{ padding: '8px 10px', textAlign: 'left', color: '#6B7280', fontWeight: 600, borderBottom: '0.5px solid #E5E7EB', whiteSpace: 'nowrap' }}>
              FCF Growth ↓ · WACC →
            </th>
            {cols.map(c => (
              <th key={c} style={{ padding: '8px 10px', textAlign: 'center', color: '#6B7280', fontWeight: 600, borderBottom: '0.5px solid #E5E7EB', whiteSpace: 'nowrap' }}>
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, ri) => (
            <tr key={ri}>
              <td style={{ padding: '7px 10px', color: '#6B7280', fontWeight: 600, borderBottom: '0.5px solid #F3F4F6', whiteSpace: 'nowrap' }}>
                {row}
              </td>
              {cols.map((col, ci) => {
                const v = values[ri]?.[ci]
                const c = cellColor(v)
                const isClosest = ri === closest_row && ci === closest_col
                return (
                  <td
                    key={ci}
                    style={{
                      padding: '7px 10px',
                      textAlign: 'center',
                      background: c.bg,
                      color: c.text,
                      fontWeight: isClosest ? 700 : 500,
                      border: isClosest ? '2px solid #F59E0B' : '0.5px solid #F3F4F6',
                      borderRadius: isClosest ? 4 : 0,
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {v != null ? `$${v.toFixed(0)}` : '—'}
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
      <div style={{ marginTop: 10, display: 'flex', gap: 16, flexWrap: 'wrap' }}>
        {[
          { bg: '#EAF3DE', text: '#3B6D11', label: 'Above today\'s price' },
          { bg: '#FCEBEB', text: '#A32D2D', label: 'Below today\'s price' },
          { bg: '#FEFCE8', text: '#854D0E', label: 'Near today\'s price' },
        ].map(({ bg, text, label }) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{ width: 12, height: 12, borderRadius: 3, background: bg, border: `0.5px solid ${text}` }} />
            <span style={{ fontSize: 11, color: '#6B7280' }}>{label}</span>
          </div>
        ))}
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div style={{ width: 12, height: 12, borderRadius: 3, border: '2px solid #F59E0B' }} />
          <span style={{ fontSize: 11, color: '#6B7280' }}>Closest to today's price</span>
        </div>
      </div>
      <div style={{ marginTop: 8, fontSize: 12, color: '#6B7280' }}>
        The amber-bordered cell ({rows[closest_row]} growth, {cols[closest_col]} WACC) is the combination closest to today's price of ${currentPrice.toFixed(2)}.
      </div>
    </div>
  )
}

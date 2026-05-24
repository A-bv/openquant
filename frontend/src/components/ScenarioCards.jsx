const pct = (v, sign = true) => {
  if (v == null) return '—'
  const s = sign && v > 0 ? '+' : ''
  return `${s}${(v * 100).toFixed(1)}%`
}
const usd = v => v == null ? '—' : `$${v.toFixed(2)}`

const configs = {
  conservative: {
    label: 'Conservative',
    accent: '#A32D2D',
    bg: '#FCEBEB',
    borderColor: '#F5B5B5',
    description: 'FCF grows at 70% of historical median — pessimistic case',
  },
  base: {
    label: 'Base',
    accent: '#185FA5',
    bg: '#E6F1FB',
    borderColor: '#93C5FD',
    description: 'FCF continues at historical median — central case',
  },
  optimistic: {
    label: 'Optimistic',
    accent: '#3B6D11',
    bg: '#EAF3DE',
    borderColor: '#B5D98A',
    description: 'FCF grows at 130% of historical median — optimistic case',
  },
}

function ScenarioCard({ name, scenario, currentPrice }) {
  const cfg = configs[name]
  const above = scenario.iv > currentPrice
  return (
    <div style={{
      flex: 1,
      minWidth: 0,
      background: '#FFFFFF',
      border: `0.5px solid ${cfg.borderColor}`,
      borderRadius: 12,
      padding: '20px 22px',
      display: 'flex',
      flexDirection: 'column',
      gap: 12,
    }}>
      <div style={{ fontSize: 10, fontWeight: 700, color: cfg.accent, textTransform: 'uppercase', letterSpacing: '0.07em' }}>
        {cfg.label}
      </div>
      <div>
        <div style={{ fontSize: 28, fontWeight: 700, color: cfg.accent, lineHeight: 1 }}>
          {usd(scenario.iv)}
        </div>
        <div style={{
          marginTop: 6,
          display: 'inline-block',
          fontSize: 12,
          fontWeight: 600,
          color: above ? '#3B6D11' : '#A32D2D',
          background: above ? '#EAF3DE' : '#FCEBEB',
          borderRadius: 4,
          padding: '2px 8px',
        }}>
          {pct(scenario.upside)} vs current price
        </div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12 }}>
          <span style={{ color: '#6B7280' }}>FCF growth assumed</span>
          <span style={{ color: '#111827', fontWeight: 600 }}>{pct(scenario.growth, false)}</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12 }}>
          <span style={{ color: '#6B7280' }}>Terminal value share</span>
          <span style={{ color: '#111827', fontWeight: 600 }}>{pct(scenario.tv_pct, false)}</span>
        </div>
      </div>
      <div style={{ fontSize: 11, color: '#9CA3AF', lineHeight: 1.4 }}>
        {cfg.description}
      </div>
    </div>
  )
}

export default function ScenarioCards({ dcf, currentPrice }) {
  return (
    <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
      {['conservative', 'base', 'optimistic'].map(name => (
        <ScenarioCard key={name} name={name} scenario={dcf[name]} currentPrice={currentPrice} />
      ))}
    </div>
  )
}

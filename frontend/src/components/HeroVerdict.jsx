/**
 * Hero section — the page's "first impression."
 *
 * Top: company name, sector, price, market cap
 * Middle: BIG verdict sentence
 * Bottom: 5-dimension scorecard (Value, Implied growth, Track record, Balance sheet, Suitability)
 */

const fmt$ = v => v == null || !Number.isFinite(v) ? '—' : `$${v.toFixed(2)}`
const fmtMcap = v => {
  if (v == null || !Number.isFinite(v)) return '—'
  const b = v / 1e9
  if (b >= 1000) return `$${(b/1000).toFixed(1)}T`
  if (b >= 100)  return `$${b.toFixed(0)}B`
  return `$${b.toFixed(1)}B`
}
const pct = (v, d = 1) => v == null || !Number.isFinite(v) ? '—' : `${(v * 100).toFixed(d)}%`

function ScorecardDot({ rating, label, reason }) {
  const colour = rating === 'green' ? '#16A34A'
              : rating === 'amber' ? '#F59E0B'
              : rating === 'red'   ? '#DC2626'
              : '#9CA3AF'
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 4, flex: 1, minWidth: 100 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <div style={{ width: 10, height: 10, borderRadius: '50%', background: colour, flexShrink: 0 }} />
        <div style={{ fontSize: 11, fontWeight: 600, color: '#111827' }}>{label}</div>
      </div>
      <div style={{ fontSize: 11, color: '#6B7280', lineHeight: 1.4 }}>{reason}</div>
    </div>
  )
}

export default function HeroVerdict({ d }) {
  if (!d) return null

  const p = d.current_price
  const ivBase = d.dcf?.base?.iv
  const upside = (Number.isFinite(p) && Number.isFinite(ivBase) && p > 0)
    ? (ivBase / p - 1)
    : null
  const allBelow = d.dcf
    ? [d.dcf.conservative, d.dcf.base, d.dcf.optimistic].every(s => Number.isFinite(s?.iv) && s.iv < p)
    : false
  const allAbove = d.dcf
    ? [d.dcf.conservative, d.dcf.base, d.dcf.optimistic].every(s => Number.isFinite(s?.iv) && s.iv > p)
    : false

  const verdictText = !d.dcf
    ? `The DCF model could not be fully computed for ${d.company_name}. See the warnings below.`
    : allBelow
      ? `Under the academic DCF model, ${d.company_name} is overvalued at ${fmt$(p)}. Even the optimistic scenario implies ${fmt$(d.dcf.optimistic.iv)}.`
      : allAbove
        ? `Under the academic DCF model, ${d.company_name} is undervalued at ${fmt$(p)}. Even the conservative scenario implies ${fmt$(d.dcf.conservative.iv)}.`
        : `The model gives a mixed picture at ${fmt$(p)} — scenarios straddle the market price.`

  // 5 scorecard dimensions
  const valueRating = upside == null ? 'unknown'
    : upside < -0.20 ? 'red'
    : upside > 0.20  ? 'green'
    : 'amber'
  const growthRating = !d.reverse_dcf || d.reverse_dcf.failed ? 'unknown'
    : Math.abs(d.reverse_dcf.gap_vs_historical || 0) < 0.05 ? 'green'
    : Math.abs(d.reverse_dcf.gap_vs_historical || 0) < 0.15 ? 'amber'
    : 'red'
  const trackRecord = d.fcf?.history
    ? (() => {
        const neg = d.fcf.history.filter(y => y.fcf < 0).length
        return neg === 0 ? 'green' : neg <= 2 ? 'amber' : 'red'
      })()
    : 'unknown'
  const balanceSheet = d.dcf?.net_debt != null
    ? d.dcf.net_debt < 0 ? 'green'
    : d.dcf.net_debt / (d.market_cap || 1) < 0.2 ? 'amber'
    : 'red'
    : 'unknown'
  const suitability = d.suitability_rating || 'unknown'

  return (
    <section style={{
      background: '#FFFFFF',
      border: '0.5px solid #E5E7EB',
      borderRadius: 12,
      padding: '24px 28px',
    }}>
      {/* Company header */}
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 12, flexWrap: 'wrap', marginBottom: 6 }}>
        <h2 style={{ fontSize: 20, fontWeight: 800, color: '#111827', margin: 0 }}>{d.company_name}</h2>
        <span style={{ fontSize: 12, fontWeight: 600, color: '#6B7280', letterSpacing: '0.04em' }}>
          {d.ticker}
        </span>
        <span style={{ fontSize: 12, color: '#9CA3AF' }}>· {d.sector}</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 20 }}>
        <span style={{ fontSize: 28, fontWeight: 800, color: '#111827', letterSpacing: '-0.02em' }}>
          {fmt$(p)}
        </span>
        <span style={{ fontSize: 13, color: '#6B7280' }}>· {fmtMcap(d.market_cap)} market cap</span>
      </div>

      {/* Headline question */}
      <div style={{ fontSize: 15, color: '#6B7280', marginBottom: 8 }}>
        Should you buy {d.company_name} at {fmt$(p)}?
      </div>

      {/* Verdict */}
      <div style={{
        fontSize: 18,
        fontWeight: 600,
        color: '#111827',
        lineHeight: 1.5,
        marginBottom: 20,
      }}>
        {verdictText}
      </div>

      {/* Price gauge */}
      {d.dcf && Number.isFinite(p) && (
        <PriceGauge
          conservative={d.dcf.conservative?.iv}
          base={d.dcf.base?.iv}
          optimistic={d.dcf.optimistic?.iv}
          marketPrice={p}
        />
      )}

      {/* Scorecard */}
      <div style={{
        marginTop: 22,
        paddingTop: 18,
        borderTop: '0.5px solid #F3F4F6',
        display: 'flex',
        gap: 16,
        flexWrap: 'wrap',
      }}>
        <ScorecardDot
          rating={valueRating}
          label="Value"
          reason={upside == null ? 'No data' : upside > 0 ? `${pct(upside)} model upside` : `${pct(Math.abs(upside))} model downside`}
        />
        <ScorecardDot
          rating={growthRating}
          label="Implied growth"
          reason={d.reverse_dcf?.failed ? 'Could not solve' : `${pct(d.reverse_dcf?.implied_growth)} required · ${pct(d.reverse_dcf?.historical_median)} delivered`}
        />
        <ScorecardDot
          rating={trackRecord}
          label="Track record"
          reason={d.fcf?.history ? `${d.fcf.history.filter(y => y.fcf >= 0).length} of ${d.fcf.history.length} years FCF positive` : 'No FCF history'}
        />
        <ScorecardDot
          rating={balanceSheet}
          label="Balance sheet"
          reason={d.dcf?.net_debt != null ? (d.dcf.net_debt < 0 ? 'Net cash position' : `Net debt ${fmtMcap(d.dcf.net_debt)}`) : 'No balance data'}
        />
        <ScorecardDot
          rating={suitability}
          label="DCF suitability"
          reason={d.suitability_rating === 'green' ? 'Model fits cleanly' : d.suitability_rating === 'amber' ? 'Run with caveats' : 'Model may not fit'}
        />
      </div>
    </section>
  )
}

function PriceGauge({ conservative, base, optimistic, marketPrice }) {
  const values = [conservative, base, optimistic, marketPrice].filter(Number.isFinite)
  if (values.length === 0) return null
  const minV = Math.min(...values, 0)
  const maxV = Math.max(...values)
  const span = (maxV - minV) || 1
  const pos = v => `${((v - minV) / span) * 100}%`

  return (
    <div style={{ position: 'relative', height: 60, marginTop: 4 }}>
      {/* track */}
      <div style={{
        position: 'absolute', top: 28, left: 0, right: 0, height: 4,
        background: 'linear-gradient(90deg, #FCA5A5 0%, #FDE68A 50%, #BBF7D0 100%)',
        borderRadius: 2,
      }} />
      {/* IV markers */}
      {[
        { label: 'Conservative', v: conservative, colour: '#A32D2D' },
        { label: 'Base', v: base, colour: '#185FA5' },
        { label: 'Optimistic', v: optimistic, colour: '#3B6D11' },
      ].filter(m => Number.isFinite(m.v)).map(m => (
        <div key={m.label} style={{
          position: 'absolute', top: 22, left: pos(m.v), transform: 'translateX(-50%)',
          textAlign: 'center', minWidth: 0,
        }}>
          <div style={{ width: 2, height: 16, background: m.colour, margin: '0 auto' }} />
          <div style={{ fontSize: 10, fontWeight: 700, color: m.colour, marginTop: 2 }}>
            {m.label}
          </div>
          <div style={{ fontSize: 10, color: '#6B7280' }}>${m.v.toFixed(0)}</div>
        </div>
      ))}
      {/* market price marker — bigger */}
      <div style={{
        position: 'absolute', top: 8, left: pos(marketPrice), transform: 'translateX(-50%)',
        textAlign: 'center',
      }}>
        <div style={{ fontSize: 10, fontWeight: 700, color: '#111827' }}>You are here</div>
        <div style={{ width: 3, height: 20, background: '#111827', margin: '2px auto' }} />
        <div style={{ fontSize: 11, fontWeight: 800, color: '#111827' }}>${marketPrice.toFixed(2)}</div>
      </div>
    </div>
  )
}

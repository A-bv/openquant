/**
 * Backtest calibration disclosure — the project's trust story.
 *
 * Loads /calibration.json (built from backtest/results/calibration_summary.json)
 * and surfaces the honest "model not yet calibrated" disclosure with the
 * numbers behind it. Compact "hero" placement sits near the top of the page.
 */

import { useEffect, useState } from 'react'

const pct = (v, d = 1) => v == null || !Number.isFinite(v) ? '—' : `${v.toFixed(d)}%`

export default function CalibrationPanel({ placement = 'full' }) {
  const [cal, setCal] = useState(null)
  const [err, setErr] = useState(null)
  useEffect(() => {
    fetch('/calibration.json')
      .then(r => r.json())
      .then(setCal)
      .catch(e => setErr(e.toString()))
  }, [])

  if (err) return null
  if (!cal) return null

  const reg = cal.calibration_regression || {}
  const verdicts = cal.verdict_hit_rate || {}
  const wellCalibrated = (reg.r_squared ?? 0) >= 0.10

  // Compact placement — minimal vertical space, key message + link
  if (placement === 'hero') {
    return (
      <section style={{
        background: '#FFFBEB',
        border: '0.5px solid #FDE68A',
        borderRadius: 10,
        padding: '12px 16px',
        display: 'flex',
        alignItems: 'center',
        gap: 14,
        flexWrap: 'wrap',
      }}>
        <div style={{
          fontSize: 11, fontWeight: 700, color: '#92400E',
          background: '#FEF3C7', padding: '3px 8px', borderRadius: 999,
          whiteSpace: 'nowrap',
        }}>
          {wellCalibrated ? '✓ CALIBRATED' : '⚠ HONEST DISCLOSURE'}
        </div>
        <div style={{ fontSize: 12, color: '#78350F', lineHeight: 1.5, flex: 1, minWidth: 200 }}>
          {wellCalibrated
            ? `Backtested on 50 S&P 500 stocks 2014-2024 — model's verdicts explain ${pct((reg.r_squared || 0) * 100)} of realized return variance.`
            : `Math is correct (163 EPFL tests pass), but our predictions on 50 real stocks 2014-2024 do NOT yet predict actual returns reliably (R² = ${reg.r_squared?.toFixed(3) ?? '—'}). Read the page knowing this.`}
        </div>
        <a href="https://github.com/A-bv/openquant/blob/main/docs/backtest_2014_2024.md" target="_blank" rel="noreferrer"
          style={{
            fontSize: 11, fontWeight: 600, color: '#92400E',
            textDecoration: 'underline', whiteSpace: 'nowrap',
          }}>
          See full backtest report →
        </a>
      </section>
    )
  }

  // Full placement — used elsewhere if needed
  return (
    <section style={{
      background: '#FFFBEB',
      border: '0.5px solid #FDE68A',
      borderRadius: 12,
      padding: '22px 26px',
    }}>
      <h3 style={{ fontSize: 15, fontWeight: 700, color: '#92400E', margin: 0, marginBottom: 6 }}>
        🟡 How much should you trust this?
      </h3>
      <p style={{ fontSize: 13, color: '#78350F', lineHeight: 1.6, marginBottom: 16, maxWidth: 720 }}>
        Our model's <strong>formulas</strong> are pinned to the EPFL Principles of Finance answer keys
        (163 unit tests). Its <strong>predictions on real stocks</strong> are still being calibrated.
        We ran the full model on 50 S&P 500 stocks starting in Jan 2014 and compared verdicts to
        what actually happened through Jan 2024:
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12, marginBottom: 16 }}>
        <BacktestStat label='Called "undervalued"' n={verdicts.undervalued?.n} mean={verdicts.undervalued?.mean_realized_annualised} />
        <BacktestStat label='Called "overvalued"' n={verdicts.overvalued?.n} mean={verdicts.overvalued?.mean_realized_annualised} />
        <BacktestStat label='Called "fairly priced"' n={verdicts.fairly_priced?.n} mean={verdicts.fairly_priced?.mean_realized_annualised} />
      </div>
      <div style={{ fontSize: 11, color: '#92400E' }}>
        Full report: <a href="https://github.com/A-bv/openquant/blob/main/docs/backtest_2014_2024.md" target="_blank" rel="noreferrer" style={{ color: '#92400E', textDecoration: 'underline' }}>
          docs/backtest_2014_2024.md
        </a>
      </div>
    </section>
  )
}

function BacktestStat({ label, n, mean }) {
  const baseline = 0.121
  const colour = mean == null ? '#9CA3AF'
    : mean > baseline + 0.01 ? '#3B6D11'
    : mean < baseline - 0.01 ? '#A32D2D'
    : '#6B7280'
  return (
    <div style={{
      background: '#FFFFFF',
      border: '0.5px solid #FDE68A',
      borderRadius: 8,
      padding: '12px 14px',
    }}>
      <div style={{ fontSize: 10, fontWeight: 700, color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 4 }}>
        {label} (n={n ?? '—'})
      </div>
      <div style={{ fontSize: 20, fontWeight: 800, color: colour, lineHeight: 1 }}>
        {mean != null ? `${(mean * 100).toFixed(1)}%/yr` : '—'}
      </div>
      <div style={{ fontSize: 10, color: '#9CA3AF', marginTop: 4 }}>
        vs S&P 500 baseline 12.1%/yr
      </div>
    </div>
  )
}

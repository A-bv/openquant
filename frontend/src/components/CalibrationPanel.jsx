/**
 * Backtest calibration disclosure — the project's trust story.
 *
 * Loads /calibration.json (built from backtest/results/calibration_summary.json)
 * and surfaces the headline numbers: when the model said X historically,
 * what actually happened over the next 10 years?
 */

import { useEffect, useState } from 'react'

const pct = (v, d = 1) => v == null || !Number.isFinite(v) ? '—' : `${v.toFixed(d)}%`

export default function CalibrationPanel() {
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

  const h = cal.headline || {}
  const reg = cal.calibration_regression || {}
  const verdicts = cal.verdict_hit_rate || {}

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
        The model's <strong>formulas</strong> are pinned to the EPFL Principles of Finance answer keys
        (163 unit tests). Its <strong>predictions on real stocks</strong> are still being calibrated.
        We ran the full model "as of" January 2014 on 50 S&P 500 stocks and compared verdicts to
        what actually happened through January 2024. Here's what we found:
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12, marginBottom: 16 }}>
        <BacktestStat
          label='Stocks called "undervalued"'
          n={verdicts.undervalued?.n}
          mean={verdicts.undervalued?.mean_realized_annualised}
          baseline={0.121}
        />
        <BacktestStat
          label='Stocks called "overvalued"'
          n={verdicts.overvalued?.n}
          mean={verdicts.overvalued?.mean_realized_annualised}
          baseline={0.121}
        />
        <BacktestStat
          label='Stocks called "fairly priced"'
          n={verdicts.fairly_priced?.n}
          mean={verdicts.fairly_priced?.mean_realized_annualised}
          baseline={0.121}
        />
      </div>

      <div style={{
        background: '#FFFFFF',
        border: '0.5px solid #FDE68A',
        borderRadius: 8,
        padding: '12px 14px',
        marginBottom: 12,
      }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 4 }}>
          Calibration regression
        </div>
        <div style={{ fontSize: 13, color: '#111827' }}>
          R² = <strong>{reg.r_squared != null ? reg.r_squared.toFixed(3) : '—'}</strong>{' '}
          (model explains {reg.r_squared != null ? (reg.r_squared * 100).toFixed(1) : '—'}% of variation in realized returns)
          {' · '}slope ≈ <strong>{reg.slope != null ? reg.slope.toFixed(4) : '—'}</strong>
        </div>
        <div style={{ fontSize: 12, color: '#92400E', marginTop: 6, fontStyle: 'italic' }}>
          {(reg.r_squared ?? 0) < 0.1
            ? "Honest finding: the model's verdicts don't currently predict realised returns. We're working on structural improvements (growth-cap tightening, growth fade, WACC floor). The math is correct; the calibration isn't."
            : "Calibration improving. See the full backtest report for sector-level detail."}
        </div>
      </div>

      <div style={{ fontSize: 11, color: '#92400E' }}>
        Full report: <a href="https://github.com/A-bv/openquant/blob/main/docs/backtest_2014_2024.md" target="_blank" rel="noreferrer" style={{ color: '#92400E', textDecoration: 'underline' }}>
          docs/backtest_2014_2024.md
        </a>
      </div>
    </section>
  )
}

function BacktestStat({ label, n, mean, baseline }) {
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
        {mean != null ? pct(mean * 100) : '—'}/yr
      </div>
      <div style={{ fontSize: 10, color: '#9CA3AF', marginTop: 4 }}>
        vs S&P 500 baseline 12.1%/yr
      </div>
    </div>
  )
}

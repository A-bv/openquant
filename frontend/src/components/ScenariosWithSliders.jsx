/**
 * Three scenario cards + an interactive slider panel that recomputes IV
 * live in JavaScript using the same DCF math as the backend.
 *
 * Backend returns base_fcf and other inputs in dcf_inputs; we use them
 * to back-solve any (growth, WACC, terminal) combination the user picks.
 */

import { useState, useMemo } from 'react'
import EPFLCitation from './EPFLCitation'
import Term, { DEFS } from './Term'
import LearnMore from './LearnMore'

const fmt$ = (v) => v == null || !Number.isFinite(v) ? '—' : `$${v.toFixed(2)}`
const pct = (v, d = 1) => v == null || !Number.isFinite(v) ? '—' : `${(v * 100).toFixed(d)}%`

/**
 * Local DCF computation — pure JS mirror of the backend's growing-perpetuity DCF.
 * Returns { iv, pv_fcfs, pv_tv, ev, equity }.
 */
function computeIV({ baseFcf, growth, wacc, terminalGrowth, horizon, netDebt, shares }) {
  if (!Number.isFinite(baseFcf) || baseFcf <= 0) return null
  if (!Number.isFinite(wacc) || wacc <= terminalGrowth) return null
  let pvFcfs = 0
  let projected10 = baseFcf
  for (let t = 1; t <= horizon; t++) {
    const fcfT = baseFcf * Math.pow(1 + growth, t)
    pvFcfs += fcfT / Math.pow(1 + wacc, t)
    if (t === horizon) projected10 = fcfT
  }
  const tv = projected10 * (1 + terminalGrowth) / (wacc - terminalGrowth)
  const pvTv = tv / Math.pow(1 + wacc, horizon)
  const ev = pvFcfs + pvTv
  const equity = ev - netDebt
  const iv = equity / shares
  return { iv, pvFcfs, pvTv, ev, equity }
}

function ScenarioCard({ name, scenario, currentPrice, accent, bg }) {
  if (!scenario) return null
  const haveIv = Number.isFinite(scenario.iv) && Number.isFinite(currentPrice)
  const above = haveIv ? scenario.iv > currentPrice : null
  return (
    <div style={{
      flex: 1, minWidth: 0,
      background: '#FFFFFF',
      border: `0.5px solid ${accent}33`,
      borderRadius: 10,
      padding: '14px 16px',
      display: 'flex', flexDirection: 'column', gap: 8,
    }}>
      <div style={{ fontSize: 10, fontWeight: 700, color: accent, textTransform: 'uppercase', letterSpacing: '0.07em' }}>
        {name}
      </div>
      <div style={{ fontSize: 24, fontWeight: 800, color: accent, lineHeight: 1 }}>
        {fmt$(scenario.iv)}
      </div>
      <div style={{
        display: 'inline-block', alignSelf: 'flex-start',
        fontSize: 11, fontWeight: 700,
        color: above == null ? '#6B7280' : above ? '#3B6D11' : '#A32D2D',
        background: above == null ? '#F3F4F6' : above ? '#EAF3DE' : '#FCEBEB',
        padding: '2px 7px', borderRadius: 4,
      }}>
        {pct(scenario.upside, 0)} vs price
      </div>
      <div style={{ fontSize: 11, color: '#6B7280', marginTop: 4 }}>
        Growth {pct(scenario.growth)} · TV share {pct(scenario.tv_pct, 0)}
      </div>
    </div>
  )
}

function Slider({ label, value, min, max, step, onChange, displayValue, hint }) {
  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 4 }}>
        <span style={{ fontSize: 12, fontWeight: 600, color: '#111827' }}>{label}</span>
        <span style={{ fontSize: 14, fontWeight: 700, color: '#185FA5', fontFamily: 'ui-monospace, monospace' }}>{displayValue}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={e => onChange(parseFloat(e.target.value))}
        style={{ width: '100%', accentColor: '#185FA5', cursor: 'pointer' }}
      />
      {hint && <div style={{ fontSize: 10, color: '#9CA3AF', marginTop: 2 }}>{hint}</div>}
    </div>
  )
}

export default function ScenariosWithSliders({ d }) {
  const inputs = d?.dcf_inputs
  const baseGrowth = d?.dcf?.base?.growth ?? 0.10
  const baseWacc = d?.wacc?.wacc ?? 0.10
  const baseTerminal = inputs?.terminal_growth ?? 0.025

  const [growth, setGrowth] = useState(baseGrowth)
  const [wacc, setWacc] = useState(baseWacc)
  const [terminal, setTerminal] = useState(baseTerminal)

  // Recompute IV from sliders, locally
  const live = useMemo(() => {
    if (!inputs || !d?.current_price) return null
    return computeIV({
      baseFcf: inputs.base_fcf,
      growth, wacc, terminalGrowth: terminal,
      horizon: inputs.horizon ?? 10,
      netDebt: inputs.net_debt,
      shares: inputs.shares_outstanding,
    })
  }, [inputs, growth, wacc, terminal, d?.current_price])

  const reset = () => {
    setGrowth(baseGrowth)
    setWacc(baseWacc)
    setTerminal(baseTerminal)
  }

  if (!d?.dcf) return null

  const liveGapPct = live && Number.isFinite(live.iv) && Number.isFinite(d.current_price)
    ? ((live.iv / d.current_price - 1) * 100).toFixed(1)
    : null

  return (
    <section style={{
      background: '#FFFFFF',
      border: '0.5px solid #E5E7EB',
      borderRadius: 12,
      padding: '24px 28px',
    }}>
      <h3 style={{ fontSize: 16, fontWeight: 700, color: '#111827', margin: 0, marginBottom: 4 }}>
        Three scenarios
        <EPFLCitation source="Berk-DeMarzo Ch.15 · WACC + DCF" test="test_epfl_exam1.py::TestExam1Problem2_HamadaCAPM" />
        <LearnMore section="scenarios" />
      </h3>
      <p style={{ fontSize: 13, color: '#6B7280', lineHeight: 1.5, marginBottom: 16, maxWidth: 720 }}>
        Each scenario picks different assumptions for{' '}
        <Term def={DEFS.FCF}>FCF</Term> growth and{' '}
        <Term def={DEFS.WACC}>WACC</Term> (the discount rate),
        then projects 10 years of cash flows and discounts them back to today.
      </p>

      <div style={{ display: 'flex', gap: 10, marginBottom: 24, flexWrap: 'wrap' }}>
        <ScenarioCard name="Conservative" scenario={d.dcf.conservative} currentPrice={d.current_price} accent="#A32D2D" />
        <ScenarioCard name="Base" scenario={d.dcf.base} currentPrice={d.current_price} accent="#185FA5" />
        <ScenarioCard name="Optimistic" scenario={d.dcf.optimistic} currentPrice={d.current_price} accent="#3B6D11" />
      </div>

      {/* Slider panel */}
      <div style={{
        background: '#F8FAFC',
        border: '0.5px solid #E5E7EB',
        borderRadius: 10,
        padding: '18px 20px',
      }}>
        <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: 14, flexWrap: 'wrap', gap: 8 }}>
          <div>
            <div style={{ fontSize: 13, fontWeight: 700, color: '#111827' }}>Try your own assumptions</div>
            <div style={{ fontSize: 11, color: '#6B7280', marginTop: 2 }}>
              Don't believe our <Term def={DEFS.beta}>β</Term> or <Term def={DEFS.WACC}>WACC</Term>?
              Slide to override and watch the intrinsic value recompute live.
            </div>
          </div>
          <button onClick={reset} style={{
            fontSize: 11, color: '#185FA5', background: 'none', border: 'none',
            cursor: 'pointer', fontFamily: 'inherit', padding: 0,
          }}>
            ↺ Reset to model defaults
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 20 }}>
          <Slider
            label={<><Term def={DEFS.FCF}>FCF</Term> growth rate (10-yr horizon)</>}
            value={growth}
            min={-0.10}
            max={1.0}
            step={0.005}
            onChange={setGrowth}
            displayValue={pct(growth)}
            hint={`How much you think the company's cash flow will grow per year. Historical median: ${pct(d.fcf?.median_growth)}`}
          />
          <Slider
            label={<>Discount rate (<Term def={DEFS.WACC}>WACC</Term> or your <Term def={DEFS.hurdle}>hurdle rate</Term>)</>}
            value={wacc}
            min={0.04}
            max={0.25}
            step={0.001}
            onChange={setWacc}
            displayValue={pct(wacc, 2)}
            hint={`Return you require for taking the risk. Model's WACC: ${pct(baseWacc, 2)} · Buffett's hurdle: ~5%`}
          />
          <Slider
            label={<><Term def={DEFS.TV}>Terminal</Term> growth (after year 10)</>}
            value={terminal}
            min={-0.02}
            max={Math.max(0.05, wacc - 0.005)}
            step={0.0025}
            onChange={setTerminal}
            displayValue={pct(terminal, 2)}
            hint={`Long-run growth rate forever after year 10. GDP-long-run ≈ 2.5%. Can't exceed the discount rate.`}
          />
        </div>

        {live && Number.isFinite(live.iv) && (
          <div style={{
            marginTop: 18, padding: '14px 16px',
            background: '#FFFFFF', border: '0.5px solid #E5E7EB', borderRadius: 8,
            display: 'flex', alignItems: 'baseline', gap: 20, flexWrap: 'wrap',
          }}>
            <div>
              <div style={{ fontSize: 10, fontWeight: 700, color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Your <Term def={DEFS.IV}>intrinsic value</Term>
              </div>
              <div style={{ fontSize: 26, fontWeight: 800, color: '#185FA5', lineHeight: 1, marginTop: 4 }}>
                {fmt$(live.iv)}
              </div>
            </div>
            {liveGapPct != null && (
              <div>
                <div style={{ fontSize: 10, fontWeight: 700, color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  vs current price {fmt$(d.current_price)}
                </div>
                <div style={{
                  fontSize: 20, fontWeight: 700, lineHeight: 1, marginTop: 4,
                  color: parseFloat(liveGapPct) > 0 ? '#3B6D11' : '#A32D2D',
                }}>
                  {parseFloat(liveGapPct) >= 0 ? '+' : ''}{liveGapPct}%
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  )
}

import { useState } from 'react'
import axios from 'axios'
import SearchBar from './components/SearchBar'
import Step from './components/Step'
import MetricCard from './components/MetricCard'
import InsightBox from './components/InsightBox'
import ReverseChart from './components/ReverseChart'
import FCFHistoryChart from './components/FCFHistoryChart'
import WaterfallChart from './components/WaterfallChart'
import ScenarioCards from './components/ScenarioCards'
import SensitivityTable from './components/SensitivityTable'
import WACCBreakdown from './components/WACCBreakdown'
import LoadingState from './components/LoadingState'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const pct  = (v, d = 1) => v == null ? '—' : `${(v * 100).toFixed(d)}%`
const fmtB = (v) => {
  if (v == null) return '—'
  const b = Math.abs(v) / 1e9
  const sign = v < 0 ? '-' : ''
  return `${sign}$${b >= 100 ? b.toFixed(0) : b.toFixed(1)}B`
}

export default function App() {
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState(null)
  const [data, setData]           = useState(null)
  const [activeTicker, setActive] = useState('')

  const analyse = async (ticker) => {
    setLoading(true)
    setError(null)
    setData(null)
    setActive(ticker)
    try {
      const res = await axios.post(`${API}/analyse`, {
        ticker,
        risk_free_rate: 0.045,
        market_risk_premium: 0.055,
        terminal_growth: 0.025,
      })
      setData(res.data)
    } catch (e) {
      const detail = e.response?.data?.detail
      const msg = (typeof detail === 'object' ? detail?.error : detail)
        || e.response?.data?.error
        || 'Analysis failed. Please try again.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  const d       = data
  const revDcf  = d?.reverse_dcf
  const revFail = revDcf?.failed

  const step1Insight = d
    ? `${d.company_name} converts ${fmtB(d.fcf?.revenue_latest)} in revenue into ${fmtB(d.fcf?.latest)} of free cash — and has grown that at ${pct(d.fcf?.median_growth)}/yr over the past five years.`
    : null

  const step2Insight = d && revDcf && !revFail
    ? (revDcf.implied_growth < revDcf.historical_median
        ? `The market is pricing ${d.company_name} as if its cash profits will ${revDcf.implied_growth < 0 ? 'decline' : 'grow slowly'} at ${pct(revDcf.implied_growth)}/yr. Yet historically it grew at ${pct(revDcf.historical_median)}/yr. That ${(Math.abs(revDcf.gap_vs_historical) * 100).toFixed(1)}pp gap is the judgment you need to make.`
        : `The market expects ${d.company_name} to grow at ${pct(revDcf.implied_growth)}/yr — above its historical rate of ${pct(revDcf.historical_median)}/yr. You need to believe the company can sustain above-average performance.`)
    : null

  const step3Insight = d?.dcf ? (() => {
    const { conservative, base, optimistic } = d.dcf
    const p = d.current_price
    const allAbove = [conservative, base, optimistic].every(s => s.iv > p)
    const allBelow = [conservative, base, optimistic].every(s => s.iv < p)
    if (allAbove) return `Under all three scenarios the model estimates ${d.company_name} is undervalued at $${p.toFixed(0)}. Even the conservative scenario implies $${conservative.iv.toFixed(0)}.`
    if (allBelow) return `Under all three scenarios the model estimates ${d.company_name} is overvalued at $${p.toFixed(0)}. Even the optimistic scenario implies only $${optimistic.iv.toFixed(0)}.`
    return `The model gives a mixed picture at $${p.toFixed(0)}. Conservative: $${conservative.iv.toFixed(0)}, base: $${base.iv.toFixed(0)}, optimistic: $${optimistic.iv.toFixed(0)}.`
  })() : null

  const step3Colour = d?.dcf ? (
    [d.dcf.conservative, d.dcf.base, d.dcf.optimistic].every(s => s.iv > d.current_price) ? 'green' :
    [d.dcf.conservative, d.dcf.base, d.dcf.optimistic].every(s => s.iv < d.current_price) ? 'red' : 'blue'
  ) : 'blue'

  return (
    <div style={{ minHeight: '100vh', background: '#F9FAFB' }}>
      {/* Topbar */}
      <header style={{
        background: '#FFFFFF',
        borderBottom: '0.5px solid #E5E7EB',
        padding: '0 48px',
        display: 'flex',
        alignItems: 'center',
        height: 56,
        gap: 20,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ fontSize: 16, fontWeight: 800, color: '#111827', letterSpacing: '-0.02em' }}>OpenQuant</span>
          <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#185FA5' }} />
        </div>
        <div style={{ flex: 1, fontSize: 12, color: '#9CA3AF' }}>
          Every stock price hides a prediction. We show you what that prediction is.
        </div>
        <a href="https://github.com/A-bv/openquant" target="_blank" rel="noreferrer"
          style={{ fontSize: 12, color: '#6B7280' }}>
          GitHub ↗
        </a>
      </header>

      {/* Content */}
      <main style={{ maxWidth: 900, margin: '0 auto', padding: '32px 24px', display: 'flex', flexDirection: 'column', gap: 20 }}>

        {/* Hero card */}
        <div style={{
          background: '#FFFFFF',
          border: '0.5px solid #E5E7EB',
          borderRadius: 12,
          padding: '28px 32px',
        }}>
          <h1 style={{ fontSize: 22, fontWeight: 800, color: '#111827', marginBottom: 10, lineHeight: 1.2 }}>
            Company Valuation
          </h1>
          <p style={{ fontSize: 13, color: '#6B7280', marginBottom: 22, lineHeight: 1.6, maxWidth: 620 }}>
            OpenQuant doesn't tell you what a company is worth. It tells you what growth assumptions are baked into today's price — and whether you agree with the market's bet.
          </p>
          <SearchBar onAnalyse={analyse} loading={loading} data={d} />
        </div>

        {/* Error */}
        {error && (
          <div style={{
            background: '#FCEBEB', border: '0.5px solid #F5B5B5',
            borderRadius: 8, padding: '14px 18px',
            color: '#A32D2D', fontSize: 13,
            display: 'flex', alignItems: 'center', gap: 12,
          }}>
            <span>{error}</span>
            <button onClick={() => analyse(activeTicker)} style={{
              color: '#185FA5', background: 'none', border: 'none',
              cursor: 'pointer', fontSize: 12, fontFamily: 'inherit',
            }}>
              Retry ↺
            </button>
          </div>
        )}

        {/* Loading */}
        {loading && <LoadingState ticker={activeTicker} />}

        {/* Not suitable */}
        {d && !d.is_suitable && (
          <div style={{
            background: '#FCEBEB', border: '0.5px solid #F5B5B5',
            borderRadius: 12, padding: '28px 32px',
          }}>
            <div style={{ fontSize: 15, fontWeight: 700, color: '#A32D2D', marginBottom: 10 }}>
              🔴 DCF not suitable for {d.company_name}
            </div>
            <p style={{ fontSize: 13, color: '#374151', marginBottom: 14, lineHeight: 1.6 }}>
              {d.suitability_message}
            </p>
            {d.alternative_methods?.length > 0 && (
              <div>
                <div style={{ fontSize: 12, fontWeight: 600, color: '#111827', marginBottom: 6 }}>Consider instead:</div>
                {d.alternative_methods.map(m => (
                  <div key={m} style={{ fontSize: 12, color: '#6B7280', padding: '2px 0' }}>· {m}</div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Results */}
        {d && d.is_suitable && (
          <>
            {/* Step 1 */}
            <Step
              number={1}
              title={`What does ${d.company_name} actually generate?`}
              why="Before valuing anything, we need to understand what the business produces. We use Free Cash Flow (FCF) — the actual cash left after paying all costs and investments. Unlike profit, FCF cannot be manipulated by accounting choices."
            >
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
                <MetricCard
                  label="Revenue (latest yr)"
                  value={fmtB(d.fcf.revenue_latest)}
                  explanation="Total sales in the most recent fiscal year, from SEC EDGAR filings"
                  colour="neutral"
                />
                <MetricCard
                  label="Free Cash Flow (latest yr)"
                  value={fmtB(d.fcf.latest)}
                  explanation="Actual cash after all operating costs and capital investments — cannot be manipulated by accounting"
                  colour={d.fcf.latest >= 0 ? 'positive' : 'negative'}
                />
                <MetricCard
                  label="FCF Margin"
                  value={pct(d.fcf.fcf_margin)}
                  explanation="FCF as a share of revenue — how efficiently the company converts sales to cash"
                  colour={d.fcf.fcf_margin >= 0.10 ? 'positive' : d.fcf.fcf_margin < 0 ? 'negative' : 'neutral'}
                />
              </div>
              <FCFHistoryChart history={d.fcf.history} companyName={d.company_name} />
              <InsightBox colour="blue">{step1Insight}</InsightBox>
            </Step>

            {/* Step 2 — reverse DCF */}
            {revDcf && !revFail && (
              <Step
                number={2}
                title={`Every stock price hides a prediction. What is ${d.company_name}'s?`}
                why="Instead of asking 'what is this worth?' — we ask: what growth rate is already baked into today's price? We reverse-solve the valuation equation to find out."
              >
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12 }}>
                  <MetricCard
                    label="Market-Implied Growth"
                    value={pct(revDcf.implied_growth)}
                    explanation={`For $${d.current_price.toFixed(2)} to be fair value, ${d.company_name}'s cash profits must grow at ${pct(revDcf.implied_growth)}/yr for 10 years`}
                    colour={revDcf.implied_growth < 0 ? 'negative' : revDcf.implied_growth >= revDcf.historical_median ? 'positive' : 'neutral'}
                  />
                  <MetricCard
                    label="Historical Median Growth"
                    value={pct(revDcf.historical_median)}
                    explanation={`What ${d.company_name} actually delivered — the track record`}
                    colour="positive"
                  />
                  <MetricCard
                    label="Gap"
                    value={`${(revDcf.gap_vs_historical || 0) >= 0 ? '+' : ''}${((revDcf.gap_vs_historical || 0) * 100).toFixed(1)}pp`}
                    explanation={`The market expects ${(revDcf.gap_vs_historical || 0) >= 0 ? (Math.abs(revDcf.gap_vs_historical * 100)).toFixed(1) + 'pp more' : (Math.abs(revDcf.gap_vs_historical * 100)).toFixed(1) + 'pp less'} than history. This is the judgment you need to make.`}
                    colour="neutral"
                  />
                </div>
                <ReverseChart revDcf={revDcf} />
                <InsightBox colour={revDcf.implied_growth < revDcf.historical_median ? 'blue' : 'green'}>
                  {step2Insight}
                </InsightBox>
              </Step>
            )}

            {revFail && (
              <Step number={2} title="Market-implied growth" why="We reverse-solve the DCF equation to find the growth rate baked into today's price.">
                <InsightBox colour="red">{revDcf?.verdict || 'Reverse DCF could not be computed.'}</InsightBox>
              </Step>
            )}

            {/* Step 3 — forward DCF */}
            <Step
              number={3}
              title={`If you disagree with the market — what is ${d.company_name} actually worth?`}
              why={`We run the valuation forward under three scenarios. Each assumes a different FCF growth rate, then discounts all future cash flows back to today using a discount rate (WACC) of ${pct(d.wacc.wacc)} — the minimum return investors require.`}
            >
              <ScenarioCards dcf={d.dcf} currentPrice={d.current_price} />
              <WaterfallChart dcfBase={d.dcf.base} netDebt={d.dcf.net_debt} companyName={d.company_name} />
              {step3Insight && (
                <InsightBox colour={step3Colour}>{step3Insight}</InsightBox>
              )}
            </Step>

            {/* Step 4 — sensitivity */}
            <Step
              number={4}
              title="How sensitive is this to assumptions?"
              why="Every DCF depends on two numbers above all: growth rate and discount rate (WACC). Small changes produce large swings in fair value. This table shows what the model implies at every combination."
            >
              <SensitivityTable sensitivity={d.sensitivity} currentPrice={d.current_price} />
            </Step>

            {/* Step 5 — WACC */}
            <Step
              number={5}
              title="How was the discount rate computed?"
              why="The discount rate (WACC) is the most important technical input. Here is exactly how it was built from the CAPM formula — every number sourced and explained."
            >
              <WACCBreakdown wacc={d.wacc} />
            </Step>
          </>
        )}
      </main>
    </div>
  )
}

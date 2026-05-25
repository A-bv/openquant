import { useState } from 'react'
import axios from 'axios'
import { useIsMobile } from './components/useIsMobile'

// v3 flow components
import HeroVerdict from './components/HeroVerdict'
import MarketBetPanel from './components/MarketBetPanel'
import ScenariosWithSliders from './components/ScenariosWithSliders'
import WhatYouNeedToBelieve from './components/WhatYouNeedToBelieve'
import MultiplesCheck from './components/MultiplesCheck'
import CalibrationPanel from './components/CalibrationPanel'

// retained components (well-tested)
import SearchBar from './components/SearchBar'
import LoadingState from './components/LoadingState'
import FCFHistoryChart from './components/FCFHistoryChart'
import SensitivityTable from './components/SensitivityTable'
import WACCBreakdown from './components/WACCBreakdown'
import EPFLCitation from './components/EPFLCitation'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function App() {
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState(null)
  const [data, setData]           = useState(null)
  const [activeTicker, setActive] = useState('')
  const isMobile = useIsMobile()

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

  const d = data

  return (
    <div style={{ minHeight: '100vh', background: '#F9FAFB' }}>
      {/* Topbar */}
      <header style={{
        background: '#FFFFFF',
        borderBottom: '0.5px solid #E5E7EB',
        padding: isMobile ? '0 16px' : '0 48px',
        display: 'flex',
        alignItems: 'center',
        height: 56,
        gap: 20,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ fontSize: 16, fontWeight: 800, color: '#111827', letterSpacing: '-0.02em' }}>
            OpenQuant
          </span>
          <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#185FA5' }} />
        </div>
        <div style={{ flex: 1, fontSize: 12, color: '#9CA3AF', display: isMobile ? 'none' : undefined }}>
          Academic-grade valuation, every formula traceable to its source, backtested on history.
        </div>
        <a href="https://github.com/A-bv/openquant" target="_blank" rel="noreferrer"
          style={{ fontSize: 12, color: '#6B7280' }}>
          GitHub ↗
        </a>
      </header>

      <main style={{
        maxWidth: 940, margin: '0 auto',
        padding: isMobile ? '16px 12px' : '28px 24px',
        display: 'flex', flexDirection: 'column', gap: 18,
      }}>

        {/* Search */}
        <section style={{
          background: '#FFFFFF',
          border: '0.5px solid #E5E7EB',
          borderRadius: 12,
          padding: isMobile ? '20px 16px' : '24px 28px',
        }}>
          <h1 style={{ fontSize: 24, fontWeight: 800, color: '#111827', marginBottom: 10, lineHeight: 1.15 }}>
            Reverse-engineer any stock price.
          </h1>
          <p style={{ fontSize: 14, color: '#6B7280', marginBottom: 18, lineHeight: 1.6, maxWidth: 660 }}>
            Type a US ticker. We'll show you the growth assumptions baked into today's price,
            estimate what the company is actually worth, and tell you exactly where our model
            could be wrong. Every formula traceable to academic source; backtested on 10 years of history.
          </p>
          <SearchBar onAnalyse={analyse} loading={loading} data={d} />
        </section>

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

        {loading && <LoadingState ticker={activeTicker} />}

        {/* Not-suitable verdict */}
        {d && !d.is_suitable && (
          <section style={{
            background: '#FCEBEB', border: '0.5px solid #F5B5B5',
            borderRadius: 12, padding: '24px 28px',
          }}>
            <div style={{ fontSize: 16, fontWeight: 700, color: '#A32D2D', marginBottom: 10 }}>
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
          </section>
        )}

        {/* Main results — v3 flow */}
        {d && d.is_suitable && (
          <>
            <HeroVerdict d={d} />

            {/* Trust signal — visible BEFORE the user dives deep */}
            <CalibrationPanel placement="hero" />

            <MarketBetPanel d={d} />
            <ScenariosWithSliders d={d} />
            <WhatYouNeedToBelieve d={d} />
            <MultiplesCheck d={d} />

            {/* FCF history — kept as a focused section */}
            <section style={{
              background: '#FFFFFF', border: '0.5px solid #E5E7EB',
              borderRadius: 12, padding: '20px 24px',
            }}>
              <h3 style={{ fontSize: 14, fontWeight: 700, color: '#111827', margin: 0, marginBottom: 4 }}>
                Free cash flow history
                <EPFLCitation source="EPFL FS p.4 · FCF formula · Berk-DeMarzo Ch.7.1" test="test_epfl_exam1.py::TestExam1Problem2_FCF" />
              </h3>
              <p style={{ fontSize: 12, color: '#6B7280', marginBottom: 12 }}>
                What the business actually generated. Red bars = negative FCF.
              </p>
              <FCFHistoryChart history={d.fcf.history} companyName={d.company_name} />
            </section>

            {/* Sensitivity */}
            <section style={{
              background: '#FFFFFF', border: '0.5px solid #E5E7EB',
              borderRadius: 12, padding: '20px 24px',
            }}>
              <h3 style={{ fontSize: 14, fontWeight: 700, color: '#111827', margin: 0, marginBottom: 4 }}>
                Sensitivity heatmap
              </h3>
              <p style={{ fontSize: 12, color: '#6B7280', marginBottom: 12, lineHeight: 1.5 }}>
                Each cell shows what the model says the stock is worth, at that combination of growth rate (rows) and discount rate (columns).
                <br />
                <strong>Read this:</strong> <span style={{ color: '#3B6D11' }}>green = above today's price</span> · <span style={{ color: '#A32D2D' }}>red = below today's price</span> · amber border = closest match to today's price.
              </p>
              <SensitivityTable sensitivity={d.sensitivity} currentPrice={d.current_price} />
            </section>

            {/* WACC breakdown — the math */}
            <section style={{
              background: '#FFFFFF', border: '0.5px solid #E5E7EB',
              borderRadius: 12, padding: '20px 24px',
            }}>
              <h3 style={{ fontSize: 14, fontWeight: 700, color: '#111827', margin: 0, marginBottom: 4 }}>
                Show your work — discount rate (WACC)
                <EPFLCitation source="EPFL FS p.4 · WACC · CAPM · Berk-DeMarzo Ch.12, 15" />
              </h3>
              <p style={{ fontSize: 12, color: '#6B7280', marginBottom: 12 }}>
                Every component of the discount rate, sourced and explained.
              </p>
              <WACCBreakdown wacc={d.wacc} />
            </section>

            {/* Buffett footer */}
            <section style={{
              background: '#F9FAFB',
              borderRadius: 12,
              padding: '16px 20px',
              fontSize: 11,
              color: '#6B7280',
              lineHeight: 1.6,
              maxWidth: 720,
            }}>
              <strong style={{ color: '#374151' }}>Note on methodology.</strong>{' '}
              Buffett doesn't use WACC — he discounts at the long-bond yield (~5%), uses
              "owner's earnings" instead of FCF, and demands a 30%+ margin of safety. His
              method gives different (often higher) IVs but he'd refuse to apply it to many of these companies. We use
              the academic method because every step is traceable to a published curriculum
              and verifiable against exam answer keys. Both philosophies are legitimate.
            </section>
          </>
        )}
      </main>
    </div>
  )
}

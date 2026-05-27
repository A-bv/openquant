import { useCallback, useEffect, useState } from 'react'
import axios from 'axios'
import { useIsMobile } from './components/useIsMobile'

// v3 flow components
import HeroVerdict from './components/HeroVerdict'
import MarketBetPanel from './components/MarketBetPanel'
import ScenariosWithSliders from './components/ScenariosWithSliders'
import WhatYouNeedToBelieve from './components/WhatYouNeedToBelieve'
import MultiplesCheck from './components/MultiplesCheck'
import CalibrationPanel from './components/CalibrationPanel'
import Conclusion from './components/Conclusion'
import Glossary from './components/Glossary'
import LearnMore from './components/LearnMore'
import DisclosureSection from './components/DisclosureSection'

// retained components (well-tested)
import SearchBar from './components/SearchBar'
import LoadingState from './components/LoadingState'
import FCFHistoryChart from './components/FCFHistoryChart'
import SensitivityTable from './components/SensitivityTable'
import WACCBreakdown from './components/WACCBreakdown'
import EPFLCitation from './components/EPFLCitation'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function getInitialTicker() {
  if (typeof window === 'undefined') return ''
  return new URLSearchParams(window.location.search).get('ticker')?.trim().toUpperCase() || ''
}

function getAnalysisError(e) {
  const detail = e.response?.data?.detail
  const apiMessage = (typeof detail === 'object' ? detail?.error : detail)
    || e.response?.data?.error

  if (apiMessage) return apiMessage

  if (e.code === 'ERR_NETWORK') {
    return [
      'The analysis API is not reachable.',
      'Start the backend on http://localhost:8000 or check the frontend API URL.',
    ].join(' ')
  }

  if (e.response?.status >= 500) {
    return 'The analysis API returned a server error. Retry once, then check backend logs.'
  }

  return 'Analysis failed. Please try again.'
}

function WorkflowStep({ number, title, text }) {
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: '28px 1fr',
      gap: 10,
      alignItems: 'start',
    }}>
      <div style={{
        width: 28,
        height: 28,
        borderRadius: 999,
        background: '#EAF2FB',
        color: '#185FA5',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: 12,
        fontWeight: 800,
      }}>
        {number}
      </div>
      <div>
        <div style={{ fontSize: 13, fontWeight: 800, color: '#111827', marginBottom: 3 }}>
          {title}
        </div>
        <div style={{ fontSize: 12, color: '#6B7280', lineHeight: 1.45 }}>
          {text}
        </div>
      </div>
    </div>
  )
}

export default function App() {
  const initialTicker = getInitialTicker()
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState(null)
  const [data, setData]           = useState(null)
  const [activeTicker, setActive] = useState(initialTicker)
  const [glossaryOpen, setGlossaryOpen] = useState(false)
  const isMobile = useIsMobile()

  const analyse = useCallback(async (ticker, { syncUrl = true } = {}) => {
    const normalizedTicker = ticker.trim().toUpperCase()
    if (!normalizedTicker) return

    if (syncUrl) {
      const url = new URL(window.location.href)
      url.searchParams.set('ticker', normalizedTicker)
      window.history.replaceState({}, '', url)
    }

    setLoading(true)
    setError(null)
    setData(null)
    setActive(normalizedTicker)
    try {
      const res = await axios.post(`${API}/analyse`, {
        ticker: normalizedTicker,
        risk_free_rate: 0.045,
        market_risk_premium: 0.055,
        terminal_growth: 0.025,
      })
      setData(res.data)
    } catch (e) {
      setError(getAnalysisError(e))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (!initialTicker) return undefined

    const id = window.setTimeout(() => {
      analyse(initialTicker, { syncUrl: false })
    }, 0)

    return () => window.clearTimeout(id)
  }, [analyse, initialTicker])

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
          The corporate finance textbook, made interactive — and tested against reality.
        </div>
        <button
          onClick={() => setGlossaryOpen(true)}
          aria-label="Open glossary"
          style={{
            fontSize: 12, fontWeight: 600,
            color: '#374151', background: '#F3F4F6',
            border: '0.5px solid #E5E7EB', borderRadius: 999,
            padding: '4px 10px', cursor: 'pointer',
            fontFamily: 'inherit',
          }}
        >
          📖 Glossary
        </button>
        <a href="https://github.com/A-bv/openquant" target="_blank" rel="noreferrer"
          style={{ fontSize: 12, color: '#6B7280' }}>
          GitHub ↗
        </a>
      </header>

      {/* Glossary drawer */}
      <Glossary open={glossaryOpen} onClose={() => setGlossaryOpen(false)} />

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
          <div style={{
            fontSize: 11,
            fontWeight: 800,
            color: '#185FA5',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            marginBottom: 8,
          }}>
            Stock Valuation Lab
          </div>
          <h1 style={{ fontSize: 26, fontWeight: 800, color: '#111827', marginBottom: 10, lineHeight: 1.12 }}>
            What is the market already pricing in?
          </h1>
          <p style={{ fontSize: 14, color: '#6B7280', marginBottom: 18, lineHeight: 1.6, maxWidth: 660 }}>
            Type a US ticker. OpenQuant translates Berk-DeMarzo's valuation
            framework into one practical question: what growth, risk, and cash-flow
            assumptions must be true for today's price to make sense?
          </p>
          <SearchBar
            key={activeTicker || 'empty-search'}
            onAnalyse={analyse}
            loading={loading}
            data={d}
            value={activeTicker}
          />
        </section>

        {!d && !loading && (
          <section style={{
            background: '#FFFFFF',
            border: '0.5px solid #E5E7EB',
            borderRadius: 12,
            padding: isMobile ? '18px 16px' : '20px 24px',
          }}>
            <div style={{
              display: 'grid',
              gridTemplateColumns: isMobile ? '1fr' : 'repeat(4, 1fr)',
              gap: 16,
            }}>
              <WorkflowStep
                number="1"
                title="Read the price"
                text="Start from the market price, not from a target price."
              />
              <WorkflowStep
                number="2"
                title="Extract the belief"
                text="Reverse the DCF to estimate what growth the price implies."
              />
              <WorkflowStep
                number="3"
                title="Challenge assumptions"
                text="Move growth, WACC, and terminal growth to test your view."
              />
              <WorkflowStep
                number="4"
                title="Open the audit"
                text="Use the course formulas only when you want the full detail."
              />
            </div>
          </section>
        )}

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

            <MarketBetPanel d={d} />
            <ScenariosWithSliders d={d} />
            <WhatYouNeedToBelieve d={d} />

            <DisclosureSection
              eyebrow="Model reliability"
              title="How much should you trust the verdict?"
              summary="The formula can be correct while the prediction remains weak. Open this before treating any fair value as a forecast."
            >
              <CalibrationPanel placement="hero" />
            </DisclosureSection>

            <DisclosureSection
              eyebrow="Cross-check"
              title="Check the verdict against market multiples"
              summary="P/E, EV/EBITDA, and FCF yield provide a quick sanity check, separate from the DCF."
            >
              <MultiplesCheck d={d} />
            </DisclosureSection>

            {/* FCF history — kept as a focused section */}
            <DisclosureSection
              eyebrow="Cash-flow evidence"
              title="Inspect free cash flow history"
              summary="Use this to judge whether the growth assumption is grounded in what the business has actually produced."
            >
              <h3 style={{ fontSize: 14, fontWeight: 700, color: '#111827', margin: 0, marginBottom: 4 }}>
                Free cash flow history
                <EPFLCitation source="Berk-DeMarzo Ch.7 · FCF formula" test="test_epfl_exam1.py::TestExam1Problem2_FCF" />
                <LearnMore section="fcfHistory" />
              </h3>
              <p style={{ fontSize: 12, color: '#6B7280', marginBottom: 12 }}>
                What the business actually generated. Red bars = negative FCF.
              </p>
              <FCFHistoryChart history={d.fcf.history} companyName={d.company_name} />
            </DisclosureSection>

            {/* Sensitivity */}
            <DisclosureSection
              eyebrow="Sensitivity"
              title="Open the valuation heatmap"
              summary="See how quickly the conclusion changes when growth and discount rate move together."
            >
              <h3 style={{ fontSize: 14, fontWeight: 700, color: '#111827', margin: 0, marginBottom: 4 }}>
                Sensitivity heatmap
                <LearnMore section="sensitivity" />
              </h3>
              <p style={{ fontSize: 12, color: '#6B7280', marginBottom: 12, lineHeight: 1.5 }}>
                Each cell shows what the model says the stock is worth, at that combination of growth rate (rows) and discount rate (columns).
                <br />
                <strong>Read this:</strong> <span style={{ color: '#3B6D11' }}>green = above today's price</span> · <span style={{ color: '#A32D2D' }}>red = below today's price</span> · amber border = closest match to today's price.
              </p>
              <SensitivityTable sensitivity={d.sensitivity} currentPrice={d.current_price} />
            </DisclosureSection>

            {/* WACC breakdown — the math */}
            <DisclosureSection
              eyebrow="Course formula"
              title="Show the WACC calculation"
              summary="Open the CAPM and WACC machinery when you want to audit the discount rate."
            >
              <h3 style={{ fontSize: 14, fontWeight: 700, color: '#111827', margin: 0, marginBottom: 4 }}>
                Show your work — discount rate (WACC)
                <EPFLCitation source="Berk-DeMarzo Ch.12 (CAPM), Ch.15 (WACC)" />
                <LearnMore section="wacc" />
              </h3>
              <p style={{ fontSize: 12, color: '#6B7280', marginBottom: 12 }}>
                Every component of the discount rate, sourced and explained.
              </p>
              <WACCBreakdown wacc={d.wacc} />
            </DisclosureSection>

            {/* Per-stock conclusion + take-aways + next actions */}
            <Conclusion d={d} onAnalyse={analyse} />

            {/* Buffett footer */}
            <DisclosureSection
              eyebrow="Methodology note"
              title="Why this uses textbook DCF rather than Buffett owner earnings"
              summary="Different valuation philosophies can produce different answers. This app uses Berk-DeMarzo because the formulas are traceable and testable."
            >
              <div style={{
                fontSize: 12,
                color: '#6B7280',
                lineHeight: 1.65,
                maxWidth: 760,
              }}>
                <strong style={{ color: '#374151' }}>Note on methodology.</strong>{' '}
                Buffett doesn't use WACC — he discounts at the long-bond yield (~5%), uses
                "owner's earnings" instead of FCF, and demands a 30%+ margin of safety. His
                method gives different (often higher) IVs but he'd refuse to apply it to many
                of these companies. We use the textbook method (Berk-DeMarzo) because every
                step is traceable to a chapter and verifiable against the textbook's worked
                problems. Both philosophies are legitimate.
              </div>
            </DisclosureSection>

            {/* Brand footer */}
            <div style={{
              textAlign: 'center', fontSize: 11, color: '#9CA3AF',
              padding: '12px 0', letterSpacing: '0.04em',
            }}>
              <strong style={{ color: '#6B7280' }}>OpenQuant</strong> · Theory. Reality. You decide.
            </div>
          </>
        )}
      </main>
    </div>
  )
}

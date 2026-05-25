/**
 * Four cards showing exactly what assumptions you'd need to hold for
 * the model's verdict to be wrong. Empowers disagreement.
 */

export default function WhatYouNeedToBelieve({ d }) {
  if (!d?.dcf || !d?.reverse_dcf) return null

  const ivBase = d.dcf.base?.iv
  const p = d.current_price
  const gap = Number.isFinite(ivBase) && Number.isFinite(p) ? (ivBase - p) / p : null

  const modelSays = gap > 0.20 ? 'undervalued'
    : gap < -0.20 ? 'overvalued'
    : 'fairly priced'

  if (modelSays === 'fairly priced') {
    return null  // less interesting to disagree with a centrist call
  }

  const direction = modelSays === 'overvalued' ? 'right' : 'wrong'
  const cards = modelSays === 'overvalued' ? [
    {
      claim: `Growth will exceed ${(d.reverse_dcf.implied_growth * 100).toFixed(0)}%/yr`,
      detail: `The implied growth rate is what today's price already assumes. To justify the price you'd need growth above that — historically rare for any large-cap over a decade.`,
    },
    {
      claim: 'Discount rate should be much lower',
      detail: `Our WACC is ${(d.wacc.wacc * 100).toFixed(1)}%. If you slide it down toward 6-8%, intrinsic value rises sharply. Buffett uses ~5% for businesses he understands.`,
    },
    {
      claim: 'Terminal value should be larger',
      detail: `We assume 2.5% perpetual growth after year 10. If you believe optionality (new products, market expansion) makes years 11+ much more valuable, the model understates.`,
    },
    {
      claim: 'DCF is the wrong framework',
      detail: 'For high-growth capex-heavy firms still in expansion phase, DCF systematically understates value. Compare with revenue multiples and option-value approaches.',
    },
  ] : [
    {
      claim: `Growth will be slower than ${(d.reverse_dcf.implied_growth * 100).toFixed(0)}%/yr`,
      detail: 'The price implies pessimism. To justify the lower price you need to believe the historical track record won\'t continue.',
    },
    {
      claim: 'Discount rate should be higher',
      detail: `Our WACC is ${(d.wacc.wacc * 100).toFixed(1)}%. If you slide it up (because you think the company is riskier than its beta suggests), intrinsic value drops.`,
    },
    {
      claim: 'Margins will compress',
      detail: `We project current FCF margin (${d.fcf?.fcf_margin ? (d.fcf.fcf_margin * 100).toFixed(1) : '—'}%) forward. If you expect competition / commoditisation to compress it, the model overstates value.`,
    },
    {
      claim: 'A structural disruption is coming',
      detail: 'DCFs project historical trends. They can\'t price structural breaks — new technology, regulation, demand collapse.',
    },
  ]

  return (
    <section style={{
      background: '#FFFFFF',
      border: '0.5px solid #E5E7EB',
      borderRadius: 12,
      padding: '24px 28px',
    }}>
      <h3 style={{ fontSize: 16, fontWeight: 700, color: '#111827', margin: 0, marginBottom: 6 }}>
        What you'd need to believe to think the model is {direction}
      </h3>
      <p style={{ fontSize: 13, color: '#6B7280', lineHeight: 1.5, marginBottom: 16, maxWidth: 720 }}>
        The model says <strong>{modelSays}</strong>. For the market to be right and the model wrong,
        you need to hold at least one of these beliefs. Each is defensible — the model can't
        tell you which is true.
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 12 }}>
        {cards.map((card, i) => (
          <div key={i} style={{
            background: '#FAFBFC',
            border: '0.5px solid #E5E7EB',
            borderRadius: 8,
            padding: '14px 16px',
          }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: '#111827', marginBottom: 6, lineHeight: 1.3 }}>
              {card.claim}
            </div>
            <div style={{ fontSize: 11, color: '#6B7280', lineHeight: 1.5 }}>
              {card.detail}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

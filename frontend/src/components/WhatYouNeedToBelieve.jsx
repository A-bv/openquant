/**
 * Four cards showing exactly what assumptions you'd need to hold for
 * the model's verdict to be wrong. Empowers disagreement.
 */

export default function WhatYouNeedToBelieve({ d }) {
  if (!d?.dcf || !d?.reverse_dcf || !d?.wacc) return null

  const ivBase = d.dcf.base?.iv
  const p = d.current_price
  const gap = Number.isFinite(ivBase) && Number.isFinite(p) ? (ivBase - p) / p : null

  const modelSays = gap > 0.20 ? 'undervalued'
    : gap < -0.20 ? 'overvalued'
    : 'fairly priced'

  if (modelSays === 'fairly priced' || gap == null) {
    return null
  }

  // Null-safe formatters
  const implied = Number.isFinite(d.reverse_dcf?.implied_growth) ? d.reverse_dcf.implied_growth : null
  const waccVal = Number.isFinite(d.wacc?.wacc) ? d.wacc.wacc : null
  const margin = Number.isFinite(d.fcf?.fcf_margin) ? d.fcf.fcf_margin : null
  const impliedPct = implied != null ? (implied * 100).toFixed(0) : '—'
  const waccPct = waccVal != null ? (waccVal * 100).toFixed(1) : '—'
  const marginPct = margin != null ? (margin * 100).toFixed(1) : '—'

  const headlinePhrase = modelSays === 'overvalued'
    ? `What would need to be true for today's price to make sense?`
    : `What would need to be false for today's price to disappoint?`
  const cards = modelSays === 'overvalued' ? [
    {
      claim: `Growth will exceed ${impliedPct}%/yr`,
      detail: `The implied growth rate is what today's price already assumes. To make the price look reasonable, you need growth above that — historically rare for any large-cap over a decade.`,
    },
    {
      claim: 'Discount rate should be much lower',
      detail: `Our WACC is ${waccPct}%. If you slide it down toward 6-8%, intrinsic value rises sharply. Buffett uses ~5% for businesses he understands.`,
    },
    {
      claim: 'Terminal value should be larger',
      detail: `We assume 2.5% perpetual growth after year 10. If you believe optionality (new products, market expansion) makes years 11+ much more valuable, the model understates.`,
    },
    {
      claim: 'DCF is the wrong framework',
      detail: 'If the company is driven by option-like upside, platform effects, or assets not captured in FCF, a standard DCF can understate value.',
    },
  ] : [
    {
      claim: `Growth will be slower than ${impliedPct}%/yr`,
      detail: 'The price implies pessimism. To justify the lower price you need to believe the historical track record won\'t continue.',
    },
    {
      claim: 'Discount rate should be higher',
      detail: `Our WACC is ${waccPct}%. If you slide it up (because you think the company is riskier than its beta suggests), intrinsic value drops.`,
    },
    {
      claim: 'Margins will compress',
      detail: `We project current FCF margin (${marginPct}%) forward. If you expect competition / commoditisation to compress it, the model overstates value.`,
    },
    {
      claim: 'A structural disruption is coming',
      detail: 'DCFs project historical trends. They can\'t price structural breaks — new technology, regulation, demand collapse.',
    },
  ]

  return (
    <section className="card decision-card">
      <h3 className="section-title">
        {headlinePhrase}
      </h3>
      <p className="section-copy">
        The model says <strong>{modelSays}</strong>, but the useful output is not the label.
        It is the list of assumptions that would make the market price reasonable.
      </p>
      <div className="belief-grid">
        {cards.map((card, i) => (
          <div key={i} className="belief-card">
            <div className="belief-number">{i + 1}</div>
            <div className="belief-claim">
              {card.claim}
            </div>
            <div className="belief-detail">
              {card.detail}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

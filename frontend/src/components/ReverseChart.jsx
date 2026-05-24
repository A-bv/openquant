import {
  BarChart, Bar, Cell, ReferenceLine,
  XAxis, YAxis, Tooltip, ResponsiveContainer, LabelList,
} from 'recharts'

const pct = v => v == null ? '—' : `${(v * 100).toFixed(1)}%`

// Recharts v3: custom tick must be a function ref, not JSX element
function CustomTick({ x, y, payload }) {
  const parts = payload.value.split('|')
  return (
    <g transform={`translate(${x},${y})`}>
      {parts.map((p, i) => (
        <text
          key={i}
          x={0}
          y={0}
          dy={14 + i * 13}
          textAnchor="middle"
          fill="#6B7280"
          fontSize={11}
        >
          {p}
        </text>
      ))}
    </g>
  )
}

// Recharts v3: content prop must be a function ref, not <Component />
function BarLabel({ x, y, width, value }) {
  if (value == null || isNaN(value)) return null
  const positive = value >= 0
  return (
    <text
      x={x + width / 2}
      y={positive ? y - 6 : y + 16}
      fill="#6B7280"
      textAnchor="middle"
      fontSize={11}
      fontWeight={500}
    >
      {Number(value).toFixed(1)}%
    </text>
  )
}

export default function ReverseChart({ revDcf }) {
  const {
    implied_growth, historical_median, historical_mean,
    revenue_cagr, gdp_growth,
  } = revDcf

  const data = [
    { name: 'Market-Implied|FCF Growth',  value: (implied_growth  ?? 0) * 100, raw: implied_growth,     implied: true },
    { name: 'Historical|Median FCF',      value: (historical_median ?? 0) * 100, raw: historical_median },
    { name: 'Historical|Mean FCF',        value: (historical_mean ?? 0) * 100,   raw: historical_mean },
    { name: 'Revenue|CAGR (5yr)',          value: (revenue_cagr    ?? 0) * 100,  raw: revenue_cagr },
    { name: 'Long-run|GDP Growth',        value: (gdp_growth      ?? 0.03) * 100, raw: gdp_growth ?? 0.03 },
  ]

  const impliedColor = (implied_growth ?? 0) >= (historical_median ?? 0) ? '#3B6D11' : '#A32D2D'

  return (
    <div style={{ width: '100%', height: 280 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 24, right: 24, left: 0, bottom: 50 }} barSize={52}>
          <XAxis
            dataKey="name"
            tick={CustomTick}
            interval={0}
            axisLine={false}
            tickLine={false}
            height={50}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#9CA3AF' }}
            axisLine={false}
            tickLine={false}
            tickFormatter={v => `${v}%`}
            width={42}
          />
          <Tooltip
            formatter={(_v, _n, { payload }) => [pct(payload.raw), '']}
            labelFormatter={l => l.replace('|', ' ')}
            contentStyle={{ border: '0.5px solid #E5E7EB', borderRadius: 8, fontSize: 12 }}
          />
          <ReferenceLine
            y={(historical_median ?? 0) * 100}
            stroke="#185FA5"
            strokeDasharray="4 3"
            strokeWidth={1.5}
            label={{
              value: `Historical median ${pct(historical_median)}`,
              position: 'insideTopRight',
              fontSize: 10,
              fill: '#185FA5',
            }}
          />
          <Bar dataKey="value" radius={[4, 4, 0, 0]}>
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.implied ? impliedColor : '#B4B2A9'} fillOpacity={0.9} />
            ))}
            <LabelList dataKey="value" content={BarLabel} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

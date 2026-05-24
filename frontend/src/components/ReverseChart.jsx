import { BarChart, Bar, Cell, ReferenceLine, XAxis, YAxis, Tooltip, ResponsiveContainer, LabelList } from 'recharts'

const pct = v => v == null ? '—' : `${(v * 100).toFixed(1)}%`

export default function ReverseChart({ revDcf }) {
  const { implied_growth, historical_median, historical_mean, revenue_cagr, gdp_growth } = revDcf

  const data = [
    { name: 'Market-Implied\nFCF Growth', value: (implied_growth || 0) * 100, raw: implied_growth, implied: true },
    { name: 'Historical\nMedian FCF',    value: (historical_median || 0) * 100, raw: historical_median },
    { name: 'Historical\nMean FCF',      value: (historical_mean || 0) * 100,   raw: historical_mean },
    { name: 'Revenue\nCAGR (5yr)',        value: (revenue_cagr || 0) * 100,      raw: revenue_cagr },
    { name: 'Long-run\nGDP Growth',      value: (gdp_growth || 0.03) * 100,     raw: gdp_growth || 0.03 },
  ]

  const impliedColor = (implied_growth || 0) >= (historical_median || 0) ? '#3B6D11' : '#A32D2D'

  const CustomLabel = ({ x, y, width, value }) => {
    const positive = value >= 0
    return (
      <text
        x={x + width / 2}
        y={positive ? y - 5 : y + 16}
        fill="#6B7280"
        textAnchor="middle"
        fontSize={11}
        fontWeight={500}
      >
        {value.toFixed(1)}%
      </text>
    )
  }

  return (
    <div style={{ width: '100%', height: 260 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 20, right: 20, left: 0, bottom: 40 }} barSize={48}>
          <XAxis
            dataKey="name"
            tick={{ fontSize: 11, fill: '#6B7280' }}
            interval={0}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#9CA3AF' }}
            axisLine={false}
            tickLine={false}
            tickFormatter={v => `${v}%`}
            width={40}
          />
          <Tooltip
            formatter={(v, n, p) => [`${p.payload.raw != null ? pct(p.payload.raw) : '—'}`, '']}
            labelStyle={{ fontSize: 12, color: '#111827' }}
            contentStyle={{ border: '0.5px solid #E5E7EB', borderRadius: 8, fontSize: 12 }}
          />
          <ReferenceLine
            y={(historical_median || 0) * 100}
            stroke="#185FA5"
            strokeDasharray="4 3"
            strokeWidth={1.5}
            label={{ value: `Historical median ${pct(historical_median)}`, position: 'right', fontSize: 10, fill: '#185FA5' }}
          />
          <Bar dataKey="value" radius={[4, 4, 0, 0]}>
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.implied ? impliedColor : '#B4B2A9'} fillOpacity={0.85} />
            ))}
            <LabelList content={<CustomLabel />} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

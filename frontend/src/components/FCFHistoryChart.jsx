import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, ReferenceLine, LabelList,
} from 'recharts'

function BarLabel({ x, y, width, value }) {
  if (value == null || isNaN(value)) return null
  const positive = value >= 0
  const b = (value / 1e9)
  return (
    <text
      x={x + width / 2}
      y={positive ? y - 5 : y + 14}
      textAnchor="middle"
      fill="#185FA5"
      fontSize={10}
      fontWeight={600}
    >
      {b >= 0 ? '' : '-'}${Math.abs(b).toFixed(1)}B
    </text>
  )
}

export default function FCFHistoryChart({ history, companyName }) {
  if (!history?.length) return null

  const data = history.map(d => ({ year: String(d.year), fcf: d.fcf }))

  // Compute a simple linear trend
  const n = data.length
  const xs = data.map((_, i) => i)
  const ys = data.map(d => d.fcf / 1e9)
  const xMean = xs.reduce((a, b) => a + b, 0) / n
  const yMean = ys.reduce((a, b) => a + b, 0) / n
  const slope = xs.reduce((s, x, i) => s + (x - xMean) * (ys[i] - yMean), 0)
    / xs.reduce((s, x) => s + (x - xMean) ** 2, 0)
  const intercept = yMean - slope * xMean

  const dataWithTrend = data.map((d, i) => ({
    ...d,
    trend: slope * i + intercept,
  }))

  const allPositive = data.every(d => d.fcf >= 0)
  const refY = allPositive ? undefined : 0

  return (
    <div>
      <div style={{ fontSize: 13, fontWeight: 600, color: '#111827', marginBottom: 8 }}>
        {companyName} — Free Cash Flow History
      </div>
      <div style={{ width: '100%', height: 240 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={dataWithTrend} margin={{ top: 24, right: 16, left: 0, bottom: 4 }} barSize={32}>
            <XAxis
              dataKey="year"
              tick={{ fontSize: 11, fill: '#9CA3AF' }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 11, fill: '#9CA3AF' }}
              axisLine={false}
              tickLine={false}
              tickFormatter={v => `$${(v / 1e9).toFixed(0)}B`}
              width={48}
              domain={['auto', 'auto']}
            />
            <Tooltip
              formatter={v => [`$${(v / 1e9).toFixed(1)}B`, 'FCF']}
              contentStyle={{ border: '0.5px solid #E5E7EB', borderRadius: 8, fontSize: 12 }}
            />
            {refY !== undefined && (
              <ReferenceLine y={0} stroke="#E5E7EB" strokeWidth={1} />
            )}
            <Bar dataKey="fcf" fill="#185FA5" fillOpacity={0.85} radius={[3, 3, 0, 0]}>
              <LabelList dataKey="fcf" content={BarLabel} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

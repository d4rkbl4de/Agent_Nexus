'use client'

import { memo, useMemo } from 'react'

type Bar = { label: string; value: number }

type BarChartProps = {
  data: Bar[]
  width?: number
  height?: number
  barColor?: string
  padding?: number
}

const BarChart = memo(function BarChart({
  data,
  width = 600,
  height = 240,
  barColor = 'currentColor',
  padding = 16
}: BarChartProps) {
  const computed = useMemo(() => {
    if (!data.length) return []

    const maxValue = Math.max(...data.map(d => d.value))
    const barWidth = (width - padding * 2) / data.length

    return data.map((d, i) => {
      const h = ((d.value / (maxValue || 1)) * (height - padding * 2))
      return {
        x: padding + i * barWidth,
        y: height - padding - h,
        width: barWidth * 0.8,
        height: h
      }
    })
  }, [data, width, height, padding])

  if (!data.length) {
    return <div style={{ width, height }} />
  }

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      {computed.map((b, i) => (
        <rect
          key={i}
          x={b.x}
          y={b.y}
          width={b.width}
          height={b.height}
          fill={barColor}
        />
      ))}
    </svg>
  )
})

export default BarChart

'use client'

import { memo, useMemo } from 'react'

type HeatCell = { x: number; y: number; value: number }

type HeatmapProps = {
  data: HeatCell[]
  rows: number
  cols: number
  width?: number
  height?: number
  minColor?: string
  maxColor?: string
}

const interpolateColor = (a: string, b: string, t: number) => {
  const pa = parseInt(a.slice(1), 16)
  const pb = parseInt(b.slice(1), 16)
  const r = Math.round(((pa >> 16) & 255) * (1 - t) + ((pb >> 16) & 255) * t)
  const g = Math.round(((pa >> 8) & 255) * (1 - t) + ((pb >> 8) & 255) * t)
  const bl = Math.round((pa & 255) * (1 - t) + (pb & 255) * t)
  return `rgb(${r},${g},${bl})`
}

const Heatmap = memo(function Heatmap({
  data,
  rows,
  cols,
  width = 600,
  height = 240,
  minColor = '#1e293b',
  maxColor = '#38bdf8'
}: HeatmapProps) {
  const computed = useMemo(() => {
    if (!data.length) return []

    const values = data.map(d => d.value)
    const min = Math.min(...values)
    const max = Math.max(...values)

    const cellWidth = width / cols
    const cellHeight = height / rows

    return data.map(d => {
      const t = (d.value - min) / (max - min || 1)
      return {
        x: d.x * cellWidth,
        y: d.y * cellHeight,
        w: cellWidth,
        h: cellHeight,
        color: interpolateColor(minColor, maxColor, t)
      }
    })
  }, [data, rows, cols, width, height, minColor, maxColor])

  if (!data.length) {
    return <div style={{ width, height }} />
  }

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      {computed.map((c, i) => (
        <rect
          key={i}
          x={c.x}
          y={c.y}
          width={c.w}
          height={c.h}
          fill={c.color}
        />
      ))}
    </svg>
  )
})

export default Heatmap

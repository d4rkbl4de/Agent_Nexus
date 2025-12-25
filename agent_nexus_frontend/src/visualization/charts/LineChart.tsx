'use client'

import { memo, useMemo } from 'react'

type Point = { x: number; y: number }

type LineChartProps = {
  data: Point[]
  width?: number
  height?: number
  stroke?: string
  strokeWidth?: number
  padding?: number
}

const LineChart = memo(function LineChart({
  data,
  width = 600,
  height = 240,
  stroke = 'currentColor',
  strokeWidth = 2,
  padding = 16
}: LineChartProps) {
  const { path, minX, maxX, minY, maxY } = useMemo(() => {
    if (!data.length) {
      return { path: '', minX: 0, maxX: 1, minY: 0, maxY: 1 }
    }

    const xs = data.map(d => d.x)
    const ys = data.map(d => d.y)

    const minX = Math.min(...xs)
    const maxX = Math.max(...xs)
    const minY = Math.min(...ys)
    const maxY = Math.max(...ys)

    const scaleX = (x: number) =>
      padding + ((x - minX) / (maxX - minX || 1)) * (width - padding * 2)
    const scaleY = (y: number) =>
      height - padding - ((y - minY) / (maxY - minY || 1)) * (height - padding * 2)

    const path = data
      .map((p, i) => `${i === 0 ? 'M' : 'L'} ${scaleX(p.x)} ${scaleY(p.y)}`)
      .join(' ')

    return { path, minX, maxX, minY, maxY }
  }, [data, width, height, padding])

  if (!data.length) {
    return <div style={{ width, height }} />
  }

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      <path
        d={path}
        fill="none"
        stroke={stroke}
        strokeWidth={strokeWidth}
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  )
})

export default LineChart

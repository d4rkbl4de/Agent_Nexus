"use client"

import { motion, MotionProps } from "framer-motion"
import { ReactNode } from "react"
import { resolveDuration } from "../tokens/duration"
import { resolveEasing } from "../tokens/easing"

type Direction = "up" | "down" | "left" | "right"

type SlideProps = {
  children: ReactNode
  in?: boolean
  direction?: Direction
  offset?: number
  duration?: number
  easing?: string | number[]
} & MotionProps

const axisMap: Record<Direction, { x?: number; y?: number }> = {
  up: { y: 1 },
  down: { y: -1 },
  left: { x: 1 },
  right: { x: -1 }
}

export default function Slide({
  children,
  in: visible = true,
  direction = "up",
  offset = 24,
  duration,
  easing,
  ...rest
}: SlideProps) {
  const axis = axisMap[direction]
  const initial = Object.fromEntries(
    Object.entries(axis).map(([k, v]) => [k, (v ?? 0) * offset])
  )

  return (
    <motion.div
      initial={{ opacity: 0, ...initial }}
      animate={{ opacity: visible ? 1 : 0, x: 0, y: 0 }}
      transition={{
        duration: resolveDuration(duration),
        ease: resolveEasing(easing)
      }}
      {...rest}
    >
      {children}
    </motion.div>
  )
}

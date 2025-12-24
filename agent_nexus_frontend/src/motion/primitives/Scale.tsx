"use client"

import { motion, MotionProps } from "framer-motion"
import { ReactNode } from "react"
import { resolveDuration } from "../tokens/duration"
import { resolveEasing } from "../tokens/easing"

type ScaleProps = {
  children: ReactNode
  in?: boolean
  from?: number
  to?: number
  duration?: number
  easing?: string | number[]
} & MotionProps

export default function Scale({
  children,
  in: visible = true,
  from = 0.95,
  to = 1,
  duration,
  easing,
  ...rest
}: ScaleProps) {
  return (
    <motion.div
      initial={{ scale: from, opacity: 0 }}
      animate={{
        scale: visible ? to : from,
        opacity: visible ? 1 : 0
      }}
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

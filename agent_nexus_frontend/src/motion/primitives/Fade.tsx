"use client"

import { motion, MotionProps } from "framer-motion"
import { ReactNode } from "react"
import { resolveDuration } from "../tokens/duration"
import { resolveEasing } from "../tokens/easing"

type FadeProps = {
  children: ReactNode
  in?: boolean
  from?: number
  to?: number
  duration?: number
  easing?: string | number[]
} & MotionProps

export default function Fade({
  children,
  in: visible = true,
  from = 0,
  to = 1,
  duration,
  easing,
  ...rest
}: FadeProps) {
  return (
    <motion.div
      initial={{ opacity: from }}
      animate={{ opacity: visible ? to : from }}
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

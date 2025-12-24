export type MotionSpeed =
  | "instant"
  | "fast"
  | "normal"
  | "slow"
  | "cinematic"

export const duration: Record<MotionSpeed, number> = {
  instant: 0,
  fast: 120,
  normal: 220,
  slow: 380,
  cinematic: 620
}

export const resolveDuration = (value?: MotionSpeed | number) => {
  if (typeof value === "number" && value >= 0) return value
  if (!value) return duration.normal
  return duration[value] ?? duration.normal
}

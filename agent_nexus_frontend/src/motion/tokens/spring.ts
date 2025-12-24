export type SpringPreset =
  | "snappy"
  | "smooth"
  | "bouncy"
  | "stiff"
  | "gentle"

export type SpringConfig = {
  type: "spring"
  stiffness: number
  damping: number
  mass: number
  velocity?: number
}

export const spring: Record<SpringPreset, SpringConfig> = {
  snappy: {
    type: "spring",
    stiffness: 420,
    damping: 28,
    mass: 0.8
  },
  smooth: {
    type: "spring",
    stiffness: 260,
    damping: 30,
    mass: 1
  },
  bouncy: {
    type: "spring",
    stiffness: 300,
    damping: 18,
    mass: 0.9
  },
  stiff: {
    type: "spring",
    stiffness: 520,
    damping: 40,
    mass: 0.7
  },
  gentle: {
    type: "spring",
    stiffness: 180,
    damping: 26,
    mass: 1.2
  }
}

export const resolveSpring = (
  value?: SpringPreset | Partial<SpringConfig>
): SpringConfig => {
  if (!value) return spring.smooth
  if (typeof value === "string") return spring[value] ?? spring.smooth
  return {
    type: "spring",
    stiffness: value.stiffness ?? spring.smooth.stiffness,
    damping: value.damping ?? spring.smooth.damping,
    mass: value.mass ?? spring.smooth.mass,
    velocity: value.velocity
  }
}

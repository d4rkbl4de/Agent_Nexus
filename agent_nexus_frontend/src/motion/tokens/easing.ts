export type Easing =
  | "linear"
  | "easeIn"
  | "easeOut"
  | "easeInOut"
  | "anticipate"
  | "circIn"
  | "circOut"
  | "circInOut"
  | "backIn"
  | "backOut"
  | "backInOut"

export const easing: Record<Easing, number[] | string> = {
  linear: "linear",
  easeIn: [0.4, 0.0, 1, 1],
  easeOut: [0.0, 0.0, 0.2, 1],
  easeInOut: [0.4, 0.0, 0.2, 1],
  anticipate: [0.68, -0.55, 0.265, 1.55],
  circIn: [0.55, 0.0, 1, 0.45],
  circOut: [0.0, 0.55, 0.45, 1],
  circInOut: [0.85, 0.0, 0.15, 1],
  backIn: [0.6, -0.28, 0.735, 0.045],
  backOut: [0.175, 0.885, 0.32, 1.275],
  backInOut: [0.68, -0.55, 0.265, 1.55]
}

export const resolveEasing = (value?: Easing | number[] | string) => {
  if (!value) return easing.easeInOut
  if (Array.isArray(value) || typeof value === "string") return value
  return easing[value] ?? easing.easeInOut
}

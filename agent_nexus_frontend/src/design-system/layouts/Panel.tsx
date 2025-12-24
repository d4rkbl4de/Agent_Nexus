import { forwardRef, ElementType, ReactNode } from "react"
import { clsx } from "clsx"

type PanelProps<T extends ElementType = "div"> = {
  as?: T
  padding?: number | string
  radius?: number | string
  elevation?: "none" | "sm" | "md" | "lg"
  bordered?: boolean
  interactive?: boolean
  children?: ReactNode
  className?: string
} & Omit<React.ComponentPropsWithoutRef<T>, "as" | "children">

const elevationMap = {
  none: "shadow-none",
  sm: "shadow-sm",
  md: "shadow-md",
  lg: "shadow-lg"
}

export const Panel = forwardRef<HTMLElement, PanelProps>((props, ref) => {
  const {
    as: Component = "div",
    padding = 16,
    radius = 12,
    elevation = "none",
    bordered = false,
    interactive = false,
    className,
    style,
    ...rest
  } = props

  const paddingValue = typeof padding === "number" ? `${padding}px` : padding
  const radiusValue = typeof radius === "number" ? `${radius}px` : radius

  return (
    <Component
      ref={ref}
      className={clsx(
        "bg-background",
        elevationMap[elevation],
        bordered && "border border-border",
        interactive && "transition-colors hover:bg-muted/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        className
      )}
      style={{
        padding: paddingValue,
        borderRadius: radiusValue,
        ...style
      }}
      {...rest}
    />
  )
})

Panel.displayName = "Panel"
export default Panel

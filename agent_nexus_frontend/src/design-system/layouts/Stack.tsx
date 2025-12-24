import { forwardRef, ElementType, ReactNode } from "react"
import { clsx } from "clsx"

type StackProps<T extends ElementType = "div"> = {
  as?: T
  direction?: "row" | "column"
  align?: "start" | "center" | "end" | "stretch" | "baseline"
  justify?: "start" | "center" | "end" | "between" | "around" | "evenly"
  gap?: number | string
  wrap?: boolean
  inline?: boolean
  children?: ReactNode
  className?: string
} & Omit<React.ComponentPropsWithoutRef<T>, "as" | "children">

const alignMap = {
  start: "items-start",
  center: "items-center",
  end: "items-end",
  stretch: "items-stretch",
  baseline: "items-baseline"
}

const justifyMap = {
  start: "justify-start",
  center: "justify-center",
  end: "justify-end",
  between: "justify-between",
  around: "justify-around",
  evenly: "justify-evenly"
}

export const Stack = forwardRef<HTMLElement, StackProps>((props, ref) => {
  const {
    as: Component = "div",
    direction = "column",
    align = "stretch",
    justify = "start",
    gap = 0,
    wrap = false,
    inline = false,
    className,
    style,
    ...rest
  } = props

  const gapValue = typeof gap === "number" ? `${gap}px` : gap

  return (
    <Component
      ref={ref}
      className={clsx(
        inline ? "inline-flex" : "flex",
        direction === "row" ? "flex-row" : "flex-col",
        alignMap[align],
        justifyMap[justify],
        wrap && "flex-wrap",
        className
      )}
      style={{ gap: gapValue, ...style }}
      {...rest}
    />
  )
})

Stack.displayName = "Stack"
export default Stack

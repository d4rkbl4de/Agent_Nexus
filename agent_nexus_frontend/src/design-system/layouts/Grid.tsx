import { forwardRef, ElementType, ReactNode } from "react"
import { clsx } from "clsx"

type GridProps<T extends ElementType = "div"> = {
  as?: T
  columns?: number | string
  rows?: number | string
  gap?: number | string
  align?: "start" | "center" | "end" | "stretch"
  justify?: "start" | "center" | "end" | "stretch"
  autoFlow?: "row" | "column" | "dense" | "row-dense" | "column-dense"
  children?: ReactNode
  className?: string
} & Omit<React.ComponentPropsWithoutRef<T>, "as" | "children">

const alignMap = {
  start: "items-start",
  center: "items-center",
  end: "items-end",
  stretch: "items-stretch"
}

const justifyMap = {
  start: "justify-items-start",
  center: "justify-items-center",
  end: "justify-items-end",
  stretch: "justify-items-stretch"
}

export const Grid = forwardRef<HTMLElement, GridProps>((props, ref) => {
  const {
    as: Component = "div",
    columns,
    rows,
    gap = 0,
    align = "stretch",
    justify = "stretch",
    autoFlow,
    className,
    style,
    ...rest
  } = props

  const gapValue = typeof gap === "number" ? `${gap}px` : gap

  return (
    <Component
      ref={ref}
      className={clsx("grid", alignMap[align], justifyMap[justify], className)}
      style={{
        gridTemplateColumns:
          typeof columns === "number" ? `repeat(${columns}, minmax(0, 1fr))` : columns,
        gridTemplateRows:
          typeof rows === "number" ? `repeat(${rows}, minmax(0, 1fr))` : rows,
        gridAutoFlow: autoFlow,
        gap: gapValue,
        ...style
      }}
      {...rest}
    />
  )
})

Grid.displayName = "Grid"
export default Grid

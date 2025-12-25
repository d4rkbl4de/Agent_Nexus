import * as React from 'react';
import * as ReactDOM from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useScheduler } from '../../motion/performance/scheduler';
import { assertExists } from '../../utils/assert';

type TooltipPosition = 'top' | 'bottom' | 'left' | 'right';

interface TooltipProps {
  label: React.ReactNode;
  children: React.ReactElement;
  position?: TooltipPosition;
  delay?: number; 
  className?: string;
}

interface PositionStyle {
  top?: number | string;
  bottom?: number | string;
  left?: number | string;
  right?: number | string;
  transform?: string;
  [key: string]: number | string | undefined; 
}

const Tooltip: React.FC<TooltipProps> = ({
  label,
  children,
  position = 'top',
  delay = 300,
  className = '',
}) => {
  const [isVisible, setIsVisible] = React.useState(false);
  const [coords, setCoords] = React.useState<PositionStyle>({});
  
  // Use MutableRefObject to explicitly allow ref assignment
  const triggerRef = React.useRef<HTMLElement | null>(null);
  const tooltipRef = React.useRef<HTMLDivElement>(null);
  const showTimeoutRef = React.useRef<number | null>(null);
  const { canRunAnimation } = useScheduler();

  const portalRoot = React.useMemo(() => document.body, []);
  assertExists(portalRoot, 'Document body must exist for portal creation.');

  const calculatePosition = React.useCallback(() => {
    if (!triggerRef.current || !tooltipRef.current) return;

    const triggerRect = triggerRef.current.getBoundingClientRect();
    const tooltipRect = tooltipRef.current.getBoundingClientRect();
    const scrollX = window.scrollX || window.pageXOffset;
    const scrollY = window.scrollY || window.pageYOffset;
    
    let style: PositionStyle = {};

    switch (position) {
      case 'top':
        style.top = triggerRect.top + scrollY - tooltipRect.height - 8;
        style.left = triggerRect.left + scrollX + (triggerRect.width / 2);
        style.transform = 'translateX(-50%)';
        break;
      case 'bottom':
        style.top = triggerRect.bottom + scrollY + 8;
        style.left = triggerRect.left + scrollX + (triggerRect.width / 2);
        style.transform = 'translateX(-50%)';
        break;
      case 'left':
        style.top = triggerRect.top + scrollY + (triggerRect.height / 2);
        style.left = triggerRect.left + scrollX - tooltipRect.width - 8;
        style.transform = 'translateY(-50%)';
        break;
      case 'right':
        style.top = triggerRect.top + scrollY + (triggerRect.height / 2);
        style.left = triggerRect.right + scrollX + 8;
        style.transform = 'translateY(-50%)';
        break;
      default:
        break;
    }

    setCoords(style);
  }, [position]);

  const handleShow = React.useCallback(() => {
    if (showTimeoutRef.current !== null) {
      window.clearTimeout(showTimeoutRef.current);
    }
    showTimeoutRef.current = window.setTimeout(() => {
      setIsVisible(true);
    }, delay);
  }, [delay]);

  const handleHide = React.useCallback(() => {
    if (showTimeoutRef.current !== null) {
      window.clearTimeout(showTimeoutRef.current);
      showTimeoutRef.current = null;
    }
    setIsVisible(false);
  }, []);

  React.useEffect(() => {
    if (isVisible) {
      const timeoutId = window.setTimeout(calculatePosition, 0); 
      
      const handleResizeScroll = canRunAnimation() ? calculatePosition : () => {};
      
      window.addEventListener('resize', handleResizeScroll);
      window.addEventListener('scroll', handleResizeScroll, true); 
      
      return () => {
        window.clearTimeout(timeoutId);
        window.removeEventListener('resize', handleResizeScroll);
        window.removeEventListener('scroll', handleResizeScroll, true);
      };
    }
  }, [isVisible, calculatePosition, canRunAnimation]);

  const childProps = children.props;
  
  // Refactor: Use a callback ref to handle both triggerRef and the child's ref
  const handleRef = React.useCallback((node: HTMLElement | null) => {
    triggerRef.current = node;
    const { ref } = children as any;
    if (typeof ref === 'function') {
      ref(node);
    } else if (ref) {
      ref.current = node;
    }
  }, [children]);

  const wrappedChildren = React.cloneElement(children, {
    ref: handleRef,
    onMouseEnter: (e: React.MouseEvent) => {
      handleShow();
      childProps.onMouseEnter?.(e);
    },
    onMouseLeave: (e: React.MouseEvent) => {
      handleHide();
      childProps.onMouseLeave?.(e);
    },
    onFocus: (e: React.FocusEvent) => {
      handleShow();
      childProps.onFocus?.(e);
    },
    onBlur: (e: React.FocusEvent) => {
      handleHide();
      childProps.onBlur?.(e);
    },
    'aria-describedby': isVisible ? 'tooltip-id-' + children.props.id : undefined,
  });

  const arrowClasses = 'absolute w-0 h-0 border-8 border-transparent';
  let arrowStyle: PositionStyle = {};

  switch (position) {
    case 'top':
      arrowStyle = { bottom: -16, left: '50%', transform: 'translateX(-50%)', borderTopColor: 'rgba(55, 65, 81, 1)' };
      break;
    case 'bottom':
      arrowStyle = { top: -16, left: '50%', transform: 'translateX(-50%)', borderBottomColor: 'rgba(55, 65, 81, 1)' };
      break;
    case 'left':
      arrowStyle = { right: -16, top: '50%', transform: 'translateY(-50%)', borderLeftColor: 'rgba(55, 65, 81, 1)' };
      break;
    case 'right':
      arrowStyle = { left: -16, top: '50%', transform: 'translateY(-50%)', borderRightColor: 'rgba(55, 65, 81, 1)' };
      break;
  }
  
  const tooltipContent = (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          ref={tooltipRef}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          transition={{ duration: 0.15 }}
          role="tooltip"
          id={'tooltip-id-' + children.props.id}
          style={{ ...coords, zIndex: 9999 }}
          className={`absolute pointer-events-none bg-gray-800 text-white text-xs px-3 py-1.5 rounded-lg shadow-xl ${className}`}
        >
          {label}
          <div className={arrowClasses} style={arrowStyle} />
        </motion.div>
      )}
    </AnimatePresence>
  );

  return (
    <>
      {wrappedChildren}
      {ReactDOM.createPortal(tooltipContent, portalRoot)}
    </>
  );
};

export default Tooltip;
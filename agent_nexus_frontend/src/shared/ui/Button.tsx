import * as React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { assert } from '../../utils/assert';
import { useReducedMotion } from '../../motion/accessibility/useReducedMotion';

type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost' | 'link';
type ButtonSize = 'sm' | 'md' | 'lg' | 'icon';

interface ButtonProps extends HTMLMotionProps<'button'> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  isDisabled?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  children?: React.ReactNode;
}

const baseStyles = 'inline-flex items-center justify-center font-medium transition-all duration-200 focus:outline-none focus:ring-4 disabled:opacity-50 disabled:cursor-not-allowed';

const sizeMap: Record<ButtonSize, string> = {
  sm: 'px-3 py-1.5 text-sm rounded-md',
  md: 'px-4 py-2 text-base rounded-lg',
  lg: 'px-6 py-3 text-lg rounded-xl',
  icon: 'p-2 rounded-full',
};

const variantMap: Record<ButtonVariant, string> = {
  primary: 'bg-indigo-600 text-white hover:bg-indigo-700 focus:ring-indigo-500/50 shadow-md',
  secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300 focus:ring-gray-400/50 border border-gray-300',
  danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500/50 shadow-md',
  ghost: 'bg-transparent text-gray-700 hover:bg-gray-100 focus:ring-gray-300/50 shadow-none',
  link: 'bg-transparent text-indigo-600 hover:text-indigo-800 focus:ring-indigo-300/50 shadow-none underline-offset-4',
};

const Button: React.FC<ButtonProps> = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      isLoading = false,
      isDisabled: propIsDisabled = false,
      leftIcon,
      rightIcon,
      children,
      className,
      ...rest
    },
    ref
  ) => {
    const shouldReduceMotion = useReducedMotion();
    const isDisabled = propIsDisabled || isLoading;

    assert(children || size === 'icon' || leftIcon || rightIcon, 'Button must have children, or be an icon button with an icon.');

    const classes = [
      baseStyles,
      sizeMap[size],
      variantMap[variant],
      className,
    ].filter(Boolean).join(' ');

    const iconClass = children ? 'w-4 h-4' : 'w-5 h-5';

    const animationProps = shouldReduceMotion ? {} : {
      whileTap: { scale: 0.98 },
      whileHover: { y: -1 },
    };
    
    // Simple spinner component optimized for integration
    const Spinner: React.FC = () => (
      <svg className={`animate-spin ${iconClass}`} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    );

    return (
      <motion.button
        ref={ref}
        className={classes}
        disabled={isDisabled}
        aria-busy={isLoading ? 'true' : 'false'}
        {...animationProps}
        {...rest}
      >
        {isLoading ? (
          <Spinner />
        ) : (
          <>
            {leftIcon && <span className={children ? 'mr-2' : ''}>{React.cloneElement(leftIcon as React.ReactElement, { className: iconClass })}</span>}
            {children}
            {rightIcon && <span className={children ? 'ml-2' : ''}>{React.cloneElement(rightIcon as React.ReactElement, { className: iconClass })}</span>}
          </>
        )}
      </motion.button>
    );
  }
);

Button.displayName = 'Button';

export default Button;
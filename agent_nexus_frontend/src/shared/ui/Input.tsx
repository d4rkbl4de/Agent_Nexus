import * as React from 'react';
import { assert } from '../../utils/assert';

type InputSize = 'sm' | 'md' | 'lg';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  size?: InputSize;
  isInvalid?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  errorMessage?: string;
  label?: string;
}

const sizeMap: Record<InputSize, string> = {
  sm: 'px-3 py-1.5 text-sm h-9',
  md: 'px-4 py-2 text-base h-11',
  lg: 'px-5 py-3 text-lg h-14',
};

const iconSizeMap: Record<InputSize, string> = {
  sm: 'w-4 h-4',
  md: 'w-5 h-5',
  lg: 'w-6 h-6',
};

const Input: React.FC<InputProps> = React.forwardRef<HTMLInputElement, InputProps>(
  (
    {
      size = 'md',
      isInvalid = false,
      leftIcon,
      rightIcon,
      errorMessage,
      label,
      className,
      id,
      ...rest
    },
    ref
  ) => {
    // Ensure an ID exists for proper accessibility linking with the label/error
    const inputId = id || React.useId();

    const baseClasses = 'block w-full border border-gray-300 rounded-lg placeholder-gray-400 focus:outline-none transition-all duration-200';
    const focusClasses = 'focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500';
    const invalidClasses = isInvalid 
      ? 'border-red-500 ring-2 ring-red-500/50 focus:border-red-500 focus:ring-red-500/50' 
      : focusClasses;

    const paddingLeft = leftIcon ? `pl-${size === 'sm' ? 9 : size === 'md' ? 10 : 12}` : '';
    const paddingRight = rightIcon ? `pr-${size === 'sm' ? 9 : size === 'md' ? 10 : 12}` : '';

    const inputClasses = [
      baseClasses,
      sizeMap[size],
      invalidClasses,
      paddingLeft,
      paddingRight,
      className,
    ].filter(Boolean).join(' ');

    const iconClasses = `absolute top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none ${iconSizeMap[size]}`;

    const iconOffset = {
      sm: 'left-3',
      md: 'left-3.5',
      lg: 'left-4',
    };

    return (
      <div className="flex flex-col w-full">
        {label && (
          <label htmlFor={inputId} className="mb-1 text-sm font-medium text-gray-700">
            {label}
          </label>
        )}
        <div className="relative">
          {leftIcon && (
            <span className={`${iconClasses} ${iconOffset[size]}`}>
              {React.cloneElement(leftIcon as React.ReactElement)}
            </span>
          )}
          
          <input
            ref={ref}
            id={inputId}
            className={inputClasses}
            aria-invalid={isInvalid}
            aria-describedby={isInvalid && errorMessage ? `${inputId}-error` : undefined}
            {...rest}
          />
          
          {rightIcon && (
            <span className={`${iconClasses} right-3`}>
              {React.cloneElement(rightIcon as React.ReactElement)}
            </span>
          )}
        </div>
        
        {isInvalid && errorMessage && (
          <p id={`${inputId}-error`} className="mt-1 text-sm text-red-600">
            {errorMessage}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
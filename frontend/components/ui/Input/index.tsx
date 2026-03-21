import React from 'react';
import type { InputProps } from './types';
import './styles.css';

/**
 * Input Component
 *
 * Warm inset styling with soft shadow on focus.
 * Supports icons, error states, and fluid widths.
 *
 * @example
 * <Input
 *   label="Email"
 *   type="email"
 *   placeholder="you@example.com"
 *   leftIcon={Mail}
 *   error="Invalid email format"
 * />
 */
export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      error,
      hint,
      size = 'md',
      leftIcon: LeftIcon,
      rightIcon: RightIcon,
      fullWidth = true,
      className = '',
      id,
      ...props
    },
    ref
  ) => {
    const inputId = id || `input-${React.useId()}`;

    const inputClasses = [
      'input',
      size !== 'md' && `input-${size}`,
      LeftIcon && 'input-with-left-icon',
      RightIcon && 'input-with-right-icon',
      error && 'input-error',
      fullWidth && 'input-full',
      className,
    ]
      .filter(Boolean)
      .join(' ');

    const wrapperClasses = ['input-wrapper', fullWidth && 'input-full']
      .filter(Boolean)
      .join(' ');

    const iconWrapperClasses = [
      'input-icon-wrapper',
      fullWidth && 'input-full',
    ]
      .filter(Boolean)
      .join(' ');

    return (
      <div className={wrapperClasses}>
        {label && (
          <label htmlFor={inputId} className="input-label">
            {label}
          </label>
        )}
        <div className={LeftIcon || RightIcon ? iconWrapperClasses : undefined}>
          {LeftIcon && (
            <LeftIcon size={16} className="input-icon-left" />
          )}
          <input ref={ref} id={inputId} className={inputClasses} {...props} />
          {RightIcon && (
            <RightIcon size={16} className="input-icon-right" />
          )}
        </div>
        {error && <span className="input-error-message">{error}</span>}
        {hint && !error && <span className="input-hint">{hint}</span>}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;

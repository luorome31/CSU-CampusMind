import React from 'react';
import type { ButtonProps } from './types';
import './styles.css';

/**
 * Button Component
 *
 * Warm minimal aesthetic with subtle lift on hover.
 * Touch-friendly with 44px minimum hit target.
 *
 * @example
 * <Button variant="primary" size="md" leftIcon={Plus}>
 *   Add Item
 * </Button>
 */
export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      isLoading = false,
      leftIcon: LeftIcon,
      rightIcon: RightIcon,
      fullWidth = false,
      children,
      className = '',
      disabled,
      ...props
    },
    ref
  ) => {
    const classes = [
      'btn',
      `btn-${variant}`,
      size !== 'md' && `btn-${size}`,
      fullWidth && 'btn-full',
      isLoading && 'btn-loading',
      className,
    ]
      .filter(Boolean)
      .join(' ');

    return (
      <button
        ref={ref}
        className={classes}
        disabled={disabled || isLoading}
        {...props}
      >
        {LeftIcon && <LeftIcon size={size === 'sm' ? 14 : 16} />}
        {children}
        {RightIcon && <RightIcon size={size === 'sm' ? 14 : 16} />}
      </button>
    );
  }
);

Button.displayName = 'Button';

export default Button;

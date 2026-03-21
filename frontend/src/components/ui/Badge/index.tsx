import React from 'react';
import type { BadgeProps } from './types';
import './styles.css';

/**
 * Badge Component
 *
 * Uppercase label badges for categorization.
 * Warm accent color palette.
 *
 * @example
 * <Badge variant="accent" size="md">New</Badge>
 */
export const Badge: React.FC<BadgeProps> = ({
  variant = 'default',
  size = 'md',
  children,
  className = '',
  ...props
}) => {
  const classes = [
    'badge',
    `badge-${variant}`,
    `badge-${size}`,
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <span className={classes} {...props}>
      {children}
    </span>
  );
};

Badge.displayName = 'Badge';

export default Badge;

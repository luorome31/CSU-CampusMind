import React from 'react';
import type { ChipProps } from './types';
import './styles.css';

/**
 * Chip Component
 *
 * Pill-style button for auth options and filters.
 * Warm muted palette with subtle hover states.
 *
 * @example
 * <Chip icon={Mail} variant="active">Email</Chip>
 */
export const Chip: React.FC<ChipProps> = ({
  variant = 'default',
  size = 'md',
  icon: Icon,
  children,
  className = '',
  ...props
}) => {
  const classes = [
    'chip',
    `chip-${size}`,
    variant !== 'default' && `chip-${variant}`,
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button type="button" className={classes} {...props}>
      {Icon && <Icon size={size === 'sm' ? 14 : 16} />}
      {children}
    </button>
  );
};

Chip.displayName = 'Chip';

export default Chip;

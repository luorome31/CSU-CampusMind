import React from 'react';
import type { CardProps, CardHeaderProps, CardBodyProps } from './types';
import './styles.css';

/**
 * Card Component
 *
 * Multiple variants: default, elevated, glass, auth (gradient border).
 * Responsive with mobile-optimized padding.
 *
 * @example
 * <Card variant="glass" padding="md">
 *   <CardHeader title="Welcome" subtitle="Getting started" />
 *   <CardBody>Content here</CardBody>
 * </Card>
 */
export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  (
    {
      variant = 'default',
      padding = 'md',
      children,
      className = '',
      ...props
    },
    ref
  ) => {
    const classes = [
      'card',
      `card-${variant}`,
      `card-padding-${padding}`,
      className,
    ]
      .filter(Boolean)
      .join(' ');

    return (
      <div ref={ref} className={classes} {...props}>
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';

/**
 * CardHeader Component
 */
export const CardHeader: React.FC<CardHeaderProps> = ({
  title,
  subtitle,
  action,
  children,
  className = '',
  ...props
}) => {
  const classes = ['card-header', className].filter(Boolean).join(' ');

  if (children) {
    return (
      <div className={classes} {...props}>
        {children}
      </div>
    );
  }

  return (
    <div className={classes} {...props}>
      <div className="flex items-center justify-between">
        {title && <h3 className="card-title">{title}</h3>}
        {action && <div className="card-action">{action}</div>}
      </div>
      {subtitle && <p className="card-subtitle">{subtitle}</p>}
    </div>
  );
};

CardHeader.displayName = 'CardHeader';

/**
 * CardBody Component
 */
export const CardBody: React.FC<CardBodyProps> = ({
  children,
  className = '',
  ...props
}) => {
  const classes = ['card-body', className].filter(Boolean).join(' ');

  return (
    <div className={classes} {...props}>
      {children}
    </div>
  );
};

CardBody.displayName = 'CardBody';

export default Card;

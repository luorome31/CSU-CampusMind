import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Card, CardHeader, CardBody } from './index';

describe('Card', () => {
  it('renders children', () => {
    render(<Card><p>Card content</p></Card>);
    expect(screen.getByText('Card content')).toBeInTheDocument();
  });

  it('renders card with card class', () => {
    render(<Card>Content</Card>);
    expect(document.querySelector('.card')).toBeInTheDocument();
  });

  it('applies variant class', () => {
    render(<Card variant="glass">Glass Card</Card>);
    const card = document.querySelector('.card');
    expect(card).toHaveClass('card-glass');
  });

  it('applies auth variant with gradient border', () => {
    render(<Card variant="auth">Auth Card</Card>);
    const card = document.querySelector('.card');
    expect(card).toHaveClass('card-auth');
  });

  it('applies padding class', () => {
    render(<Card padding="lg">Large Padding</Card>);
    const card = document.querySelector('.card');
    expect(card).toHaveClass('card-padding-lg');
  });

  it('merges custom className', () => {
    render(<Card className="custom-class">Custom</Card>);
    const card = document.querySelector('.card');
    expect(card).toHaveClass('custom-class');
  });

  it('forwards ref to the card element', () => {
    let ref: HTMLDivElement | null = null;
    render(
      <Card ref={(el) => { ref = el; }}>Ref Test</Card>
    );
    expect(ref).toBeInstanceOf(HTMLDivElement);
  });
});

describe('CardHeader', () => {
  it('renders title when provided', () => {
    render(<CardHeader title="Card Title" />);
    expect(screen.getByText('Card Title')).toBeInTheDocument();
  });

  it('renders subtitle when provided', () => {
    render(<CardHeader title="Title" subtitle="Card Subtitle" />);
    expect(screen.getByText('Card Subtitle')).toBeInTheDocument();
  });

  it('renders action element when provided', () => {
    render(<CardHeader title="Title" action={<button>Action</button>} />);
    expect(screen.getByRole('button', { name: 'Action' })).toBeInTheDocument();
  });

  it('renders children when provided instead of title/subtitle', () => {
    render(<CardHeader><span>Custom Header</span></CardHeader>);
    expect(screen.getByText('Custom Header')).toBeInTheDocument();
  });
});

describe('CardBody', () => {
  it('renders children', () => {
    render(<CardBody><p>Body content</p></CardBody>);
    expect(screen.getByText('Body content')).toBeInTheDocument();
  });

  it('applies card-body class', () => {
    render(<CardBody>Content</CardBody>);
    const body = document.querySelector('.card-body');
    expect(body).toHaveClass('card-body');
  });
});

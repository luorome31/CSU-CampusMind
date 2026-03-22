import React from 'react';
import { Badge } from '../components/ui/Badge';
import { Chip } from '../components/ui/Chip';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardHeader, CardBody } from '../components/ui/Card';
import { Mail, User, Lock, Check } from 'lucide-react';

/**
 * Full Components Showcase
 * Shows all reusable UI components standalone
 */
export const ComponentsShowcase: React.FC = () => {
  return (
    <div className="showcase">
      {/* Badges */}
      <section className="showcase-section">
        <h2 className="showcase-title">Badge</h2>
        <p className="showcase-desc">Uppercase labels for categorization</p>
        <div className="demo-row">
          <Badge variant="default">Default</Badge>
          <Badge variant="accent">Accent</Badge>
          <Badge variant="warm">Warm</Badge>
          <Badge variant="success">Success</Badge>
          <Badge variant="error">Error</Badge>
        </div>
        <div className="demo-row" style={{ marginTop: 'var(--space-3)' }}>
          <Badge variant="accent" size="sm">Small</Badge>
          <Badge variant="warm" size="sm">Warm Small</Badge>
        </div>
      </section>

      {/* Chips */}
      <section className="showcase-section">
        <h2 className="showcase-title">Chip</h2>
        <p className="showcase-desc">Pill-style selection controls</p>
        <div className="demo-row">
          <Chip icon={User}>Profile</Chip>
          <Chip icon={Mail}>Email</Chip>
          <Chip icon={Lock} variant="active">Active</Chip>
          <Chip icon={Check} variant="active">Selected</Chip>
          <Chip disabled>Disabled</Chip>
        </div>
      </section>

      {/* Buttons */}
      <section className="showcase-section">
        <h2 className="showcase-title">Button</h2>
        <p className="showcase-desc">Interactive action triggers</p>
        <div className="demo-row">
          <Button variant="primary">Primary</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="link">Link</Button>
        </div>
        <div className="demo-row" style={{ marginTop: 'var(--space-3)' }}>
          <Button size="sm">Small</Button>
          <Button size="lg">Large</Button>
          <Button isLoading>Loading</Button>
          <Button leftIcon={Check} variant="primary">With Icon</Button>
        </div>
        <div className="demo-row" style={{ marginTop: 'var(--space-3)' }}>
          <Button disabled>Disabled</Button>
          <Button fullWidth>Full Width</Button>
        </div>
      </section>

      {/* Inputs */}
      <section className="showcase-section">
        <h2 className="showcase-title">Input</h2>
        <p className="showcase-desc">Text entry fields</p>
        <div className="demo-stack">
          <Input label="Default" placeholder="Enter text..." leftIcon={User} />
          <Input label="With Error" placeholder="Invalid..." error="This field is required" />
          <Input label="Success" placeholder="Valid..." />
          <Input label="Disabled" placeholder="Cannot edit" disabled />
        </div>
      </section>

      {/* Cards */}
      <section className="showcase-section">
        <h2 className="showcase-title">Card</h2>
        <p className="showcase-desc">Content containers with multiple variants</p>
        <div className="cards-grid">
          <Card variant="default" padding="md">
            <CardHeader title="Default" subtitle="Standard surface" />
            <CardBody>
              <p className="card-text">Warm off-white background with subtle shadow and border.</p>
            </CardBody>
          </Card>
          <Card variant="elevated" padding="md">
            <CardHeader title="Elevated" subtitle="Floating effect" />
            <CardBody>
              <p className="card-text">More prominent shadow for emphasis.</p>
            </CardBody>
          </Card>
          <Card variant="glass" padding="md">
            <CardHeader title="Glass" subtitle="Frosted blur" />
            <CardBody>
              <p className="card-text">backdrop-filter blur with transparency.</p>
            </CardBody>
          </Card>
        </div>
      </section>

      <style>{`
        .showcase {
          padding: var(--space-6);
          max-width: 900px;
          margin: 0 auto;
        }

        .showcase-section {
          margin-bottom: var(--space-10);
          padding-bottom: var(--space-8);
          border-bottom: 1px solid var(--color-border);
        }

        .showcase-section:last-child {
          border-bottom: none;
        }

        .showcase-title {
          font-size: var(--text-xl);
          font-weight: var(--font-semibold);
          color: var(--color-text-primary);
          margin: 0 0 var(--space-1);
        }

        .showcase-desc {
          font-size: var(--text-sm);
          color: var(--color-text-tertiary);
          margin: 0 0 var(--space-4);
        }

        .demo-row {
          display: flex;
          flex-wrap: wrap;
          gap: var(--space-3);
          align-items: center;
        }

        .demo-stack {
          display: flex;
          flex-direction: column;
          gap: var(--space-4);
          max-width: 400px;
          width: 100%;
        }

        .cards-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
          gap: var(--space-4);
        }

        .card-text {
          font-size: var(--text-sm);
          color: var(--color-text-secondary);
          margin: 0;
          line-height: var(--leading-relaxed);
        }

        @media (max-width: 640px) {
          .showcase {
            padding: var(--space-4);
          }

          .cards-grid {
            grid-template-columns: 1fr;
          }

          .demo-stack {
            max-width: 100%;
          }
        }
      `}</style>
    </div>
  );
};

export default ComponentsShowcase;

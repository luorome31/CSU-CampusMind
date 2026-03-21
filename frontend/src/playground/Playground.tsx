import React, { useState } from 'react';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardHeader, CardBody } from '../components/ui/Card';
import { Chip } from '../components/ui/Chip';
import { ComponentsShowcase } from './ComponentsShowcase';
import { ColorPalette } from './ColorPalette';
import { Mail, Lock, User, Plus } from 'lucide-react';
import '../styles/tokens/colors.css';
import '../styles/tokens/spacing.css';
import '../styles/tokens/typography.css';
import '../styles/tokens/elevation.css';

/**
 * Design System Playground
 *
 * Interactive preview with viewport switching.
 * Demonstrates components at mobile (375px) and desktop (1440px).
 */
export const Playground: React.FC = () => {
  const [viewport, setViewport] = useState<'mobile' | 'desktop'>('desktop');
  const [activeTab, setActiveTab] = useState<'components' | 'preview' | 'tokens'>('components');

  const viewportWidth = viewport === 'mobile' ? 375 : 1440;
  const viewportLabel = viewport === 'mobile' ? '375px (Mobile)' : '1440px (Desktop)';

  return (
    <div className="playground">
      {/* Header */}
      <header className="playground-header">
        <div className="playground-title">
          <h1>Design System</h1>
          <Badge variant="accent">Warm Minimal</Badge>
        </div>
        <div className="playground-controls">
          <div className="viewport-switcher">
            <button
              className={`viewport-btn ${viewport === 'mobile' ? 'active' : ''}`}
              onClick={() => setViewport('mobile')}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="5" y="2" width="14" height="20" rx="2" ry="2"/>
                <line x1="12" y1="18" x2="12.01" y2="18"/>
              </svg>
              Mobile
            </button>
            <button
              className={`viewport-btn ${viewport === 'desktop' ? 'active' : ''}`}
              onClick={() => setViewport('desktop')}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                <line x1="8" y1="21" x2="16" y2="21"/>
                <line x1="12" y1="17" x2="12" y2="21"/>
              </svg>
              Desktop
            </button>
          </div>
          <Badge variant="default">{viewportLabel}</Badge>
        </div>
      </header>

      {/* Tab navigation */}
      <nav className="playground-tabs">
        {(['components', 'preview', 'tokens'] as const).map((tab) => (
          <button
            key={tab}
            className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </nav>

      {/* Preview area */}
      <div className="playground-viewport-wrapper">
        <div
          className="playground-viewport playground-full"
          style={{ width: activeTab === 'preview' ? viewportWidth : '100%' }}
        >
          <div className="viewport-content">
            {activeTab === 'components' && <ComponentsShowcase />}
            {activeTab === 'preview' && <ResponsivePreview />}
            {activeTab === 'tokens' && <ColorPalette />}
          </div>
        </div>
      </div>

      <style>{`
        .playground {
          min-height: 100vh;
          background: var(--color-bg-base);
          padding: var(--space-6);
        }

        .playground-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          max-width: 1200px;
          margin: 0 auto var(--space-6);
          flex-wrap: wrap;
          gap: var(--space-4);
        }

        .playground-title {
          display: flex;
          align-items: center;
          gap: var(--space-3);
        }

        .playground-title h1 {
          font-size: var(--text-2xl);
          font-weight: var(--font-semibold);
          color: var(--color-text-primary);
          margin: 0;
        }

        .playground-controls {
          display: flex;
          align-items: center;
          gap: var(--space-4);
        }

        .viewport-switcher {
          display: flex;
          background: var(--color-bg-surface);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          padding: var(--space-1);
        }

        .viewport-btn {
          display: flex;
          align-items: center;
          gap: var(--space-2);
          padding: var(--space-2) var(--space-3);
          border: none;
          background: transparent;
          color: var(--color-text-secondary);
          font-size: var(--text-sm);
          font-family: var(--font-sans);
          cursor: pointer;
          border-radius: var(--radius-md);
          transition: all var(--duration-fast);
        }

        .viewport-btn:hover {
          color: var(--color-text-primary);
        }

        .viewport-btn.active {
          background: var(--color-bg-elevated);
          color: var(--color-text-primary);
          box-shadow: var(--shadow-card);
        }

        .playground-tabs {
          display: flex;
          gap: var(--space-2);
          max-width: 1200px;
          margin: 0 auto var(--space-6);
          border-bottom: 1px solid var(--color-border);
          padding-bottom: var(--space-2);
        }

        .tab-btn {
          padding: var(--space-2) var(--space-4);
          border: none;
          background: transparent;
          color: var(--color-text-secondary);
          font-size: var(--text-sm);
          font-weight: var(--font-medium);
          font-family: var(--font-sans);
          cursor: pointer;
          border-radius: var(--radius-md) var(--radius-md) 0 0;
          transition: all var(--duration-fast);
        }

        .tab-btn:hover {
          color: var(--color-text-primary);
          background: rgba(0, 0, 0, 0.03);
        }

        .tab-btn.active {
          color: var(--color-text-primary);
          background: var(--color-bg-surface);
          border-bottom: 2px solid var(--color-accent);
        }

        .playground-viewport-wrapper {
          display: flex;
          justify-content: center;
          padding: var(--space-4);
          width: 100%;
        }

        .playground-viewport {
          background: white;
          border-radius: var(--radius-2xl);
          box-shadow: var(--shadow-elevated);
          transition: width var(--duration-slow) var(--ease-default);
          min-height: 400px;
          width: 100%;
        }

        .playground-full {
          width: 100%;
          max-width: 100%;
        }

        .viewport-content {
          padding: var(--space-6);
        }

        .demo-section {
          margin-bottom: var(--space-8);
        }

        .demo-section:last-child {
          margin-bottom: 0;
        }

        .demo-label {
          font-size: var(--text-xs);
          font-weight: var(--font-medium);
          text-transform: uppercase;
          letter-spacing: var(--tracking-label);
          color: var(--color-text-tertiary);
          margin-bottom: var(--space-3);
        }

        .demo-row {
          display: flex;
          flex-wrap: wrap;
          gap: var(--space-3);
          align-items: center;
        }

        .demo-col {
          display: flex;
          flex-direction: column;
          gap: var(--space-4);
          width: 100%;
        }

        /* Responsive adjustments */
        @media (max-width: 480px) {
          .playground {
            padding: var(--space-4);
          }

          .playground-header {
            flex-direction: column;
            align-items: flex-start;
          }

          .playground-controls {
            width: 100%;
            justify-content: space-between;
          }

          .viewport-content {
            padding: var(--space-4);
          }

          .demo-col {
            max-width: 100% !important;
          }
        }
      `}</style>
    </div>
  );
};

/** Responsive preview with all demos */
const ResponsivePreview: React.FC = () => {
  return (
    <div>
      <div className="demo-section">
        <p className="demo-label">Buttons</p>
        <div className="demo-row">
          <Button variant="primary">Primary</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="link">Link</Button>
          <Button variant="primary" size="sm">Small</Button>
          <Button variant="primary" size="lg">Large</Button>
          <Button variant="primary" isLoading>Loading</Button>
          <Button variant="primary" leftIcon={Plus}>With Icon</Button>
        </div>
      </div>

      <div className="demo-section">
        <p className="demo-label">Inputs</p>
        <div className="demo-col" style={{ maxWidth: '320px' }}>
          <Input label="Email" type="email" placeholder="you@example.com" leftIcon={Mail} />
          <Input label="Password" type="password" placeholder="Enter password" leftIcon={Lock} />
          <Input label="With Error" placeholder="Invalid input" error="This field is required" />
          <Input label="Disabled" placeholder="Cannot edit" disabled />
        </div>
      </div>

      <div className="demo-section">
        <p className="demo-label">Cards</p>
        <div className="demo-col" style={{ maxWidth: '400px' }}>
          <Card variant="default" padding="md">
            <CardHeader title="Default Card" subtitle="Standard surface with border" />
            <CardBody>
              <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)', margin: 0 }}>
                Warm off-white background with subtle shadow.
              </p>
            </CardBody>
          </Card>
          <Card variant="glass" padding="md">
            <CardHeader title="Glass Card" subtitle="Frosted glass effect" />
            <CardBody>
              <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)', margin: 0 }}>
                backdrop-filter blur with transparency.
              </p>
            </CardBody>
          </Card>
          <Card variant="elevated" padding="md">
            <CardHeader
              title="Elevated Card"
              subtitle="More prominent shadow"
              action={<Badge variant="accent" size="sm">New</Badge>}
            />
            <CardBody>
              <div className="demo-row" style={{ marginTop: 'var(--space-3)' }}>
                <Chip icon={User} variant="active">Profile</Chip>
                <Chip icon={Mail}>Email</Chip>
                <Chip icon={Lock}>Security</Chip>
              </div>
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Playground;

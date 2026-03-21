import React from 'react';

/**
 * Color Palette Reference
 * Visual reference for all design tokens
 */
export const ColorPalette: React.FC = () => {
  return (
    <div className="palette">
      <h1 className="palette-title">Design Tokens</h1>
      <p className="palette-subtitle">CampusMind Design System - Warm Minimal Aesthetic</p>

      {/* Background System */}
      <section className="palette-section">
        <h2 className="section-title">Background</h2>
        <div className="swatches">
          <ColorSwatch name="bg-base" var="--color-bg-base" hex="#f7f2ea" />
          <ColorSwatch name="bg-surface" var="--color-bg-surface" hex="rgba(255,255,255,0.82)" isTransparent />
          <ColorSwatch name="bg-elevated" var="--color-bg-elevated" hex="rgba(255,255,255,0.92)" isTransparent />
          <ColorSwatch name="bg-inset" var="--color-bg-inset" hex="#eee6dc" />
          <ColorSwatch name="bg-overlay" var="--color-bg-overlay" hex="rgba(255,255,255,0.6)" isTransparent />
        </div>
      </section>

      {/* Text System */}
      <section className="palette-section">
        <h2 className="section-title">Text</h2>
        <div className="swatches">
          <ColorSwatch name="text-primary" var="--color-text-primary" hex="#2d2a26" darkText />
          <ColorSwatch name="text-secondary" var="--color-text-secondary" hex="#5d5a55" darkText />
          <ColorSwatch name="text-tertiary" var="--color-text-tertiary" hex="#7e8b97" darkText />
          <ColorSwatch name="text-muted" var="--color-text-muted" hex="rgba(93,90,85,0.7)" isTransparent darkText />
        </div>
      </section>

      {/* Accent System */}
      <section className="palette-section">
        <h2 className="section-title">Accent</h2>
        <div className="swatches">
          <ColorSwatch name="accent" var="--color-accent" hex="#9fb1c2" />
          <ColorSwatch name="accent-light" var="--color-accent-light" hex="#c7ad96" />
          <ColorSwatch name="accent-hover" var="--color-accent-hover" hex="#d7c6ae" />
          <ColorSwatch name="accent-bg" var="--color-accent-bg" hex="rgba(159,177,194,0.2)" isTransparent />
        </div>
      </section>

      {/* Border System */}
      <section className="palette-section">
        <h2 className="section-title">Border</h2>
        <div className="swatches">
          <ColorSwatch name="border" var="--color-border" hex="rgba(45,42,38,0.12)" isTransparent darkText />
          <ColorSwatch name="border-hover" var="--color-border-hover" hex="rgba(159,177,194,0.5)" isTransparent darkText />
          <ColorSwatch name="border-subtle" var="--color-border-subtle" hex="rgba(45,42,38,0.08)" isTransparent darkText />
        </div>
      </section>

      {/* Status Colors */}
      <section className="palette-section">
        <h2 className="section-title">Status</h2>
        <div className="swatches">
          <ColorSwatch name="success" var="--color-success" hex="#1a7f37" />
          <ColorSwatch name="error" var="--color-error" hex="#cf222e" />
          <ColorSwatch name="warning" var="--color-warning" hex="#d29922" />
          <ColorSwatch name="info" var="--color-info" hex="#0969da" />
        </div>
      </section>

      {/* Typography Scale */}
      <section className="palette-section">
        <h2 className="section-title">Typography Scale</h2>
        <div className="type-scale">
          <TypeSample label="5xl (Hero)" size="var(--text-5xl)" sample="CampusMind" />
          <TypeSample label="4xl (Section)" size="var(--text-4xl)" sample="Design System" />
          <TypeSample label="3xl" size="var(--text-3xl)" sample="Components" />
          <TypeSample label="2xl" size="var(--text-2xl)" sample="Beautiful UI" />
          <TypeSample label="xl" size="var(--text-xl)" sample="Warm Minimal" />
          <TypeSample label="lg" size="var(--text-lg)" sample="Editorial aesthetic" />
          <TypeSample label="base" size="var(--text-base)" sample="Body text for reading" />
          <TypeSample label="sm" size="var(--text-sm)" sample="Secondary information" />
          <TypeSample label="xs" size="var(--text-xs)" sample="Labels and captions" />
        </div>
      </section>

      {/* Spacing Scale */}
      <section className="palette-section">
        <h2 className="section-title">Spacing Scale</h2>
        <div className="spacing-scale">
          <SpacingSample name="space-1" value="4px" size="0.25rem" />
          <SpacingSample name="space-2" value="8px" size="0.5rem" />
          <SpacingSample name="space-3" value="12px" size="0.75rem" />
          <SpacingSample name="space-4" value="16px" size="1rem" />
          <SpacingSample name="space-5" value="20px" size="1.25rem" />
          <SpacingSample name="space-6" value="24px" size="1.5rem" />
          <SpacingSample name="space-8" value="32px" size="2rem" />
          <SpacingSample name="space-10" value="40px" size="2.5rem" />
          <SpacingSample name="space-12" value="48px" size="3rem" />
        </div>
      </section>

      {/* Border Radius */}
      <section className="palette-section">
        <h2 className="section-title">Border Radius</h2>
        <div className="radius-scale">
          <RadiusSample name="sm" value="6px" radius="6px" />
          <RadiusSample name="md" value="8px" radius="8px" />
          <RadiusSample name="lg" value="12px" radius="12px" />
          <RadiusSample name="xl" value="16px" radius="16px" />
          <RadiusSample name="2xl" value="18px" radius="18px" />
          <RadiusSample name="full" value="9999px" radius="9999px" />
        </div>
      </section>

      {/* Shadows */}
      <section className="palette-section">
        <h2 className="section-title">Shadows</h2>
        <div className="shadow-showcase">
          <ShadowSample name="card" description="Default cards" shadow="var(--shadow-card)" />
          <ShadowSample name="card-hover" description="Hover state" shadow="var(--shadow-card-hover)" />
          <ShadowSample name="elevated" description="Floating elements" shadow="var(--shadow-elevated)" />
          <ShadowSample name="inset" description="Input fields" shadow="var(--shadow-inset)" isInset />
        </div>
      </section>

      <style>{`
        .palette {
          padding: var(--space-8);
          max-width: 1000px;
          margin: 0 auto;
          font-family: var(--font-sans);
        }

        .palette-title {
          font-size: var(--text-3xl);
          font-weight: var(--font-semibold);
          color: var(--color-text-primary);
          margin: 0 0 var(--space-2);
        }

        .palette-subtitle {
          font-size: var(--text-base);
          color: var(--color-text-secondary);
          margin: 0 0 var(--space-8);
        }

        .palette-section {
          margin-bottom: var(--space-10);
        }

        .section-title {
          font-size: var(--text-lg);
          font-weight: var(--font-semibold);
          color: var(--color-text-primary);
          margin: 0 0 var(--space-4);
          padding-bottom: var(--space-2);
          border-bottom: 1px solid var(--color-border);
        }

        .swatches {
          display: flex;
          flex-wrap: wrap;
          gap: var(--space-4);
        }

        .swatch {
          display: flex;
          flex-direction: column;
          gap: var(--space-2);
          min-width: 70px;
        }

        .swatch-color {
          width: 70px;
          height: 70px;
          border-radius: var(--radius-lg);
          border: 1px solid var(--color-border);
          position: relative;
          overflow: hidden;
        }

        .swatch-color.is-transparent {
          background-image: linear-gradient(45deg, #ccc 25%, transparent 25%),
                            linear-gradient(-45deg, #ccc 25%, transparent 25%),
                            linear-gradient(45deg, transparent 75%, #ccc 75%),
                            linear-gradient(-45deg, transparent 75%, #ccc 75%);
          background-size: 8px 8px;
          background-position: 0 0, 0 4px, 4px -4px, -4px 0px;
        }

        .swatch-color::after {
          content: '';
          position: absolute;
          inset: 0;
          border-radius: inherit;
        }

        .swatch-name {
          font-size: var(--text-xs);
          font-weight: var(--font-medium);
          color: var(--color-text-primary);
          font-family: var(--font-mono);
        }

        .swatch-hex {
          font-size: 10px;
          color: var(--color-text-tertiary);
          font-family: var(--font-mono);
        }

        /* Type Scale */
        .type-scale {
          display: flex;
          flex-direction: column;
          gap: var(--space-3);
        }

        .type-sample {
          display: flex;
          align-items: baseline;
          gap: var(--space-4);
        }

        .type-label {
          width: 100px;
          font-size: var(--text-xs);
          color: var(--color-text-tertiary);
          font-family: var(--font-mono);
          flex-shrink: 0;
        }

        .type-sample-text {
          color: var(--color-text-primary);
          line-height: 1.2;
        }

        /* Spacing Scale */
        .spacing-scale {
          display: flex;
          flex-direction: column;
          gap: var(--space-3);
        }

        .spacing-sample {
          display: flex;
          align-items: center;
          gap: var(--space-4);
        }

        .spacing-label {
          width: 80px;
          font-size: var(--text-xs);
          color: var(--color-text-tertiary);
          font-family: var(--font-mono);
          flex-shrink: 0;
        }

        .spacing-bar {
          height: 16px;
          background: var(--color-accent);
          border-radius: var(--radius-sm);
          opacity: 0.6;
        }

        .spacing-value {
          font-size: var(--text-xs);
          color: var(--color-text-secondary);
          font-family: var(--font-mono);
        }

        /* Radius Scale */
        .radius-scale {
          display: flex;
          flex-wrap: wrap;
          gap: var(--space-4);
        }

        .radius-sample {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: var(--space-2);
        }

        .radius-box {
          width: 60px;
          height: 60px;
          background: var(--color-accent);
          opacity: 0.5;
        }

        .radius-name {
          font-size: var(--text-xs);
          color: var(--color-text-tertiary);
          font-family: var(--font-mono);
        }

        /* Shadow Showcase */
        .shadow-showcase {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: var(--space-4);
        }

        .shadow-sample {
          padding: var(--space-4);
          background: var(--color-bg-surface);
          border-radius: var(--radius-lg);
          text-align: center;
        }

        .shadow-sample.is-inset {
          box-shadow: var(--shadow-inset);
        }

        .shadow-name {
          font-size: var(--text-sm);
          font-weight: var(--font-medium);
          color: var(--color-text-primary);
          margin: 0 0 var(--space-1);
        }

        .shadow-desc {
          font-size: var(--text-xs);
          color: var(--color-text-tertiary);
          margin: 0;
        }

        @media (max-width: 640px) {
          .palette {
            padding: var(--space-4);
          }

          .swatches {
            gap: var(--space-3);
          }

          .swatch {
            min-width: 60px;
          }

          .swatch-color {
            width: 60px;
            height: 60px;
          }

          .type-sample {
            flex-direction: column;
            gap: var(--space-1);
          }

          .type-label {
            width: auto;
          }

          .spacing-sample {
            flex-wrap: wrap;
          }

          .spacing-label {
            width: 70px;
          }

          .radius-scale {
            gap: var(--space-3);
          }

          .shadow-showcase {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

/** Color swatch component */
const ColorSwatch: React.FC<{
  name: string;
  var: string;
  hex: string;
  isTransparent?: boolean;
  darkText?: boolean;
}> = ({ name, var: varName, hex, isTransparent, darkText }) => (
  <div className="swatch">
    <div
      className={`swatch-color ${isTransparent ? 'is-transparent' : ''}`}
      style={{
        backgroundColor: isTransparent ? undefined : hex,
      }}
    >
      {isTransparent && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            borderRadius: 'inherit',
            backgroundColor: hex,
          }}
        />
      )}
    </div>
    <span className="swatch-name">{name}</span>
    <span className="swatch-hex">{hex}</span>
  </div>
);

/** Typography sample */
const TypeSample: React.FC<{
  label: string;
  size: string;
  sample: string;
}> = ({ label, size, sample }) => (
  <div className="type-sample">
    <span className="type-label">{label}</span>
    <span className="type-sample-text" style={{ fontSize: `var(${size})` }}>
      {sample}
    </span>
  </div>
);

/** Spacing sample */
const SpacingSample: React.FC<{
  name: string;
  value: string;
  size: string;
}> = ({ name, value, size }) => (
  <div className="spacing-sample">
    <span className="spacing-label">{name}</span>
    <div className="spacing-bar" style={{ width: size }} />
    <span className="spacing-value">{value}</span>
  </div>
);

/** Border radius sample */
const RadiusSample: React.FC<{
  name: string;
  value: string;
  radius: string;
}> = ({ name, value, radius }) => (
  <div className="radius-sample">
    <div className="radius-box" style={{ borderRadius: radius }} />
    <span className="radius-name">{name}</span>
    <span className="swatch-hex">{value}</span>
  </div>
);

/** Shadow sample */
const ShadowSample: React.FC<{
  name: string;
  description: string;
  shadow: string;
  isInset?: boolean;
}> = ({ name, description, shadow, isInset }) => (
  <div className={`shadow-sample ${isInset ? 'is-inset' : ''}`} style={isInset ? undefined : { boxShadow: shadow }}>
    {!isInset && (
      <div
        style={{
          width: '100%',
          height: '60px',
          background: 'var(--color-bg-surface)',
          borderRadius: 'var(--radius-lg)',
          marginBottom: 'var(--space-3)',
        }}
      />
    )}
    <p className="shadow-name">{name}</p>
    <p className="shadow-desc">{description}</p>
  </div>
);

export default ColorPalette;

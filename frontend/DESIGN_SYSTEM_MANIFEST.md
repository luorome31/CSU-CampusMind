# CampusMind Design System Manifest

## 1. Design Philosophy

**Aesthetic Name**: Warm Minimal / Soft Luxury

A refined, editorial aesthetic inspired by high-end research journals. Features warm cream tones with subtle glassmorphism accents and floating gradient orbs. The design conveys trustworthiness and sophistication without feeling cold or corporate.

**Core Principles**:
- Warm neutrals over cold grays
- Soft shadows over harsh edges
- Restrained motion over decorative animation
- Glassmorphism accents for depth
- Paper-like texture through subtle gradients

---

## 2. Foundations

### Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-bg-base` | `#f7f2ea` | Page background |
| `--color-bg-surface` | `rgba(255,255,255,0.82)` | Card surfaces |
| `--color-bg-elevated` | `rgba(255,255,255,0.92)` | Elevated elements |
| `--color-bg-inset` | `#eee6dc` | Inset/input backgrounds |
| `--color-text-primary` | `#2d2a26` | Headings, body text |
| `--color-text-secondary` | `#5d5a55` | Secondary text |
| `--color-text-tertiary` | `#7e8b97` | Placeholder, hints |
| `--color-accent` | `#9fb1c2` | Cool accent (blue-gray) |
| `--color-accent-light` | `#c7ad96` | Warm accent (tan) |
| `--color-border` | `rgba(45,42,38,0.12)` | Subtle borders |

### Typography

| Token | Value | Usage |
|-------|-------|-------|
| `--font-sans` | `DS-Project, system-ui` | Primary font |
| `--font-mono` | `IBM Plex Mono, monospace` | Code/mono |
| `--text-xs` | `0.75rem (12px)` | Labels, badges |
| `--text-sm` | `0.875rem (14px)` | Secondary text |
| `--text-base` | `1rem (16px)` | Body text |
| `--text-lg` | `1.125rem (18px)` | Subheadings |
| `--text-4xl` | `2.25rem → 2.5rem` | Section titles (fluid) |
| `--text-5xl` | `3rem → 3.5rem` | Hero titles (fluid) |

### Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| `--space-1` | `0.25rem (4px)` | Micro spacing |
| `--space-2` | `0.5rem (8px)` | Tight spacing |
| `--space-3` | `0.75rem (12px)` | Default gap |
| `--space-4` | `1rem (16px)` | Component padding |
| `--space-6` | `1.5rem (24px)` | Section gaps |
| `--space-8` | `2rem (32px)` | Large gaps |
| `--hit-target-min` | `2.75rem (44px)` | WCAG touch target |

### Elevation

| Token | Description |
|-------|-------------|
| `--shadow-card` | `0 1px 3px rgba(0,0,0,0.1)` - Default cards |
| `--shadow-elevated` | `0 12px 28px -14px rgba(45,42,38,0.55)` - Floating |
| `--shadow-inset` | `inset 2px 2px 6px rgba(150,140,128,0.15)` - Inputs |
| `--shadow-inset-focus` | Inset + 2px accent glow ring |

### Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-md` | `8px` | Buttons, inputs |
| `--radius-lg` | `12px` | Cards |
| `--radius-xl` | `16px` | Modals |
| `--radius-2xl` | `18px` | Auth cards |
| `--radius-full` | `9999px` | Pills, badges |

### Motion

| Token | Value |
|-------|-------|
| `--duration-fast` | `150ms` |
| `--duration-normal` | `200ms` |
| `--duration-slow` | `300ms` |
| `--ease-default` | `cubic-bezier(0.4, 0, 0.2, 1)` |
| `--ease-soft` | `cubic-bezier(0.25, 0.1, 0.25, 1)` |

---

## 3. Responsive Rules

### Breakpoints

| Name | Width | Usage |
|------|-------|-------|
| `sm` | `640px+` | Large phones, tablets |
| `md` | `768px+` | Tablets, small laptops |
| `lg` | `1024px+` | Laptops |
| `xl` | `1280px+` | Desktops |

### Mobile-First Strategy

1. Design for 375px first
2. Use `min-width` media queries for larger screens
3. Stack layouts on mobile, side-by-side on desktop
4. Hide non-essential elements on mobile
5. Use `100svh` for full-height sections

### Navigation Patterns

| Context | Mobile | Desktop |
|---------|--------|---------|
| Primary nav | Bottom tab bar or hamburger | Top header with inline links |
| Auth pages | Single column, hidden decorative | Two-column with decorative orbs |
| Cards | Full-width stack | Grid 2-3 columns |

### Touch Optimization

- Minimum tap target: 44x44px (`--hit-target-min`)
- Use `gap` instead of margins for touch spacing
- Consider `padding` over `margin` for interactive areas
- Test hover states with actual touch (hover is sticky on mobile)

---

## 4. AI Prompt Context (500 words)

**Style Summary for Future AI Generation**:

You are building components for CampusMind, a scientific productivity platform. The design aesthetic is "Warm Minimal" — refined and editorial like a high-end research journal, but approachable.

**Color Direction**: Warm cream backgrounds (#f7f2ea) with near-black warm text (#2d2a26). The primary accent is a muted blue-gray (#9fb1c2) that feels scientific yet soft. Secondary warm tan accent (#c7ad96). Avoid cold grays and pure blacks.

**Typography**: Use DS-Project font family with system-ui fallback. Font sizes follow a fluid scale from 12px to 36px (mobile) / 56px (desktop). Tight letter-spacing (-0.025em) for headings. Wide letter-spacing (0.16em) for labels/badges.

**Spatial System**: 4px base unit. Standard gaps are 8px, 12px, 16px, 24px. Component padding is typically 12px-16px. Section spacing is 32px-48px. Always ensure 44px minimum for touch targets.

**Shadows & Depth**: Prefer soft, warm shadows with blur (e.g., `0 12px 28px -14px rgba(45,42,38,0.55)`). Use inset shadows for inputs. Consider glassmorphism (backdrop-blur + semi-transparent white) for overlays.

**Borders**: Very subtle — typically `rgba(45,42,38,0.12)`. Rounded corners: 8px for inputs/buttons, 12-18px for cards.

**Motion**: Short and purposeful. 150-200ms for micro-interactions, 300ms for larger transitions. Use `cubic-bezier(0.4, 0, 0.2, 1)` for default easing. Avoid bounce or overshoot unless specifically needed.

**Component Patterns**:
- Buttons: Warm white backgrounds, subtle shadow, lift on hover
- Inputs: Inset shadow effect, focus ring with accent color
- Cards: Semi-transparent white or glass effect, soft shadow
- Badges: Pill-shaped, uppercase text, muted colors

**What to Avoid**:
- Pure white (#fff) backgrounds
- Hard black text (#000)
- Blue/purple gradients
- Inter, Roboto, or system default fonts
- Square corners or heavy borders
- Decorative motion or animations

---

## 5. File Structure

```
frontend/
├── styles/tokens/
│   ├── colors.css      # Color system
│   ├── spacing.css     # Spacing scale
│   ├── typography.css  # Type scale
│   └── elevation.css   # Shadows & motion
├── components/ui/
│   ├── Button/
│   │   ├── index.tsx
│   │   ├── types.ts
│   │   └── styles.css
│   ├── Input/
│   ├── Card/
│   ├── Badge/
│   └── Chip/
└── playground/
    └── Playground.tsx  # Interactive preview
```

---

## 6. Component Checklist

Before shipping any component, verify:

- [ ] Semantic HTML (button for buttons, label for labels)
- [ ] Keyboard navigable (focus-visible styles)
- [ ] 44px minimum touch target
- [ ] Color contrast meets WCAG AA (4.5:1 for text)
- [ ] No hardcoded colors (use CSS variables)
- [ ] No hardcoded pixel widths (use relative units)
- [ ] Responsive at 375px and 1440px
- [ ] Reduced motion respected (`prefers-reduced-motion`)
- [ ] Loading/disabled/error states handled

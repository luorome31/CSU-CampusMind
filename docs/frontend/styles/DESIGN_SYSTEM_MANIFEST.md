# CampusMind Design System Manifest

## 1. Design Philosophy

**Aesthetic Name**: Warm Paper + Blue-Grey Accent (温柔文具 Gentle Stationery)

A refined, editorial aesthetic inspired by high-end research journals. Features warm cream tones with subtle glassmorphism accents. The design conveys trustworthiness and sophistication without feeling cold or corporate.

**Core Principles**:
- Warm cream backgrounds over cold grays and pure white
- Soft diffused shadows over harsh edges
- Low-contrast harmony (no pure #000000 or #FFFFFF in text)
- Blue-gray accent (#537D96) for emphasis
- Physical spring animations for interactions
- Paper-like texture through subtle warmth

---

## 2. Foundations

### Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg` | `#F8F5ED` | Page background, warm cream |
| `--bg-card` | `#FCFAF5` | Card, bubble, popup surfaces |
| `--bg-glass` | `rgba(250,248,242,0.92)` | Glassmorphism/header overlay |
| `--sidebar-bg` | `#F4F2EA` | Sidebar background, slightly darker than content |
| `--bg-inset` | `#E8E5DD` | Inset/input backgrounds |
| `--text` | `#3B3D3F` | Primary text, high contrast |
| `--text-light` | `#6B6F73` | Secondary text |
| `--text-muted` | `#8E9196` | Placeholder, hints, timestamps |
| `--accent` | `#537D96` | Primary accent, blue-gray |
| `--accent-hover` | `#456A80` | Accent hover state |
| `--accent-light` | `rgba(83,125,150,0.08)` | Light accent background |
| `--border` | `rgba(83,125,150,0.22)` | Global unified border |
| `--shadow` | `rgba(59,61,63,0.09)` | Diffused shadow color |
| `--green` | `#7BAE7F` | Success state |
| `--coral` | `#EC8F8D` | Warning/alert/attention |

### Typography

| Token | Value | Usage |
|-------|-------|-------|
| `--font-sans` | `"DS-Project", system-ui` | Primary font |
| `--font-mono` | `"IBM Plex Mono", monospace` | Code/mono |
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
| `--shadow-card` | `0 4px 24px var(--shadow)` - Default cards |
| `--shadow-card-hover` | `0 8px 32px var(--shadow)` - Card hover |
| `--shadow-elevated` | `0 8px 32px var(--shadow)` - Floating elements |
| `--shadow-inset` | `inset 0 2px 4px rgba(59,61,63,0.08)` - Inputs |
| `--shadow-inset-focus` | Inset + 2px accent glow ring |

### Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-sm` | `6px` | Buttons, tags |
| `--radius-md` | `10px` | Inputs, card titles |
| `--radius-lg` | `16px` | Cards, panels, modals |
| `--radius-xl` | `18px` | Auth cards |
| `--radius-full` | `9999px` | Pills, badges |

### Motion

| Token | Value | Usage |
|-------|-------|-------|
| `--duration-fast` | `150ms` | Micro-interactions |
| `--duration-base` | `300ms` | Default transition, all interactive animations |
| `--duration-slow` | `400ms` | Large element transitions |
| `--ease-spring` | `cubic-bezier(0.16, 1, 0.3, 1)` | Physical spring, hover/expand |
| `--ease-default` | `cubic-bezier(0.4, 0, 0.2, 1)` | Standard easing |
| `--ease-soft` | `cubic-bezier(0.25, 0.1, 0.25, 1)` | Soft transition |

---

## 3. Responsive Rules

### Breakpoints

| Name | Width | Usage |
|------|-------|-------|
| `sm` | `640px+` | Large phones, tablets |
| `md` | `768px+` | Tablets, small laptops |
| `lg` | `1024px+` | Laptops |
| `xl` | `1280px+` | Desktops |

### Layout Widths

| Token | Value | Usage |
|-------|-------|-------|
| `--sidebar-width` | `240px` | Left sidebar width |
| `--preview-panel-width` | `580px` | Right context/preview panel |
| `--chat-min-width` | `400px` | Min width before sidebar collapse |

### Mobile-First Strategy

1. Design for 375px first
2. Use `min-width` media queries for larger screens
3. Stack layouts on mobile, side-by-side on desktop
4. Sidebar becomes drawer on mobile
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

You are building components for CampusMind, a scientific productivity platform. The design aesthetic is "Warm Paper + Blue-Grey Accent" — refined and editorial like a high-end research journal, but approachable.

**Color Direction**: Warm cream backgrounds (#F8F5ED) with warm gray text (#3B3D3F). The primary accent is a muted blue-gray (#537D96) that feels scientific yet soft. Avoid pure white (#fff) backgrounds and pure black (#000) text. The overall feel should be like quality stationery — warm, restrained, and tactile.

**Typography**: Use DS-Project font family with system-ui fallback. Font sizes follow a fluid scale from 12px to 36px (mobile) / 56px (desktop). Tight letter-spacing for headings. Wide letter-spacing for labels/badges.

**Spatial System**: 4px base unit. Standard gaps are 8px, 12px, 16px, 24px. Component padding is typically 12px-16px. Section spacing is 32px-48px. Always ensure 44px minimum for touch targets.

**Shadows & Depth**: Prefer soft, diffused shadows (e.g., `0 4px 24px rgba(59,61,63,0.09)`). Use inset shadows for inputs. Consider glassmorphism (backdrop-blur + semi-transparent white) for overlays.

**Borders**: Very subtle — typically `rgba(83,125,150,0.22)`. Rounded corners: 6px for buttons/tags, 10px for inputs, 16px for cards/modals.

**Motion**: Use physical spring easing `cubic-bezier(0.16, 1, 0.3, 1)` for all interactive animations. Duration is 300ms base. Avoid bounce or overshoot unless specifically needed. Respect `prefers-reduced-motion`.

**Component Patterns**:
- Buttons: Warm white/card backgrounds, subtle shadow, lift on hover with spring animation
- Inputs: Inset shadow effect, focus ring with accent color
- Cards: Card background (#FCFAF5), soft shadow, 16px radius
- Badges: Pill-shaped, uppercase text, muted colors
- Session items: Hover with subtle overlay, streaming dot indicator
- Chat bubbles: User uses accent-light background, AI uses card background

**What to Avoid**:
- Pure white (#fff) or pure black (#000) backgrounds
- High contrast text colors
- Blue/purple gradients
- Inter, Roboto, or system default fonts
- Square corners or heavy borders
- Decorative motion or animations
- Linear easing (avoid `ease-in`, `ease-out` alone)

---

## 5. File Structure

```
frontend/
├── index.html              # Business app entry
├── playground.html         # Design system preview entry
├── vite.config.ts         # Multi-entry Vite config
├── package.json
│   ├── npm run dev        # Business app (port 5173)
│   └── npm run playground # Design system (port 5174/playground.html)
├── src/
│   ├── main.tsx           # Business app bootstrap
│   ├── App.tsx            # Business app root component
│   ├── components/ui/     # Design system components
│   │   ├── Button/
│   │   │   ├── index.tsx
│   │   │   ├── types.ts
│   │   │   └── styles.css
│   │   ├── Input/
│   │   ├── Card/
│   │   ├── Badge/
│   │   ├── Chip/
│   │   └── index.ts       # Unified exports
│   ├── styles/tokens/     # Design tokens
│   │   ├── colors.css
│   │   ├── spacing.css
│   │   ├── typography.css
│   │   └── elevation.css
│   └── playground/
│       ├── main.tsx       # Playground bootstrap
│       ├── Playground.tsx  # Main playground component
│       ├── ComponentsShowcase.tsx
│       └── ColorPalette.tsx
└── docs/styles/
    └── DESIGN_SYSTEM_MANIFEST.md
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
- [ ] Interactive animations use `--ease-spring` with `--duration-base` (300ms)

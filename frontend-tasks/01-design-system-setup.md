# Frontend Task 01: Design System Setup

## Objective
Establish the foundational design system and CSS variables for the LiVin Matrix cyberpunk aesthetic.

## Description
Create the core design system files implementing the Obsidian-inspired cyberpunk color scheme, typography, and spacing system that will be used throughout the application.

## Requirements

### 1. CSS Custom Properties Setup
- Create `src/styles/design-system.css` with all color, typography, and spacing variables
- Implement the full Obsidian cyberpunk color palette:
  - Primary purple scale (--primary-50 to --primary-900)
  - Cyberpunk background system (pure black #000000 base)
  - Neon glow colors (purple, cyan, pink)
  - Functional colors (success, warning, error, info)
  - Matrix heatmap colors (negative, neutral, positive, strong)

### 2. Typography System
- Define font families: JetBrains Mono, Inter, Orbitron
- Set up text size scale (--text-xs to --text-4xl)
- Configure font weights (--font-thin to --font-extrabold)
- Add text glow effect variable (--text-glow)

### 3. Spacing and Layout
- Define space scale (--space-1 to --space-16)
- Set up border radius values (--radius-sm to --radius-xl)
- Create component sizing variables

### 4. Tailwind CSS Configuration
- Configure `tailwind.config.js` to use custom CSS variables
- Extend default theme with cyberpunk color palette
- Add custom font families
- Set up spacing scale extensions

## Acceptance Criteria
- [ ] All CSS custom properties defined in design-system.css
- [ ] Tailwind config properly extends theme with custom variables
- [ ] Font loading configured (Google Fonts or local)
- [ ] Design system variables accessible throughout app
- [ ] Color contrast meets WCAG AA standards (4.5:1 for normal text)

## Technical Notes
- Use CSS custom properties for runtime theme switching capability
- Ensure all colors have sufficient contrast against backgrounds
- Font fallbacks properly configured for cross-platform compatibility
- Design system should be imported in main App.css

## Files to Create
- `src/styles/design-system.css`
- `tailwind.config.js` (extend existing)
- `src/styles/fonts.css` (if using local fonts)

## Dependencies
- Tailwind CSS
- Google Fonts API (for Orbitron, Inter)
- JetBrains Mono font

## Estimated Time: 6-8 hours

## Priority: High
This is a foundational task that all other UI components will depend on.
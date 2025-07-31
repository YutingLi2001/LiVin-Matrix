# Frontend Task 02: Base UI Components

## Objective
Implement the foundational UI components (Button, Input, Card) with cyberpunk styling and proper TypeScript interfaces.

## Description
Create the core reusable UI components that will be used throughout the application, implementing the cyberpunk aesthetic with neon glow effects and proper accessibility features.

## Requirements

### 1. Button Component
```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'ghost' | 'danger';
  size: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  icon?: ReactNode;
  fullWidth?: boolean;
  children: ReactNode;
  onClick?: () => void;
}
```

**Visual Requirements:**
- Primary: Neon purple background (#8b5cf6), white text, hover glow effect
- Secondary: Transparent background, purple border, neon glow on hover
- Ghost: Text-only, purple background glow on hover
- Danger: Neon red variant for destructive actions
- Minimum click target: 44px × 44px (accessibility)
- Loading state with spinner animation
- Disabled state with reduced opacity

### 2. Input Component
```typescript
interface InputProps {
  type: 'text' | 'number' | 'email' | 'password' | 'time';
  placeholder?: string;
  label?: string;
  error?: string;
  helper?: string;
  prefix?: ReactNode;
  suffix?: ReactNode;
  value?: string;
  onChange?: (value: string) => void;
  disabled?: boolean;
}
```

**Visual Requirements:**
- Pure black background with purple border
- Focus state: neon purple glow (0 0 8px var(--neon-purple))
- Error state: neon red border and glow
- Label: Inter Medium 14px, purple accent color
- Purple glowing cursor
- Proper ARIA labels and descriptions

### 3. Card Component
```typescript
interface CardProps {
  variant: 'default' | 'elevated' | 'outlined';
  padding: 'sm' | 'md' | 'lg';
  interactive?: boolean;
  children: ReactNode;
  onClick?: () => void;
}
```

**Visual Requirements:**
- Background: --bg-secondary (dark black #0a0a0a)
- Border: 1px solid rgba(139, 92, 246, 0.3)
- Hover state (if interactive): purple neon glow border
- Border radius: --radius-lg
- Optional backdrop-filter blur for glass effect
- Smooth transitions for all hover states

## Acceptance Criteria
- [ ] All three components implemented with proper TypeScript interfaces
- [ ] Cyberpunk styling matches design specification
- [ ] Components are fully accessible (WCAG AA)
- [ ] Hover and focus states with neon glow effects
- [ ] Loading and disabled states properly handled
- [ ] Components work across different screen sizes
- [ ] Storybook stories created for each component (optional but recommended)

## Technical Notes
- Use forwardRef for proper ref forwarding
- Implement proper focus management
- Use CSS-in-JS or CSS modules for component styling
- Ensure all interactive elements are keyboard accessible
- Add proper ARIA attributes for screen readers

## Files to Create
- `src/components/ui/Button.tsx`
- `src/components/ui/Input.tsx`
- `src/components/ui/Card.tsx`
- `src/components/ui/index.ts` (barrel exports)
- Component-specific CSS files or styled-components

## Dependencies
- React 18+
- TypeScript
- Tailwind CSS (configured in Task 01)
- Lucide React (for icons)

## Testing Requirements
- Unit tests for each component
- Accessibility tests with @testing-library/jest-dom
- Visual regression tests (if Chromatic is set up)

## Estimated Time: 12-16 hours

## Priority: High
These components are building blocks for all other UI elements.
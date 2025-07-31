# Frontend Task 04: Matrix Heatmap Component

## Objective
Implement the core 6x6 correlation matrix heatmap visualization with cyberpunk styling and interactive features.

## Description
Create the central data visualization component that displays correlation relationships between the six life dimensions using a cyberpunk-styled heatmap with neon colors and interactive elements.

## Requirements

### 1. MatrixHeatmap Component Interface
```typescript
interface MatrixHeatmapProps {
  data: CorrelationMatrix;
  dimensions: string[];
  onCellClick: (rowIndex: number, colIndex: number) => void;
  timeRange: 'week' | 'month' | 'quarter' | 'all';
  loading?: boolean;
}

interface CorrelationMatrix {
  values: number[][]; // 6x6 matrix of correlation values (-1 to 1)
  labels: string[];   // Dimension names
}
```

### 2. Visual Requirements

#### Color Coding System
- **Negative Correlation (-1 to -0.3):** Neon red (#ff0066)
- **Weak Correlation (-0.3 to 0.3):** Dark gray (#404040)
- **Positive Correlation (0.3 to 1):** Neon green (#00ff88)
- **Strong Correlation (>0.7 or <-0.7):** Main purple (#8b5cf6) with glow

#### Matrix Styling
- 6x6 grid with equal cell sizes
- Cell borders: thin purple glow lines
- Hover effects: neon glow border + tooltip
- Cell click: pulse animation + selection state
- Responsive sizing: scales down on mobile

### 3. Interactive Features

#### Hover Effects
- Cell highlight with neon border glow
- Tooltip showing:
  - Correlation coefficient value
  - Relationship strength description
  - Dimension pair names
- Row/column highlighting (subtle)

#### Click Interactions
- Cell selection state with persistent highlight
- Multiple cell selection support (Ctrl+click)
- Callback to parent component with cell data
- Smooth pulse animation on click

### 4. Responsive Design
- **Desktop:** Full 6x6 matrix, optimal cell size
- **Tablet:** Reduced cell size, scrollable if needed
- **Mobile:** Compact view with smaller cells, touch-optimized

### 5. Loading States
- Skeleton animation with cyberpunk styling
- Shimmer effect with purple accent
- Maintains layout during data loading

## Acceptance Criteria
- [ ] 6x6 matrix renders correctly with correlation data
- [ ] Color coding matches cyberpunk design specification
- [ ] Hover effects work smoothly with neon glow
- [ ] Click interactions trigger proper callbacks
- [ ] Tooltip displays correlation information clearly
- [ ] Responsive design works across all screen sizes
- [ ] Loading state provides good user feedback
- [ ] Accessibility features (keyboard navigation, ARIA labels)
- [ ] Smooth animations don't impact performance

## Technical Notes
- Use SVG or Canvas for precise rendering control
- Consider using D3.js for data-to-visual mapping
- Alternative: CSS Grid with styled divs for simpler implementation
- Optimize for 60fps animations
- Use requestAnimationFrame for smooth hover effects

## Files to Create
- `src/components/charts/MatrixHeatmap.tsx`
- `src/components/charts/MatrixCell.tsx`
- `src/components/charts/MatrixTooltip.tsx`
- `src/utils/colorScale.ts` (correlation to color mapping)
- `src/types/matrix.ts` (TypeScript interfaces)

## Dependencies
- Recharts or D3.js (for data visualization)
- React (for component structure)
- Tailwind CSS (for styling)

## Testing Requirements
- Unit tests for color mapping functions
- Integration tests for hover and click interactions
- Visual regression tests for matrix appearance
- Performance tests for smooth animations
- Accessibility tests (keyboard navigation, screen readers)

## Data Requirements
- Mock correlation matrix data for development
- Proper error handling for invalid data
- Support for empty/loading states

## Performance Considerations
- Debounce hover effects to prevent excessive re-renders
- Use CSS transforms for animations instead of layout changes
- Consider virtualization for very large matrices (future enhancement)
- Optimize tooltip rendering to prevent memory leaks

## Estimated Time: 20-24 hours

## Priority: High
This is the core visualization component of the entire application.
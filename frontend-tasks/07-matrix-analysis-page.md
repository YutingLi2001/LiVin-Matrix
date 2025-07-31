# Frontend Task 07: Matrix Analysis Page

## Objective
Implement the comprehensive matrix analysis interface with full correlation visualization, time controls, and detailed data exploration features.

## Description
Create the dedicated analysis page that houses the complete 6x6 matrix visualization with advanced interaction capabilities, time range filtering, dimension selection, and detailed data drill-down features.

## Requirements

### 1. MatrixAnalysisPage Component
```typescript
interface MatrixAnalysisPageProps {
  initialTimeRange?: TimeRange;
  initialDimensions?: string[];
}
```

### 2. Page Layout Structure

#### Top Controls Bar
- Time range selector (Day/Week/Month/Quarter/All)
- Dimension visibility toggles
- Export options (future feature placeholder)
- Reset/clear selections button

#### Main Matrix Area
- Full 6x6 correlation heatmap (from Task 04)
- Enhanced with selection states
- Multi-select capabilities (Ctrl+click)
- Keyboard navigation support

#### Right Panel: Details Drawer
- Selected cell(s) information
- Correlation strength interpretation
- Historical trend for selected relationship
- Recommendations or insights (placeholder)

#### Bottom Panel: Time Series (expandable)
- Dual-axis chart showing both dimensions over time
- Highlight correlation periods
- Interactive brushing for time selection

### 3. TimeRangeSelector Component
```typescript
interface TimeRangeSelectorProps {
  value: TimeRange;
  onChange: (range: TimeRange) => void;
  loading?: boolean;
}

type TimeRange = 'day' | 'week' | 'month' | 'quarter' | 'all';
```

**Features:**
- Cyberpunk-styled tab interface
- Active state with neon glow
- Loading indicators during data fetch
- Keyboard accessibility

### 4. DimensionToggle Component
```typescript
interface DimensionToggleProps {
  dimensions: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
}
```

**Features:**
- Checkbox-style toggles with cyberpunk styling
- "Select All" / "Clear All" functionality
- Visual feedback for dimension visibility
- Maintains at least 2 dimensions selected

### 5. CorrelationDetailsPanel Component
```typescript
interface CorrelationDetailsPanelProps {
  selectedCells: MatrixCell[];
  correlationData: CorrelationData;
  onClose: () => void;
}

interface MatrixCell {
  row: number;
  col: number;
  value: number;
  dimensions: [string, string];
}
```

**Features:**
- Slide-in panel with cyberpunk glass effect
- Correlation interpretation (strong, moderate, weak)
- Historical data visualization
- Actionable insights or suggestions

### 6. Interactive Features

#### Matrix Interactions
- Single click: Select cell, show details
- Ctrl+click: Multi-select cells
- Drag selection: Select rectangular area (advanced)
- Keyboard navigation: Arrow keys + Enter
- Hover: Preview tooltip with basic info

#### Time Controls
- Smooth data transitions when changing time range
- Loading states during data fetching
- Comparison mode (show before/after)
- Animation of correlation changes over time

#### Data Export (Placeholder)
- Export correlation matrix as CSV
- Export visualization as PNG
- Share analysis link (future feature)

## Acceptance Criteria
- [ ] Full matrix analysis page with all control components
- [ ] Time range selector updates matrix data correctly
- [ ] Dimension toggles show/hide matrix rows/columns
- [ ] Cell selection shows detailed information panel
- [ ] Multi-select functionality works properly
- [ ] Keyboard navigation throughout the interface
- [ ] Smooth transitions between different time ranges
- [ ] Responsive design adapts to smaller screens
- [ ] Loading states provide clear feedback
- [ ] Error handling for data fetch failures
- [ ] Accessibility compliance for complex interface

## Technical Notes
- Use URL parameters to maintain state on page refresh
- Implement proper state management for complex interactions
- Consider using React Query for data caching
- Optimize for performance with large datasets
- Use proper focus management for accessibility

## Files to Create
- `src/pages/MatrixAnalysisPage.tsx`
- `src/components/analysis/TimeRangeSelector.tsx`
- `src/components/analysis/DimensionToggle.tsx`
- `src/components/analysis/CorrelationDetailsPanel.tsx`
- `src/components/analysis/TimeSeries.tsx`
- `src/hooks/useMatrixAnalysis.ts`
- `src/utils/correlationUtils.ts`

## Dependencies
- Recharts (for time series charts)
- React Router (for URL state management)
- React Query (for data management)
- Framer Motion (for panel animations)

## Data Requirements
- Comprehensive correlation matrix data
- Time-series data for dimension pairs
- Statistical significance data
- Historical correlation trends
- Mock insights and recommendations

## Styling Requirements
- Cyberpunk control panel styling
- Neon glow effects for active states
- Glass effect for details panel
- Smooth transitions and animations
- Consistent spacing and typography

## Performance Considerations
- Debounce time range changes to prevent excessive API calls
- Memoize expensive correlation calculations
- Use virtual scrolling for large datasets (if needed)
- Optimize chart re-rendering with proper dependencies

## Testing Requirements
- Integration tests for matrix interaction flows
- Unit tests for correlation calculation utilities
- Accessibility tests for complex keyboard navigation
- Performance tests for smooth interactions
- Visual regression tests for different time ranges

## Advanced Features (Future)
- Correlation prediction/forecasting
- Statistical significance indicators
- Anomaly detection highlighting
- Correlation strength audio feedback
- Advanced filtering and search

## Estimated Time: 22-26 hours

## Priority: High
Core analytical interface that provides primary value proposition.
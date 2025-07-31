# Frontend Task 06: Dashboard and Metrics Components

## Objective
Implement the main dashboard with key metrics cards, trend visualizations, and matrix preview components.

## Description
Create the central dashboard that provides users with an at-a-glance view of their life metrics, featuring cyberpunk-styled metric cards, trend charts, and a simplified matrix preview.

## Requirements

### 1. MetricCard Component
```typescript
interface MetricCardProps {
  title: string;
  value: number | string;
  unit?: string;
  trend?: 'up' | 'down' | 'stable';
  trendValue?: number;
  sparkline?: number[];
  loading?: boolean;
  variant?: 'default' | 'highlighted';
}
```

**Visual Requirements:**
- Title: Inter Medium 14px, silver-gray (#b4b4b4)
- Value: JetBrains Mono Bold 24px, white with subtle glow
- Trend indicators: Neon green (up), neon red (down), gray (stable)
- Sparkline: Micro chart with purple accent color
- Cyberpunk card styling with neon border

### 2. Dashboard Layout

#### Top Section: Key Metrics Grid (4 columns)
- **Overall Wellbeing Score:** Calculated aggregate metric
- **Sleep Quality:** Average sleep rating
- **Energy Level:** Current energy trend
- **Productivity Index:** Daily productivity score

#### Middle Section: Matrix Preview
- Simplified 3x3 or 6x6 matrix view
- Click-through to full Matrix Analysis page
- Shows strongest correlations with highlights
- Loading state with cyberpunk shimmer

#### Bottom Section: Recent Trends
- Mini charts showing 7-day trends for each dimension
- Interactive hover effects
- Quick insights and notable changes

### 3. TrendChart Component
```typescript
interface TrendChartProps {
  data: DataPoint[];
  dimension: string;
  timeRange: 'week' | 'month';
  height?: number;
  showAxis?: boolean;
  color?: string;
}

interface DataPoint {
  date: string;
  value: number;
}
```

**Features:**
- Recharts line chart with cyberpunk styling
- Neon purple gradient fills
- Hover tooltips with data details
- Responsive sizing for different layouts

### 4. Dashboard Container
```typescript
interface DashboardProps {
  userId?: string;
  timeRange?: 'week' | 'month';
}
```

**Responsive Behavior:**
- **Desktop:** 4-column metric grid
- **Tablet:** 2-column metric grid
- **Mobile:** 1-column stacked layout

## Acceptance Criteria
- [ ] MetricCard displays values with proper cyberpunk styling
- [ ] Trend indicators work with proper color coding
- [ ] Matrix preview links to full analysis page
- [ ] Mini trend charts render correctly with Recharts
- [ ] Responsive grid layout adapts to screen sizes
- [ ] Loading states provide good user feedback
- [ ] Dashboard updates when new data is available
- [ ] Hover effects and interactions feel smooth
- [ ] Performance is good with multiple charts
- [ ] Accessibility features for data visualization

## Technical Notes
- Use CSS Grid for responsive metric card layout
- Implement proper loading skeleton states
- Consider using React Query for data fetching
- Optimize chart rendering performance
- Use memoization to prevent unnecessary re-renders

## Files to Create
- `src/components/dashboard/Dashboard.tsx`
- `src/components/dashboard/MetricCard.tsx`
- `src/components/dashboard/MatrixPreview.tsx`
- `src/components/charts/TrendChart.tsx`
- `src/components/charts/SparklineChart.tsx`
- `src/hooks/useDashboardData.ts`
- `src/utils/metricCalculations.ts`

## Dependencies
- Recharts (for trend charts)
- React Query (for data management)
- date-fns (for date formatting)
- Lucide React (for trend icons)

## Data Requirements
- Mock data for all metric types
- Calculation functions for derived metrics
- Proper error handling for missing data
- Loading states for async data fetching

## Styling Requirements
- Cyberpunk metric card styling
- Neon glow effects on hover
- Purple accent colors for charts
- Consistent spacing and typography
- Smooth animations for state changes

## Performance Considerations
- Lazy load trend charts if they're below the fold
- Debounce hover effects on metric cards
- Use CSS transforms for smooth animations
- Optimize chart re-rendering with proper keys

## Testing Requirements
- Unit tests for metric calculation functions
- Integration tests for dashboard data flow
- Visual tests for responsive behavior
- Performance tests for chart rendering
- Accessibility tests for data visualization

## Integration Points
- Links to Matrix Analysis page
- Links to Data Entry forms
- Real-time updates when data changes
- Proper error boundaries for chart failures

## Estimated Time: 18-22 hours

## Priority: High
Primary user interface that demonstrates app value immediately.
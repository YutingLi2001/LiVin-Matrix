# Frontend Task 05: Data Entry Forms System

## Objective
Implement the comprehensive data entry form system for all six life dimensions with cyberpunk styling and optimized user experience.

## Description
Create the data input interface that allows users to quickly record daily metrics across sleep, nutrition, exercise, mood, productivity, and social dimensions. The system should be keyboard-optimized and completable in 3-4 minutes.

## Requirements

### 1. Core Form Components

#### DimensionInput Component
```typescript
interface DimensionInputProps {
  dimension: 'sleep' | 'nutrition' | 'exercise' | 'mood' | 'productivity' | 'social';
  values: Record<string, any>;
  onChange: (values: Record<string, any>) => void;
  collapsed?: boolean;
  onToggle?: () => void;
}
```

#### RatingInput Component
```typescript
interface RatingInputProps {
  value: number;
  onChange: (value: number) => void;
  max: number;
  icon?: 'star' | 'circle' | 'heart';
  size: 'sm' | 'md' | 'lg';
  color?: string;
  label: string;
}
```

### 2. Six Dimension Forms

#### 1. Sleep Dimension (Target: 30 seconds)
**Fields:**
- Sleep duration (hours:minutes picker)
- Sleep quality (1-5 rating)
- Bedtime (time picker)
- Wake time (time picker)
- Sleep disruptions (quick checkboxes)

#### 2. Nutrition Dimension (Target: 45 seconds)
**Fields:**
- Meals quality (1-5 rating)
- Water intake (glasses counter)
- Fruits/vegetables (portions counter)
- Energy level (1-5 rating)
- Cravings (quick tags)

#### 3. Exercise Dimension (Target: 60-90 seconds)
**Fields:**
- Workout type (dropdown/tags)
- Duration (minutes input)
- Intensity (1-5 rating)
- Steps (number input with optional sync)
- Recovery feeling (1-5 rating)

#### 4. Mood Dimension (Target: 30 seconds)
**Fields:**
- Overall mood (1-5 rating)
- Stress level (1-5 rating)
- Anxiety level (1-5 rating)
- Emotional tags (quick select)

#### 5. Productivity Dimension (Target: 45 seconds)
**Fields:**
- Focus level (1-5 rating)
- Tasks completed (counter)
- Work satisfaction (1-5 rating)
- Distractions (1-5 rating, inverted)
- Deep work hours (number input)

#### 6. Social Dimension (Target: 30 seconds)
**Fields:**
- Social interactions (counter)
- Relationship satisfaction (1-5 rating)
- Social energy (1-5 rating)
- Meaningful conversations (counter)

### 3. Form Features

#### Collapsible Card Layout
- Each dimension in a separate card
- Expand/collapse functionality
- Progress indicators showing completion
- Smooth cyberpunk animations

#### Smart Defaults and Templates
- Pre-filled values based on user patterns
- Quick templates for common scenarios
- "Copy from yesterday" functionality

#### Keyboard Optimization
- Tab navigation through all inputs
- Enter to submit section
- Escape to collapse cards
- Number key shortcuts for ratings

## Acceptance Criteria
- [ ] All six dimension forms implemented and functional
- [ ] Collapsible card layout with smooth animations
- [ ] Keyboard navigation optimized for speed
- [ ] Form validation with cyberpunk error styling
- [ ] Smart defaults and template system
- [ ] Progress indicators for completion tracking
- [ ] Responsive design for tablet/mobile
- [ ] Form state persistence (local storage)
- [ ] 3-4 minute completion target achievable
- [ ] Accessibility compliance (WCAG AA)

## Technical Notes
- Use React Hook Form for form state management
- Implement proper form validation with Yup or Zod
- Use local storage for draft persistence
- Consider using a step-by-step wizard approach
- Optimize for both mouse and keyboard users

## Files to Create
- `src/components/forms/DimensionInput.tsx`
- `src/components/forms/RatingInput.tsx`
- `src/components/forms/DataEntryForm.tsx`
- `src/components/forms/dimensions/` (folder with individual dimension components)
  - `SleepForm.tsx`
  - `NutritionForm.tsx`
  - `ExerciseForm.tsx`
  - `MoodForm.tsx`
  - `ProductivityForm.tsx`
  - `SocialForm.tsx`
- `src/hooks/useFormPersistence.ts`
- `src/utils/formValidation.ts`

## Dependencies
- React Hook Form
- Yup or Zod (validation)
- date-fns (for time/date handling)
- Lucide React (icons)

## Styling Requirements
- Cyberpunk card styling with neon accents
- Purple glow effects on focus states
- Error states with neon red styling
- Progress indicators with animated fills
- Smooth expand/collapse animations

## Testing Requirements
- Form validation tests for each dimension
- Keyboard navigation flow tests
- Persistence functionality tests
- Responsive behavior tests
- Performance tests for smooth animations

## Performance Considerations
- Debounce form auto-save functionality
- Optimize re-renders with proper memoization
- Use CSS transforms for animations
- Lazy load dimension components if needed

## Estimated Time: 24-28 hours

## Priority: High
Core functionality for daily user interaction with the application.
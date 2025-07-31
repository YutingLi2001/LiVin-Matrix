# Frontend Task 08: State Management Architecture

## Objective
Implement the global state management system using React Context and useReducer for handling application state, user data, and UI interactions.

## Description
Set up a scalable state management architecture that handles user data, analysis state, UI state, and data persistence while maintaining good performance and developer experience.

## Requirements

### 1. Global State Structure
```typescript
interface AppState {
  user: UserState;
  data: DataState;
  analysis: AnalysisState;
  ui: UIState;
}

interface UserState {
  profile: UserProfile | null;
  preferences: UserPreferences;
  isAuthenticated: boolean;
}

interface DataState {
  records: UserRecord[];
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
  isDirty: boolean; // Has unsaved changes
}

interface AnalysisState {
  correlationMatrix: CorrelationMatrix | null;
  selectedTimeRange: TimeRange;
  selectedDimensions: string[];
  selectedCells: MatrixCell[];
  insights: Insight[];
  loading: boolean;
}

interface UIState {
  sidebarOpen: boolean;
  activeModal: string | null;
  notifications: Notification[];
  theme: 'cyberpunk'; // Future: support multiple themes
}
```

### 2. Context Providers Setup

#### AppProvider (Root Provider)
```typescript
const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Combines all context providers
  // Handles provider composition
}
```

#### Individual Context Files
- `UserContext.tsx` - User authentication and profile
- `DataContext.tsx` - User records and data management
- `AnalysisContext.tsx` - Matrix analysis state
- `UIContext.tsx` - Interface state and interactions

### 3. Reducer Functions

#### DataReducer
```typescript
type DataAction = 
  | { type: 'FETCH_DATA_START' }
  | { type: 'FETCH_DATA_SUCCESS'; payload: UserRecord[] }
  | { type: 'FETCH_DATA_ERROR'; payload: string }
  | { type: 'ADD_RECORD'; payload: UserRecord }
  | { type: 'UPDATE_RECORD'; payload: { id: string; updates: Partial<UserRecord> } }
  | { type: 'DELETE_RECORD'; payload: string }
  | { type: 'MARK_DIRTY' }
  | { type: 'MARK_CLEAN' };
```

#### AnalysisReducer
```typescript
type AnalysisAction =
  | { type: 'SET_TIME_RANGE'; payload: TimeRange }
  | { type: 'TOGGLE_DIMENSION'; payload: string }
  | { type: 'SELECT_CELL'; payload: MatrixCell }
  | { type: 'CLEAR_SELECTION' }
  | { type: 'SET_CORRELATION_MATRIX'; payload: CorrelationMatrix }
  | { type: 'SET_LOADING'; payload: boolean };
```

### 4. Custom Hooks

#### Data Management Hooks
```typescript
const useUserData = () => {
  // Returns user records, loading state, error handling
  // Provides functions: addRecord, updateRecord, deleteRecord
};

const useDataEntry = () => {
  // Specialized hook for data entry forms
  // Provides: saveRecord, getDraftData, clearDraft
};
```

#### Analysis Hooks
```typescript
const useMatrixAnalysis = () => {
  // Returns analysis state and control functions
  // Provides: setTimeRange, toggleDimension, selectCell
};

const useCorrelations = (timeRange: TimeRange, dimensions: string[]) => {
  // Calculates correlations based on current data
  // Returns: correlationMatrix, loading, error
};
```

#### UI Hooks
```typescript
const useUI = () => {
  // Controls UI state: sidebar, modals, notifications
  // Provides: openSidebar, closeSidebar, showNotification
};
```

### 5. Local Storage Integration

#### Persistence Layer
```typescript
const usePersistence = () => {
  // Handles saving/loading state to localStorage
  // Provides: saveState, loadState, clearStorage
};
```

**Persistence Strategy:**
- Draft data entries (auto-save every 10 seconds)
- User preferences and settings
- Analysis view preferences (time range, selected dimensions)
- UI state (sidebar preferences, theme settings)

### 6. Error Handling

#### Error Boundaries
- Global error boundary for unhandled exceptions
- Context-specific error handling
- User-friendly error messages with cyberpunk styling

#### Error State Management
```typescript
interface ErrorState {
  message: string;
  type: 'network' | 'validation' | 'system';
  timestamp: Date;
  dismissable: boolean;
}
```

## Acceptance Criteria
- [ ] All context providers properly set up and composed
- [ ] Reducers handle all necessary actions correctly
- [ ] Custom hooks provide clean API for components
- [ ] Local storage persistence works reliably
- [ ] Error handling provides good user experience
- [ ] State updates trigger proper re-renders
- [ ] Performance is good (no excessive re-renders)
- [ ] TypeScript types are comprehensive and correct
- [ ] State can be debugged easily in development

## Technical Notes
- Use React DevTools for state debugging
- Implement proper action creators for consistency
- Consider using Immer for immutable state updates
- Use proper dependency arrays in useEffect hooks
- Implement proper cleanup for subscriptions

## Files to Create
- `src/context/AppProvider.tsx`
- `src/context/UserContext.tsx`
- `src/context/DataContext.tsx`
- `src/context/AnalysisContext.tsx`
- `src/context/UIContext.tsx`
- `src/reducers/dataReducer.ts`
- `src/reducers/analysisReducer.ts`
- `src/hooks/useUserData.ts`
- `src/hooks/useDataEntry.ts`
- `src/hooks/useMatrixAnalysis.ts`
- `src/hooks/useCorrelations.ts`
- `src/hooks/useUI.ts`
- `src/hooks/usePersistence.ts`
- `src/utils/localStorage.ts`
- `src/types/state.ts`

## Dependencies
- React (Context API, useReducer)
- TypeScript (for type safety)
- Immer (optional, for immutable updates)

## Performance Considerations
- Split contexts to prevent unnecessary re-renders
- Use React.memo for expensive components
- Implement proper selector patterns
- Consider using useMemo for derived state
- Debounce expensive operations

## Testing Requirements
- Unit tests for all reducers
- Integration tests for context providers
- Tests for custom hooks
- Tests for localStorage persistence
- Performance tests for state updates

## Development Tools
- React DevTools integration
- State logging in development mode
- Action type checking with TypeScript
- Clear error messages for debugging

## Migration Strategy
- Start with basic state structure
- Gradually migrate existing useState calls
- Test each context provider individually
- Ensure backward compatibility during transition

## Estimated Time: 16-20 hours

## Priority: High
Foundation for all other components and data flow throughout the application.
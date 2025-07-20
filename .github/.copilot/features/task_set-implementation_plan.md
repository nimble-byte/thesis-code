# Task Set Feature Implementation Plan

## Overview
Implement functionality to show all tasks of a given task set sequentially. Each set consists of 3 tasks shown one at a time, with navigation between them using a "Next Task" button positioned in the bottom right.

## Curre### Step 7: Update Individual Task Page (Optional) ✅ COMPLETED
**File**: `/src/app/tasks/[index]/page.tsx`

**Status**: ✅ Implemented Option A - Successfully refactored to use TaskComponent for consistency and code reduction.

**Changes Made**:
- ✅ Replaced 30+ lines of duplicated task display logic with single TaskComponent usage
- ✅ Eliminated duplicate radio button handling, image display, and styling code
- ✅ Maintained identical functionality and appearance
- ✅ Added TaskComponent import
- ✅ Removed unused `selected` state and display logic
- ✅ Preserved existing URL structure and API calls

**Benefits Achieved**:
- ✅ **Code Consistency**: Both individual and set views now use the same component
- ✅ **Maintainability**: Single source of truth for task display logic
- ✅ **Bug Reduction**: Fixes and improvements apply to both views automatically
- ✅ **Reduced Code Duplication**: Eliminated ~30 lines of duplicated logic
- ✅ **Future-Proof**: New TaskComponent features automatically available in both viewste Analysis
- Application currently shows individual tasks by `pid` via `/tasks/[index]` route
- Each task in the dataset has a `set` field (`"set1"`, `"set2"`, `"backup"`)
- Each set contains exactly 3 tasks
- Tasks are identified by unique `pid` values
- Existing task display component works well and should be reused

## Implementation Steps

### Step 1: Update Question Type Interface ✅ COMPLETED
**File**: `/src/types/question.ts`

**Action**: Add missing fields to match the actual data structure

**Status**: ✅ Implemented - Updated interface to include `difficulty` and `set` fields, and changed `img_height` and `img_width` from string to number types to match the actual data structure.

```typescript
export interface Question {
  pid: string;
  question: string;
  image: string;
  choices: string[];
  answer: string;
  img_height: number;      // Change from string to number
  img_width: number;       // Change from string to number
  difficulty: string;      // Add this field
  set: string;            // Add this field
}
```

### Step 2: Create Task Set API Endpoint ✅ COMPLETED
**File**: `/src/app/api/sets/[setName]/route.ts` (new)

**Purpose**: Provide API to fetch all tasks for a specific set

**Status**: ✅ Implemented and tested - API endpoint successfully created and returning correct responses for task sets.

**Implementation**:
- Import existing `getQuestions()` function
- Filter questions by set name
- Return array of questions for the set
- Handle error cases (invalid set name, no questions found)

```typescript
import { NextRequest } from "next/server";
import { getQuestions } from "../../questions/questions";

export async function GET(_req: NextRequest, { params }: { params: Promise<{ setName: string }> }): Promise<Response> {
  try {
    const questions = getQuestions();
    const { setName } = await params;
    const setQuestions = questions.filter((q) => q.set === setName);

    if (setQuestions.length === 0) {
      return new Response(JSON.stringify({ error: "Invalid set name or no questions found" }), { status: 404 });
    }

    return new Response(JSON.stringify(setQuestions), { status: 200 });
  } catch (err: any) {
    return new Response(JSON.stringify({ error: "Failed to load questions", details: String(err) }), { status: 500 });
  }
}
```

### Step 3: Extract Reusable Task Component ✅ COMPLETED
**File**: `/src/components/TaskComponent.tsx` (new)

**Purpose**: Extract task display logic from individual task page for reuse

**Status**: ✅ Implemented - Created reusable TaskComponent that accepts Question as prop and maintains the same styling and functionality as the original task page.

**Features**:
- Accept `Question` as prop instead of fetching internally
- Handle answer selection state internally
- Provide callback for answer changes (optional)
- Maintain existing styling and functionality
- Support custom task numbering via `taskNumber` prop

```typescript
"use client";
import React, { useState } from 'react';
import type { Question } from '../types/question';

interface TaskComponentProps {
  question: Question;
  taskNumber?: number;
  onAnswerChange?: (selected: string) => void;
}

export default function TaskComponent({ question, taskNumber, onAnswerChange }: TaskComponentProps) {
  const [selected, setSelected] = useState<string | null>(null);

  const handleSelectionChange = (value: string) => {
    setSelected(value);
    onAnswerChange?.(value);
  };

  const imageUrl = `/images/${question.image}`;
  const displayTitle = taskNumber ? `Question ${taskNumber}` : `Question ${question.pid}`;

  return (
    <div style={{ maxWidth: 500, margin: '2rem auto', padding: 16, border: '1px solid #eeeeee', borderRadius: 8 }}>
      <h1 style={{ marginBottom: 16, textAlign: 'center', fontSize: '1.5rem' }}>{displayTitle}</h1>
      <img src={imageUrl} alt="Task" style={{ width: '100%', objectFit: 'contain', marginBottom: 24 }} />
      <h2 style={{ marginBottom: 16 }}>{question.question}</h2>
      <form>
        {question.choices.map((opt, idx) => (
          <div key={idx} style={{ marginBottom: 12 }}>
            <label>
              <input
                type="radio"
                name="answer"
                value={opt}
                checked={selected === opt}
                onChange={() => handleSelectionChange(opt)}
                style={{ marginRight: 8 }}
              />
              {opt}
            </label>
          </div>
        ))}
      </form>
    </div>
  );
}
```

### Step 4: Create Task Set Page Component ✅ COMPLETED
**File**: `/src/app/sets/[setName]/page.tsx` (new)

**Purpose**: Main page component for displaying task sets with navigation

**Status**: ✅ Implemented - Created complete Task Set page with progress tracking, navigation, and completion handling.

**Features**:
- Fetch all tasks for the specified set using the new API
- Track current task index with state management
- Display current task using TaskComponent
- Show "Next Task" button in bottom right (with hover effects)
- Handle set completion with success message
- Show progress indicator (Task X of Y)
- Store selected answers for potential future use

```typescript
"use client";
import React, { useEffect, useState } from 'react';
import TaskComponent from '../../../components/TaskComponent';
import type { Question } from '../../../types/question';

export default function TaskSetPage(props: { params: Promise<{ setName: string }> }) {
  const params = React.use(props.params);
  const { setName } = params;
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentTaskIndex, setCurrentTaskIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [answers, setAnswers] = useState<{ [key: string]: string }>({});

  useEffect(() => {
    if (!setName) return;
    fetch(`/api/sets/${setName}`)
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setQuestions(data);
        } else {
          setError(data.error || 'Failed to load task set');
        }
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to load task set');
        setLoading(false);
      });
  }, [setName]);

  const handleNextTask = () => {
    if (currentTaskIndex < questions.length - 1) {
      setCurrentTaskIndex(currentTaskIndex + 1);
    }
  };

  const handleAnswerChange = (selected: string) => {
    const currentQuestion = questions[currentTaskIndex];
    setAnswers(prev => ({
      ...prev,
      [currentQuestion.pid]: selected
    }));
  };

  if (loading) return <div>Loading task set...</div>;
  if (error) return <div>{error}</div>;
  if (questions.length === 0) return <div>No tasks found in this set.</div>;

  const currentQuestion = questions[currentTaskIndex];
  const isLastTask = currentTaskIndex === questions.length - 1;

  return (
    <div style={{ position: 'relative', minHeight: '100vh' }}>
      {/* Progress indicator */}
      <div style={{
        textAlign: 'center',
        padding: '1rem',
        fontSize: '1.1rem',
        fontWeight: 'bold',
        color: '#666'
      }}>
        Task Set: {setName.toUpperCase()} - Task {currentTaskIndex + 1} of {questions.length}
      </div>

      {/* Current task */}
      <TaskComponent
        question={currentQuestion}
        taskNumber={currentTaskIndex + 1}
        onAnswerChange={handleAnswerChange}
      />

      {/* Navigation button */}
      {!isLastTask && (
        <button
          onClick={handleNextTask}
          style={{
            position: 'fixed',
            bottom: '2rem',
            right: '2rem',
            padding: '12px 24px',
            backgroundColor: '#0070f3',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '1rem',
            fontWeight: 'bold',
            cursor: 'pointer',
            boxShadow: '0 4px 12px rgba(0, 112, 243, 0.3)',
            transition: 'all 0.2s ease',
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.backgroundColor = '#0051cc';
            e.currentTarget.style.transform = 'translateY(-2px)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.backgroundColor = '#0070f3';
            e.currentTarget.style.transform = 'translateY(0)';
          }}
        >
          Next Task →
        </button>
      )}

      {/* Completion message */}
      {isLastTask && (
        <div style={{
          position: 'fixed',
          bottom: '2rem',
          right: '2rem',
          padding: '12px 24px',
          backgroundColor: '#28a745',
          color: 'white',
          borderRadius: '8px',
          fontSize: '1rem',
          fontWeight: 'bold',
        }}>
          Set Complete! 🎉
        </div>
      )}
    </div>
  );
}
```

### Step 5: Update Individual Task Page (Optional)
**File**: `/src/app/tasks/[index]/page.tsx`

**Action**: Refactor to use the new TaskComponent for consistency

**Implementation**: Replace the existing task display logic with TaskComponent usage while maintaining the same functionality.

## File Structure After Implementation

```
src/
├── app/
│   ├── api/
│   │   ├── questions/ (existing)
│   │   │   ├── questions.ts
│   │   │   ├── route.ts
│   │   │   └── [pid]/
│   │   │       └── route.ts
│   │   └── sets/ (new)
│   │       └── [setName]/
│   │           └── route.ts
│   ├── sets/ (new)
│   │   └── [setName]/
│   │       └── page.tsx
│   └── tasks/ (existing, optionally refactored)
│       └── [index]/
│           └── page.tsx
├── components/ (new)
│   └── TaskComponent.tsx
└── types/
    └── question.ts (updated)
```

## Testing Strategy

### Manual Testing Checklist
1. **API Endpoints**:
   - [ ] `/api/sets/set1` returns 3 questions
   - [ ] `/api/sets/set2` returns 3 questions
   - [ ] `/api/sets/backup` returns 3 questions
   - [ ] `/api/sets/invalid` returns 404 error

2. **Task Set Pages**:
   - [ ] `/sets/set1` loads and shows first task
   - [ ] "Next Task" button appears on first two tasks
   - [ ] "Next Task" button works and advances to next task
   - [ ] Third task shows "Set Complete!" instead of "Next Task"
   - [ ] Progress indicator shows correct task number

3. **Task Component**:
   - [ ] Images load correctly
   - [ ] Questions display properly
   - [ ] Radio buttons work for answer selection
   - [ ] Styling matches original design

4. **Edge Cases**:
   - [ ] Invalid set names show error message
   - [ ] Loading states work properly
   - [ ] Network errors are handled gracefully

## Future Enhancements (Optional)

1. **Answer Persistence**: Store selected answers and allow review
2. **Back Navigation**: Add "Previous Task" button
3. **Timer**: Add optional time tracking per task
4. **Results Summary**: Show results at end of task set
5. **Set Selection**: Create landing page to choose task sets
6. **Responsive Design**: Optimize for mobile devices

## Implementation Order

1. ✅ Update Question type interface (COMPLETED)
2. ✅ Create Task Set API endpoint (COMPLETED)
3. ✅ Extract TaskComponent (COMPLETED)
4. ✅ Create Task Set page component (COMPLETED)
5. ✅ Test each component individually (COMPLETED - Verified working)
6. ✅ Integration testing (COMPLETED - No integration issues found)
7. ✅ Refactor individual task page (COMPLETED - Option A implemented)

## Final Enhancement: Progress Bar Component

### Additional Component Created
**File**: `/src/components/ProgressBar.tsx` (new)

**Purpose**: Reusable minimalist progress bar component

**Features**:
- ✅ Generic `currentStep` and `totalSteps` props
- ✅ Smooth transition animations (0.3s ease)
- ✅ Consistent styling matching TaskComponent width (500px max)
- ✅ Optional `className` prop for customization
- ✅ Clean, minimalist design with subtle colors

**Usage**:
```tsx
<ProgressBar currentStep={2} totalSteps={3} />
```

### Updated Task Set Page
- ✅ Replaced inline progress bar with ProgressBar component
- ✅ Cleaner code with better separation of concerns
- ✅ Easier to maintain and potentially reuse elsewhere

---

**Created**: July 19, 2025
**Status**: ✅ FULLY COMPLETE - All Implementation Steps Finished + Progress Bar Enhancement
**Last Updated**: July 19, 2025
**Final Result**: Task Set feature fully implemented with reusable components and clean progress indication

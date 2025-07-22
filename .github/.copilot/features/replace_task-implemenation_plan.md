# Implementation Plan: Replace Task in Task Set

## Feature Overview

Enable users to manually replace any task in a task set while working on it, selecting a replacement task of the same difficulty. Any answer given for the replaced task is reset.

## Current State Analysis

- Users work through a predefined set of tasks sequentially.
- Tasks are fixed for the duration of the set; no replacement is possible.
- Answers are persisted per task.
- No UI exists for replacing a task or selecting alternatives.

## Goals

- Allow users to trigger a task replacement at any point during a set.
- Provide a UI for selecting a replacement task (filtered by difficulty).
- Ensure the replacement is in-place (same position in set).
- Reset any answer for the replaced task.
- Maintain a smooth and intuitive user experience.

## Implementation Plan

### Phase 1: Data & API Enhancements

#### 1.1 Expose Task Pool by Difficulty

- **Purpose**: Backend/API endpoint or utility to fetch tasks by difficulty.
- **Features**:
  - Returns all tasks of a given difficulty
  - Excludes tasks already in the set (except current)
- **Approach**:
  - Adjust the existing questions API endpoint to accept optional query parameters:
    - `difficulty`: If provided, only return questions matching this difficulty.
    - `exclude`: One or more question pids (comma-separated) to exclude from the results.
  - Apply these filters server-side before returning the questions list.
  - Maintain backward compatibility: if no query params are provided, return all questions as before.

### Phase 2: Core Replacement Functionality

#### 2.1 Add Replace Button to Task UI

- **Purpose**: Allow users to initiate task replacement.
- **Features**:
  - Button visible on each task in the set
  - Accessible and clearly labeled

#### 2.2 Implement Replacement Modal/Dialog

- **Purpose**: Let users select a replacement task.
- **Features**:
  - Modal/dialog opens on button click (Replace Task)
  - Fetches and lists available tasks of the same difficulty (excluding the current task)
  - Shows a simple list with each task's pid and question text
  - User can select a replacement task from the list (e.g., radio button or highlight)
  - Confirm and cancel actions (confirm triggers replacement, cancel closes modal)
  - Shows loading indicator while fetching tasks
  - Shows error or empty state if no replacements are available
  - Modal is accessible and can be closed with Escape or by clicking outside
- **Approach**:
  - Implement a reusable `Modal` component that accepts header, body, and footer/actions as props
  - Build the replacement dialog using the `Modal` component
  - On open, fetch available tasks from `/api/questions?difficulty=<current>&exclude=<currentPid>`
  - Render a simple list of tasks (pid and question text) with selection controls
  - Track selected replacement in local state
  - On confirm, call a callback to update the task set state and close the modal
  - On cancel, simply close the modal
  - Ensure modal is visually consistent with the app and accessible

#### 2.3 Update Task Set State Management

- **Purpose**: Replace the current task in-place and reset answer.
- **Features**:
  - Swap out the task in the set data structure
  - Reset any persisted answer for that position
  - Ensure UI updates accordingly

### Phase 3: UI/UX Improvements

#### 3.1 Visual Feedback and Edge Cases

- **Purpose**: Ensure smooth user experience.
- **Features**:
  - Loading indicators for replacement
  - Error handling (e.g., no available replacements)
  - Confirmation message on successful replacement

### Implementation Priority

| Priority | Feature                                 | Category |
| -------- | --------------------------------------- | -------- |
| 1        | Backend/API for task pool by difficulty | high     |
| 2        | Replace button in task UI               | high     |
| 3        | Replacement modal/dialog                | medium   |
| 4        | State management for replacement/reset  | medium   |
| 5        | UI/UX improvements                      | low      |

## Future Enhancements

- Allow undoing a replacement
- Track replacement history for analytics
- Suggest replacement tasks based on user preferences
- Support batch replacement (multiple at once)

## Notes

- Ensure accessibility for all UI elements
- Consider performance for large task pools
- Test thoroughly for edge cases (e.g., no replacements available)

## Feature Progress

- [x] Backend/API for task pool by difficulty
- [x] Replace button in task UI
- [ ] Replacement modal/dialog
- [ ] State management for replacement/reset
- [ ] UI/UX improvements

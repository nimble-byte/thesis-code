# Implementation Plan: Answer Persistence for Task Sets

## Feature Overview

Persist user solutions to task sets on disk, saving each completed set of answers as a uniquely identified file and appending all solutions to a master file.

## Current State Analysis

- Answers to task sets are currently not persisted; they exist only in memory during a session.
- The "Next Task" button is enabled regardless of whether the current task has been answered.
- No mechanism exists to uniquely identify or store individual solutions.
- No master file collects all solutions.

## Goals

- Persist each completed solution (answers to all three questions in a task set) as a separate file, named with a UUID.
- Maintain a master file that appends every new solution.
- Only persist when all three questions in a task set have been answered.
- Disable the "Next Task" button until the current question is answered.
- Ensure solutions are uniquely identified and can be presented multiple times.

## Implementation Plan


### Phase 1: Data Model & Persistence Logic

#### 1.1 Define Solution Data Structure

- **Purpose**: Standardize what constitutes a "solution" (answers to all three questions in a task set, task set ID, timestamps, UUID).
- **Features**:
  - Task set identifier (`setId`, a UUID)
  - Answers array (one entry per question/task in the set):
    - `pid`: string (task/question ID)
    - `givenAnswer`: string (user's selected answer)
    - `correctAnswer`: string (from the dataset)
    - `timestamp`: ISO string (when the answer was submitted/"next" clicked)
  - Solution UUID (unique for this solution instance)
  - Solution completion timestamp (when all questions in the set were answered)

#### 1.2 Implement File Persistence Utilities

- **Purpose**: Write/read solution files and update the master file.
- **Features**:
  - Save solution as a new file (e.g., `solution-<solutionUuid>.json`) once all three questions are answered
  - Append solution to master file (e.g., `all_solutions.jsonl` or `.json`) after each completed task set
  - Ensure atomic writes to prevent data loss

### Phase 2: UI/UX Changes

#### 2.1 Update "Next Task" Button Logic and Solution Tracking

- **Purpose**: Ensure answers are tracked with timestamps and the button is only enabled when the current question is answered.
- **Approach**:
  - Introduce intermediary solution tracking in the `page.tsx` component.
  - For each answer, store: `pid`, `givenAnswer`, `correctAnswer`, and `timestamp` (recorded when the "Next Task" button is clicked).
  - Only enable the "Next Task" button if the current question has an answer.
  - On click, record the answer and move to the next question.

#### 2.2 Trigger Persistence on Task Set Completion

- **Purpose**: Persist solution when user has answered all three questions in a task set and submits the set.
- **Approach**:
  - createa an API for solution persistence
    - uses the POST call
    - accepts a TaskSetSolution object
    - returns a 201 status and the full TaskSetSolution object in the response
  - After the last question is answered, show a "Submit Tasks" button instead of the completion message.
  - When the user clicks "Submit Tasks":
    - Generate the solution UUID and completion timestamp.
    - Call persistence utilities (via API route) to save the solution and update the master file.

### Phase 3: Integration & Testing

#### 3.1 Integrate Persistence with Task Flow

- **Purpose**: Ensure persistence is triggered at the correct time in the user flow.
- **Features**:
  - Hook into task set completion event (after all three questions are answered and their answers recorded)

#### 3.2 Test Persistence and UI Logic

- **Purpose**: Validate correct file creation, master file updates, and UI behavior.
- **Features**:
  - Unit tests for persistence utilities
  - Manual/automated UI tests for button logic

### Implementation Priority

| Priority | Feature                                 | Category |
| -------- | --------------------------------------- | -------- |
| 1        | Solution data structure & persistence   | high     |
| 2        | Update "Next Task" button logic         | high     |
| 3        | Integration with task flow              | medium   |
| 4        | Master file append logic                | medium   |
| 5        | Testing (unit & UI)                     | low      |

## Future Enhancements

- Add encryption or user authentication for solution files.
- Implement solution export/import functionality.
- Add UI for browsing past solutions.
- Support for editing or deleting solutions.

## Notes

- Ensure file write operations are robust and handle errors gracefully.
- Consider file naming conventions and storage location for easy retrieval.
- If running in a browser-only environment, disk persistence may require a backend or browser storage workaround.

## Progress

- [x] Phase 1: Data Model & Persistence Logic
  - [x] Define solution data structure
  - [x] Implement file persistence utilities
- [x] Phase 2: UI/UX Changes
  - [x] Update "Next Task" button logic
  - [x] Trigger persistence on completion
- [x] Phase 3: Integration & Testing
  - [x] Integrate persistence with task flow
  - [x] Test persistence and UI logic

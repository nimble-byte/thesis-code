import fs from 'fs';
import path from 'path';
import { TaskSetSolution } from '../types/solution';

const SOLUTIONS_DIR = path.join(process.cwd(), 'task-server', 'data', 'solutions');
const MASTER_FILE = path.join(SOLUTIONS_DIR, 'all_solutions.json');

/**
 * Saves a solution as a new file named solution-<solutionUuid>.json in the solutions directory.
 * @param solution The solution object to save
 */
export function saveSolutionFile(solution: TaskSetSolution): void {
  const filePath = path.join(SOLUTIONS_DIR, `solution-${solution.solutionUuid}.json`);
  fs.writeFileSync(filePath, JSON.stringify(solution, null, 2), 'utf-8');
}

/**
 * Appends a solution to the master file (all_solutions.json), which is a valid JSON array.
 * @param solution The solution object to append
 */
export function appendToMasterFile(solution: TaskSetSolution): void {
  let solutions: TaskSetSolution[] = [];
  if (fs.existsSync(MASTER_FILE)) {
    const content = fs.readFileSync(MASTER_FILE, 'utf-8');
    try {
      solutions = JSON.parse(content);
      if (!Array.isArray(solutions)) solutions = [];
    } catch {
      solutions = [];
    }
  }
  solutions.push(solution);
  fs.writeFileSync(MASTER_FILE, JSON.stringify(solutions, null, 2), 'utf-8');
}

/**
 * Reads all solutions from the master file (all_solutions.json).
 * @returns Array of TaskSetSolution objects
 */
export function readAllSolutions(): TaskSetSolution[] {
  if (!fs.existsSync(MASTER_FILE)) return [];
  const content = fs.readFileSync(MASTER_FILE, 'utf-8');
  try {
    const arr = JSON.parse(content);
    return Array.isArray(arr) ? arr : [];
  } catch {
    return [];
  }
}

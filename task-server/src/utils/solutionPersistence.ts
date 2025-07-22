import fs from 'fs';
import path from 'path';
import { TaskSetSolution } from '../types/solution';

const SOLUTIONS_DIR = path.join(process.cwd(), 'data', 'solutions');
const MASTER_FILE = path.join(SOLUTIONS_DIR, 'all_solutions.json');

function ensureSolutionsDir() {
  if (!fs.existsSync(SOLUTIONS_DIR)) {
    fs.mkdirSync(SOLUTIONS_DIR, { recursive: true });
  }
}

/**
 * Saves a solution as a new file named solution-<uuid>.json in the solutions directory.
 * @param solution The solution object to save
 */
export function saveSolutionFile(solution: TaskSetSolution): void {
  ensureSolutionsDir();
  const filePath = path.join(SOLUTIONS_DIR, `solution-${solution.uuid}.json`);
  fs.writeFileSync(filePath, JSON.stringify(solution, null, 2), 'utf-8');
}

/**
 * Appends a solution to the master file (all_solutions.json), which is a valid JSON array.
 * @param solution The solution object to append
 */
export function appendToMasterFile(solution: TaskSetSolution): void {
  ensureSolutionsDir();
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
  ensureSolutionsDir();
  if (!fs.existsSync(MASTER_FILE)) return [];
  const content = fs.readFileSync(MASTER_FILE, 'utf-8');
  try {
    const arr = JSON.parse(content);
    return Array.isArray(arr) ? arr : [];
  } catch {
    return [];
  }
}

/**
 * Reads a solution by its UUID from the solutions directory.
 * @param uuid The UUID of the solution
 * @returns The TaskSetSolution object if found, otherwise throws an error
 */
export function readSolutionById(uuid: string): TaskSetSolution {
  const filePath = path.join(SOLUTIONS_DIR, `solution-${uuid}.json`);
  if (!fs.existsSync(filePath)) {
    throw new Error(`Solution with UUID ${uuid} not found.`);
  }
  const content = fs.readFileSync(filePath, 'utf-8');
  try {
    return JSON.parse(content) as TaskSetSolution;
  } catch {
    throw new Error(`Failed to parse solution file for UUID ${uuid}.`);
  }
}

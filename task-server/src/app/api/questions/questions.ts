import fs from 'fs';
import path from 'path';
import type { Question } from '../../../types/question';

const datasetPath = path.resolve(process.env.DATASET_PATH || '');
const questionsFile = path.join(datasetPath, 'filtered_dataset.csv');

let cachedQuestions: Question[] | null = null;

function parseCSV(filePath: string): Question[] {
  const data = fs.readFileSync(filePath, 'utf-8');
  const [header, ...rows] = data.trim().split('\n');
  const keys = header.split(';');
  return rows.map(row => {
    const values = row.split(';');
    const obj: any = Object.fromEntries(keys.map((k, i) => [k, values[i]]));
    try {
      obj.choices = JSON.parse(obj.choices);
    } catch {
      obj.choices = [];
    }
    return obj as Question;
  });
}

export function getQuestions(): Question[] {
  if (!cachedQuestions) {
    cachedQuestions = parseCSV(questionsFile);
  }
  return cachedQuestions;
}

import { NextRequest } from 'next/server';
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

function getQuestions(): Question[] {
  if (!cachedQuestions) {
    cachedQuestions = parseCSV(questionsFile);
  }
  return cachedQuestions;
}

export async function GET(req: NextRequest): Promise<Response> {
  try {
    const questions = getQuestions();
    const { searchParams } = new URL(req.url);
    const index = searchParams.get('index');
    const question = questions.find(q => q.pid === index);
    if (question) {
        return new Response(JSON.stringify(question), { status: 200 });
    } else {
        return new Response(JSON.stringify({ error: 'Invalid index' }), { status: 400 });
    }
  } catch (err: any) {
    return new Response(JSON.stringify({ error: 'Failed to load questions', details: String(err) }), { status: 500 });
  }
}

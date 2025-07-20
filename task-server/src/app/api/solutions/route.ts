import { NextRequest, NextResponse } from 'next/server';
import { saveSolutionFile, appendToMasterFile } from '@/utils/solutionPersistence';
import type { TaskSetSolution } from '@/types/solution';

export async function POST(req: NextRequest) {
  try {
    const solution: TaskSetSolution = await req.json();
    // Save solution as a new file and append to master file
    saveSolutionFile(solution);
    appendToMasterFile(solution);
    return NextResponse.json(solution, { status: 201 });
  } catch (err: any) {
    return NextResponse.json({ error: err.message || 'Failed to persist solution' }, { status: 500 });
  }
}

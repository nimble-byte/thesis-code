import { NextRequest, NextResponse } from "next/server";
import {
  saveSolutionFile,
  appendToMasterFile,
  readAllSolutions,
} from "@/utils/solutionPersistence";
import type { TaskSetSolution } from "@/types/solution";

export async function GET(_req: NextRequest): Promise<NextResponse> {
  try {
    const solutions: TaskSetSolution[] = readAllSolutions();
    return NextResponse.json(solutions, { status: 200 });
  } catch (err: any) {
    return NextResponse.json({
      error: err.message || "Failed to read solutions",
      status: 500,
    });
  }
}

export async function POST(req: NextRequest): Promise<NextResponse> {
  try {
    const solution: TaskSetSolution = await req.json();
    // Save solution as a new file and append to master file
    saveSolutionFile(solution);
    appendToMasterFile(solution);
    return NextResponse.json(solution, { status: 201 });
  } catch (err: any) {
    return NextResponse.json({
      error: err.message || "Failed to persist solution",
      status: 500,
    });
  }
}

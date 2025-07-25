import { NextRequest, NextResponse } from "next/server";
import { readSolutionById } from "@/utils/solutionPersistence";

export async function GET(_req: NextRequest, { params }: { params: Promise<{ uuid: string }> }): Promise<NextResponse> {
  const { uuid } = await params;
  if (!uuid || typeof uuid !== "string") {
    return NextResponse.json({ error: "Invalid or missing UUID." }, { status: 400 });
  }
  try {
    const solution = readSolutionById(uuid);
    return NextResponse.json(solution, { status: 200 });
  } catch (err: any) {
    return NextResponse.json({ error: err.message || "Solution not found." }, { status: 404 });
  }
}

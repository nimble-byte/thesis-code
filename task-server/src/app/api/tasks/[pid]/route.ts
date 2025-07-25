import { NextRequest, NextResponse } from "next/server";
import { getQuestions } from "@/utils/questions";

export async function GET(_req: NextRequest, { params }: { params: Promise<{ pid: string }> }): Promise<NextResponse> {
  try {
    const questions = getQuestions();
    const { pid } = await params;
    const question = questions.find((q) => q.pid === pid);

    if (!question) {
      return NextResponse.json({ error: "Invalid pid" }, { status: 404 });
    } else {
      return NextResponse.json(question, { status: 200 });
    }
  } catch (err: any) {
    return NextResponse.json({ error: "Failed to load questions", details: String(err) }, { status: 500 });
  }
}

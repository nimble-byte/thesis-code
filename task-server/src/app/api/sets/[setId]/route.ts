import { NextRequest, NextResponse } from "next/server";
import { getQuestions } from "@/utils/questions";

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ setId: string }> }
): Promise<NextResponse> {
  try {
    const { setId } = await params;

    const questions = getQuestions();
    const setQuestions = questions.filter((q) => q.set === setId);

    if (setQuestions.length === 0) {
      return NextResponse.json(
        { error: "Invalid set ID or no questions found" },
        { status: 404 }
      );
    }

    return NextResponse.json(setQuestions, { status: 200 });
  } catch (err: any) {
    return NextResponse.json(
      {
        error: "Failed to load questions",
        details: String(err),
      },
      { status: 500 }
    );
  }
}

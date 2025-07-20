import { NextRequest } from "next/server";
import { getQuestions } from "@/utils/questions";

export async function GET(_req: NextRequest, { params }: { params: Promise<{ setId: string }> }): Promise<Response> {
  try {
    const { setId } = await params;

    const questions = getQuestions();
    const setQuestions = questions.filter((q) => q.set === setId);

    if (setQuestions.length === 0) {
      return new Response(JSON.stringify({ error: "Invalid set ID or no questions found" }), { status: 404 });
    }

    return new Response(JSON.stringify(setQuestions), { status: 200 });
  } catch (err: any) {
    return new Response(JSON.stringify({ error: "Failed to load questions", details: String(err) }), { status: 500 });
  }
}

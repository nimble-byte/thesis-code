import { NextRequest } from "next/server";
import { getQuestions } from "@/utils/questions";

export async function GET(_req: NextRequest, { params }: { params: Promise<{ pid: string }> }): Promise<Response> {
  try {
    const questions = getQuestions();
    const { pid } = await params;
    const question = questions.find((q) => q.pid === pid);

    if (!question) {
      return new Response(JSON.stringify({ error: "Invalid pid" }), { status: 404 });
    } else {
      return new Response(JSON.stringify(question), { status: 200 });
    }
  } catch (err: any) {
    return new Response(JSON.stringify({ error: "Failed to load questions", details: String(err) }), { status: 500 });
  }
}

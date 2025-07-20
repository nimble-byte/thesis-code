import { getQuestions } from "@/utils/questions";
import { NextRequest } from "next/server";

export async function GET(req: NextRequest): Promise<Response> {
  try {
    const difficulty = req.nextUrl.searchParams.get("difficulty");
    const excludeParam = req.nextUrl.searchParams.get("exclude");
    let exclude: string[] = [];

    if (excludeParam) {
      exclude = excludeParam.split(",").map((s) => s.trim());
    }

    let questions = getQuestions();

    if (difficulty) {
      questions = questions.filter((q) => q.difficulty === difficulty);
    }
    if (exclude.length > 0) {
      questions = questions.filter((q) => !exclude.includes(q.pid));
    }

    return new Response(JSON.stringify(questions), { status: 200 });
  } catch (err: any) {
    return new Response(JSON.stringify({ error: "Failed to load questions", details: String(err) }), { status: 500 });
  }
}

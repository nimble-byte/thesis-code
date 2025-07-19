import { getQuestions } from "./questions"

export async function GET(): Promise<Response> {
  try {
    const questions = getQuestions();
    return new Response(JSON.stringify(questions), { status: 200 });
  } catch (err: any) {
    return new Response(JSON.stringify({ error: 'Failed to load questions', details: String(err) }), { status: 500 });
  }
}

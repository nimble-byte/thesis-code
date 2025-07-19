// Shared type for a question
export interface Question {
  pid: string;
  question: string;
  image: string;
  choices: string[];
  answer: string;
  img_height: number;
  img_width: number;
  difficulty: string;
  set: string;
}

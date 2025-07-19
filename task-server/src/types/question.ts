// Shared type for a question
export interface Question {
  pid: string;
  question: string;
  image: string;
  choices: string[];
  answer: string;
  img_height: string;
  img_width: string;
}

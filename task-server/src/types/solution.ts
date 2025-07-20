
/**
 * Represents a user's answer to a single task/question in a task set.
 */
export interface TaskAnswer {
  /**
   * Task/question ID (pid from dataset)
   */
  pid: string;
  /**
   * User's selected answer
   */
  givenAnswer: string;
  /**
   * Correct answer from dataset
   */
  correctAnswer: string;
  /**
   * ISO string timestamp when the answer was submitted ("next" clicked)
   */
  timestamp: string;
}

/**
 * Represents a completed solution for a task set, including all answers and metadata.
 */
export interface TaskSetSolution {
  /**
   * UUID of the task set (setId)
   */
  setId: string;
  /**
   * Array of answers for all questions in the set
   */
  answers: TaskAnswer[];
  /**
   * Unique UUID for this solution instance
   */
  uuid: string;
  /**
   * ISO string timestamp when all questions in the set were answered
   */
  completedAt: string;
}

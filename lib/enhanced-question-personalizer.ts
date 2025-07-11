// Enhanced question personalization functions
export interface PersonalizedQuestion {
  id?: string;
  question: string;
  personalizedContext?: string;
  difficulty?: string;
  relevanceScore?: number;
}

export async function personalizeQuestions(
  questions: any[], 
  resumeData: any, 
  jobData: any
): Promise<PersonalizedQuestion[]> {
  // Basic implementation - can be enhanced later
  return questions.map((q, index) => ({
    id: `q-${index}`,
    question: q.question || q.title || 'Sample Question',
    personalizedContext: '',
    difficulty: q.difficulty || 'medium',
    relevanceScore: 1
  }));
}

export function generatePersonalizedContext(question: any, userData: any): string {
  return '';
}

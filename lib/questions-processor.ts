// Question processing utilities
export interface Question {
  id?: string
  title: string
  type: string
  difficulty?: string
  summaries?: string
  approach?: string
  relevance?: string
  followUps?: string[]
  link?: string
}

export function processQuestionBank(questions: any[]): Question[] {
  return questions.map((q, index) => ({
    id: `q-${index}`,
    title: q.title || q.question || 'Sample Question',
    type: q.type || 'general',
    difficulty: q.difficulty || 'medium',
    summaries: q.summaries || q.description || '',
    approach: q.approach || '',
    relevance: q.relevance || '',
    followUps: q.followUps || [],
    link: q.link || ''
  }))
}

export function selectQuestionsByRole(questions: Question[], role: string): Question[] {
  // Simple filtering logic - can be enhanced
  return questions.filter(q => 
    q.type.toLowerCase().includes(role.toLowerCase()) ||
    q.title.toLowerCase().includes(role.toLowerCase())
  )
}

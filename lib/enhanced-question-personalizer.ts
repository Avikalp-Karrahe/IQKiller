import { openai, getModel } from './openai'
import { z } from 'zod'
import { DetailedResumeData } from './enhanced-resume-parser'
import { Question } from './questions-processor'

export interface PersonalizedQuestion extends Question {
  personalizedQuestion: string
  personalizedApproach: string
  relevanceToCandidate: string
  specificContext: string // References to their specific projects/experience
  followUpQuestions: string[]
  preparationTips: string[]
}

export interface PersonalizationContext {
  resumeData: DetailedResumeData
  jobData: {
    role: string
    company: string
    location: string
    description: string
    requirements: string[]
  }
  matchScore: number
}

const personalizedQuestionSchema = z.object({
  personalizedQuestion: z.string(),
  personalizedApproach: z.string(),
  relevanceToCandidate: z.string(),
  specificContext: z.string(),
  followUpQuestions: z.array(z.string()),
  preparationTips: z.array(z.string())
})

export async function createHighlyPersonalizedQuestions(
  questions: Question[],
  context: PersonalizationContext
): Promise<PersonalizedQuestion[]> {
  const personalizedQuestions: PersonalizedQuestion[] = []
  
  for (const question of questions) {
    try {
      const completion = await openai.chat.completions.create({
        model: 'gpt-4o-mini-2024-07-18', // Use latest model
        messages: [
          {
            role: 'system',
            content: 'You are an expert at personalizing interview questions based on candidate background.'
          },
          {
            role: 'user',
            content: createPersonalizationPrompt(question, context)
          }
        ],
        response_format: { type: 'json_object' }
      })
      
      const result = completion.choices[0].message.content
      if (!result) throw new Error('No content in response')
      
      const personalization = personalizedQuestionSchema.parse(JSON.parse(result))
      
      personalizedQuestions.push({
        ...question,
        ...personalization
      })
    } catch (error) {
      console.error('Question personalization error:', error)
      // Fallback to basic personalization
      personalizedQuestions.push(createBasicPersonalizedQuestion(question, context))
    }
  }
  
  return personalizedQuestions
}

function createPersonalizationPrompt(question: Question, context: PersonalizationContext): string {
  const { resumeData, jobData } = context
  
  return `
    TASK: Transform this generic interview question into a highly personalized question that references the candidate's specific background.
    
    ORIGINAL QUESTION: "${question.summaries}"
    QUESTION TYPE: ${question.type}
    
    TARGET ROLE: ${jobData.role} at ${jobData.company}
    
    CANDIDATE'S DETAILED BACKGROUND:
    
    EXPERIENCE:
    - ${resumeData.experienceDescription}
    - Current Role: ${resumeData.currentRole} at ${resumeData.currentCompany}
    - Total Experience: ${resumeData.experienceYears} years
    
    EDUCATION:
    - Degree: ${resumeData.education.degree} in ${resumeData.education.field}
    - University: ${resumeData.education.university}
    
    SPECIFIC PROJECTS:
    ${resumeData.projects.map((project, idx) => 
      `${idx + 1}. ${project.title}: ${project.description}
         Technologies: ${project.technologies.join(', ')}
         ${project.achievements ? `Achievement: ${project.achievements}` : ''}
         ${project.metrics ? `Metrics: ${project.metrics}` : ''}`
    ).join('\n')}
    
    WORK EXPERIENCE:
    ${resumeData.workExperience.map((work, idx) => 
      `${idx + 1}. ${work.role} at ${work.company} (${work.duration})
         Key Achievements: ${work.achievements.join(', ')}
         Technologies: ${work.technologies.join(', ')}`
    ).join('\n')}
    
    TECHNICAL SKILLS:
    - Programming: ${resumeData.technicalSkills.programmingLanguages.join(', ')}
    - Frameworks: ${resumeData.technicalSkills.frameworks.join(', ')}
    - Tools: ${resumeData.technicalSkills.tools.join(', ')}
    - Libraries: ${resumeData.technicalSkills.libraries.join(', ')}
    
    QUANTIFIED ACHIEVEMENTS:
    ${resumeData.achievements.map(achievement => 
      `- ${achievement.description}${achievement.metrics ? ` (${achievement.metrics})` : ''}`
    ).join('\n')}
    
    PERSONALIZATION REQUIREMENTS:
    
    1. PERSONALIZED QUESTION:
    - Start with "Given your experience with [specific project/technology/company]..."
    - Reference their exact background, projects, or achievements
    - Make it feel like it was written specifically for them
    - Keep the core technical challenge but personalize the context
    
    2. PERSONALIZED APPROACH:
    - Explain how their specific background gives them an advantage
    - Reference particular projects or experiences that are relevant
    - Mention specific technologies they've used
    - Connect to their quantified achievements
    
    3. RELEVANCE TO CANDIDATE:
    - Explain exactly why this question matters for someone with their background
    - Reference their specific experience level (${resumeData.experienceYears} years)
    - Connect to their education (${resumeData.education.degree})
    - Mention their current role context
    
    4. SPECIFIC CONTEXT:
    - Include specific references to their projects, companies, or achievements
    - Use their exact technology stack
    - Reference their quantified results where relevant
    - Make it clear this is tailored to their unique background
    
    5. FOLLOW-UP QUESTIONS (3-4):
    - Reference their specific projects or experiences
    - Ask about challenges they might have faced in their listed projects
    - Connect to their technology choices and architectural decisions
    
    6. PREPARATION TIPS (2-3):
    - Leverage their existing project experience
    - Suggest how to present their specific achievements
    - Reference their technology stack advantages
    
    EXAMPLE STYLE (like the Spotify example):
    "Given your experience with [specific project] and [specific technology], how would you approach [challenge] in the context of [role]? Please outline your approach, including lessons from your work on [specific project] and how your experience with [specific technology] would inform your strategy."
    
    BE EXTREMELY SPECIFIC - use their exact project names, company names, technologies, metrics, and achievements.
  `
}

function createBasicPersonalizedQuestion(question: Question, context: PersonalizationContext): PersonalizedQuestion {
  const { resumeData, jobData } = context
  
  return {
    ...question,
    personalizedQuestion: `Given your ${resumeData.experienceDescription} and background in ${resumeData.technicalSkills.programmingLanguages.join(', ')}, ${question.summaries}`,
    personalizedApproach: `Your experience with ${resumeData.technicalSkills.programmingLanguages.slice(0, 2).join(' and ')} positions you well for this question. Focus on demonstrating your practical experience and problem-solving approach from your ${resumeData.experienceYears} years in the field.`,
    relevanceToCandidate: `This question is particularly relevant for someone with your background in ${resumeData.education.field} and experience as ${resumeData.currentRole}. Your work with ${resumeData.technicalSkills.frameworks.slice(0, 2).join(' and ')} makes this a natural fit.`,
    specificContext: `References your experience at ${resumeData.currentCompany} and your work with ${resumeData.technicalSkills.programmingLanguages.join(', ')}.`,
    followUpQuestions: [
      `How did you handle similar challenges in your role at ${resumeData.currentCompany}?`,
      `What lessons from your ${resumeData.projects[0]?.title || 'recent projects'} would apply here?`,
      `How would you leverage your experience with ${resumeData.technicalSkills.frameworks[0] || 'your tech stack'} for this problem?`
    ],
    preparationTips: [
      `Review your specific experience with ${resumeData.technicalSkills.programmingLanguages.slice(0, 2).join(' and ')}`,
      `Prepare examples from your ${resumeData.projects.length} projects that demonstrate problem-solving`,
      `Think about how your ${resumeData.education.degree} background gives you an analytical advantage`
    ]
  }
}

export function generatePersonalizedIntroduction(
  resumeData: DetailedResumeData,
  jobData: { role: string; company: string },
  matchScore: number
): string {
  const skills = resumeData.technicalSkills.programmingLanguages.slice(0, 3).join(', ')
  const education = resumeData.education.degree
  const experience = resumeData.experienceDescription
  const projects = resumeData.stats.totalProjects
  
  return `${jobData.role} interview: Your robust background in ${skills} positions you exceptionally well for this role at ${jobData.company}. With ${experience} and a ${education} degree, you have the technical expertise and analytical mindset that will resonate with the team. Leverage your proven track record of ${projects} successful projects to illustrate your ability to derive actionable insights from complex data. As you prepare, focus on articulating how your skills can enhance ${jobData.company}'s objectives and drive data-driven decisions that impact the industry.`
}

export function generatePersonalizedTalkingPoints(resumeData: DetailedResumeData): {
  strengths: string[]
  competitiveAdvantages: string[]
  projectHighlights: string[]
} {
  return {
    strengths: resumeData.technicalSkills.programmingLanguages.slice(0, 3).map(skill => 
      `${skill}: Highlight your ${skill} experience`
    ),
    competitiveAdvantages: [
      `Advanced degree: ${resumeData.education.degree}`,
      `Strong combination: ${resumeData.technicalSkills.programmingLanguages.slice(0, 3).join(', ')}`,
      `Proven track record: ${resumeData.stats.totalProjects} projects`
    ],
    projectHighlights: resumeData.projects.slice(0, 3).map(project => 
      `${project.title}: ${project.description.substring(0, 100)}...`
    )
  }
}

// Legacy exports for backward compatibility
export interface PersonalizedQuestionLegacy {
  id?: string
  question: string
  personalizedContext?: string
  difficulty?: string
  relevanceScore?: number
}

export interface PersonalizationContextLegacy {
  resumeHighlights?: string[]
  roleRequirements?: string[]
  industryFocus?: string
  experienceLevel?: string
  companyContext?: string
}

export async function personalizeQuestions(
  questions: any[], 
  resumeData: any, 
  jobData: any
): Promise<PersonalizedQuestionLegacy[]> {
  // Basic implementation - can be enhanced later
  return questions.map((q, index) => ({
    id: `q-${index}`,
    question: q.question || q.title || 'Sample Question',
    personalizedContext: '',
    difficulty: q.difficulty || 'medium',
    relevanceScore: 1
  }))
} 
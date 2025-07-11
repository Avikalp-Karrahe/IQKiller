import { openai } from './openai'
import { z } from 'zod'

export interface CompanyInsights {
  overview: string
  culture: string
  interviewProcess: {
    stages: {
      name: string
      description: string
      duration: string
      tips: string[]
    }[]
  }
  techStack: string[]
  values: string[]
  challenges: string[]
  projects: string[]
  preparationTips: string[]
}

export interface SalaryInsights {
  range: {
    min: number
    max: number
    currency: string
  }
  benefits: string[]
  bonuses: string[]
  negotiationTips: string[]
}

const companyInsightsSchema = z.object({
  overview: z.string(),
  culture: z.string(),
  interviewProcess: z.object({
    stages: z.array(z.object({
      name: z.string(),
      description: z.string(),
      duration: z.string(),
      tips: z.array(z.string())
    }))
  }),
  techStack: z.array(z.string()),
  values: z.array(z.string()),
  challenges: z.array(z.string()),
  projects: z.array(z.string()),
  preparationTips: z.array(z.string())
})

const salaryInsightsSchema = z.object({
  range: z.object({
    min: z.number(),
    max: z.number(),
    currency: z.string()
  }),
  benefits: z.array(z.string()),
  bonuses: z.array(z.string()),
  negotiationTips: z.array(z.string())
})

export async function researchCompanyInsights(
  company: string,
  role: string,
  location: string
): Promise<CompanyInsights> {
  try {
    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini-2024-07-18',
      messages: [
        {
          role: 'system',
          content: 'You are an expert at researching companies and providing interview insights.'
        },
        {
          role: 'user',
          content: `Research and provide comprehensive insights about ${company} for a ${role} interview guide.
          Include:
          1. Company overview
          2. Company culture
          3. Interview process stages
          4. Tech stack
          5. Company values
          6. Current challenges
          7. Notable projects
          8. Preparation tips
          
          Format as a JSON object matching the schema.`
        }
      ],
      response_format: { type: 'json_object' }
    })

    const result = completion.choices[0].message.content
    if (!result) throw new Error('No content in response')
    
    return companyInsightsSchema.parse(JSON.parse(result))
  } catch (error) {
    console.error('Error researching company insights:', error)
    return {
      overview: `${company} is a technology company.`,
      culture: 'The company values innovation and collaboration.',
      interviewProcess: {
        stages: [
          {
            name: 'Initial Screen',
            description: 'Phone or video call with recruiter',
            duration: '30 minutes',
            tips: ['Research company basics', 'Prepare your elevator pitch']
          },
          {
            name: 'Technical Interview',
            description: 'Technical assessment and coding challenges',
            duration: '1-2 hours',
            tips: ['Practice coding problems', 'Review core concepts']
          },
          {
            name: 'Final Round',
            description: 'Multiple interviews with team members',
            duration: '3-4 hours',
            tips: ['Prepare questions about the role', 'Review your past projects']
          }
        ]
      },
      techStack: ['Various modern technologies'],
      values: ['Innovation', 'Collaboration', 'Excellence'],
      challenges: ['Scaling systems', 'Market competition'],
      projects: ['Various innovative solutions'],
      preparationTips: [
        'Research the company thoroughly',
        'Practice coding problems',
        'Prepare questions for interviewers'
      ]
    }
  }
}

export async function generateSalaryInsights(
  company: string,
  role: string,
  location: string
): Promise<SalaryInsights> {
  try {
    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini-2024-07-18',
      messages: [
        {
          role: 'system',
          content: 'You are an expert at providing salary and compensation insights.'
        },
        {
          role: 'user',
          content: `Provide salary insights for a ${role} position at ${company} in ${location}.
          Include:
          1. Salary range (min and max)
          2. Benefits
          3. Bonuses
          4. Negotiation tips
          
          Format as a JSON object matching the schema.`
        }
      ],
      response_format: { type: 'json_object' }
    })

    const result = completion.choices[0].message.content
    if (!result) throw new Error('No content in response')
    
    return salaryInsightsSchema.parse(JSON.parse(result))
  } catch (error) {
    console.error('Error generating salary insights:', error)
    return {
      range: {
        min: 80000,
        max: 150000,
        currency: 'USD'
      },
      benefits: [
        'Health insurance',
        'Retirement plans',
        'Paid time off'
      ],
      bonuses: [
        'Annual performance bonus',
        'Sign-on bonus'
      ],
      negotiationTips: [
        'Research market rates',
        'Highlight your experience',
        'Consider total compensation'
      ]
    }
  }
}

export function generateProcessDiagram(stages: { name: string; description: string }[]): string {
  const nodes = stages.map((stage, index) => `${index + 1}["${stage.name}"]`)
  const connections = stages.slice(0, -1).map((_, index) => `${index + 1} --> ${index + 2}`)
  
  return `
graph LR
${nodes.join('\n')}
${connections.join('\n')}
`
}

// Legacy exports for backward compatibility
export interface CompanyData {
  name?: string
  industry?: string
  size?: string
  culture?: string[]
  recentNews?: string[]
}

export async function researchCompany(companyName: string): Promise<CompanyData> {
  // Basic implementation - can be enhanced later
  return {
    name: companyName,
    industry: '',
    size: '',
    culture: [],
    recentNews: []
  }
}

export function generateCompanyInsights(companyData: CompanyData): string[] {
  return []
} 
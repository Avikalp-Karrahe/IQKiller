import { z } from "zod"

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

export const questionsSchema = z.array(
  z.object({
    title: z.string(),
    type: z.string(),
    difficulty: z.string().optional(),
    summaries: z.string().optional(),
    approach: z.string().optional(),
    relevance: z.string().optional(),
    followUps: z.array(z.string()).optional(),
    link: z.string().optional()
  })
)

export const resumeSchema = z.object({
  name: z.string(),
  experience: z.string(),
  skills: z.array(z.string()),
  education: z.string().optional(),
  projects: z.array(z.string()).optional()
})

export const jobSchema = z.object({
  title: z.string(),
  company: z.string(),
  description: z.string(),
  requirements: z.array(z.string()).optional(),
  location: z.string().optional()
})

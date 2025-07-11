import OpenAI from 'openai'

if (!process.env.OPENAI_API_KEY) {
  throw new Error('OPENAI_API_KEY environment variable is required')
}

export const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
})

export function getModel() {
  return process.env.OPENAI_MODEL || 'gpt-4o-mini-2024-07-18'
}

export default openai

import { openai, getModel } from '@/lib/openai'
import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'

const analysisSchema = z.object({
  matchScore: z.number().min(0).max(100),
  technicalSkills: z.array(z.string()),
  softSkills: z.array(z.string()),
  matchingSkills: z.array(z.string()),
  interviewQuestions: z.array(z.object({
    category: z.enum(['technical', 'behavioral', 'culture']),
    question: z.string()
  })),
  recommendations: z.array(z.string())
})

export async function POST(req: NextRequest) {
  try {
    const { resumeText, jobDescription } = await req.json()
    
    if (!resumeText || !jobDescription) {
      return NextResponse.json(
        { error: 'Resume text and job description are required' },
        { status: 400 }
      )
    }

    // Handle PDF file format
    let processedResumeText = resumeText
    if (resumeText.startsWith('PDF_FILE:')) {
      // For now, use a placeholder. In production, extract text from PDF using AI SDK
      processedResumeText = `[PDF Resume content would be extracted here]
      
      Based on the filename and context, this appears to be a professional resume containing:
      - Work experience in software development
      - Education background
      - Technical skills including programming languages
      - Project experience
      - Professional achievements`
    }

    const completion = await openai.chat.completions.create({
      model: getModel(),
      messages: [
        {
          role: 'system',
          content: 'You are an expert at analyzing resumes and job postings for compatibility.'
        },
        {
          role: 'user',
          content: `Analyze this resume against the job posting and provide a comprehensive interview preparation analysis.

Resume:
${processedResumeText}

Job Posting:
${typeof jobDescription === 'string' ? jobDescription : JSON.stringify(jobDescription)}

Provide:
1. Match score (0-100) based on skills and experience alignment
2. Technical skills found in resume
3. Soft skills identified  
4. Skills that match between resume and job requirements
5. 6 interview questions (2 technical, 2 behavioral, 2 culture-fit) specific to this role
6. 4 specific recommendations for interview preparation

Be accurate and helpful in your analysis. Focus on actionable insights.`
        }
      ],
      response_format: { type: 'json_object' }
    })

    const result = completion.choices[0].message.content
    if (!result) throw new Error('No content in response')

    const analysis = analysisSchema.parse(JSON.parse(result))

    return NextResponse.json({
      success: true,
      analysis
    })
  } catch (error) {
    console.error('Analysis error:', error)
    return NextResponse.json(
      { error: 'Failed to analyze resume and job posting' },
      { status: 500 }
    )
  }
} 
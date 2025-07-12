import { NextRequest } from 'next/server'
import { openai } from '@/lib/openai'

export async function POST(req: NextRequest) {
  console.log('🚀 === IMMEDIATE JOB ANALYSIS: Starting ===')
  
  try {
    const body = await req.json();
    console.log('📄 Job analysis request received:', {
      hasJobData: !!body.jobData,
      jobDataKeys: body.jobData ? Object.keys(body.jobData) : []
    })
    
    if (!body.jobData) {
      return Response.json({ error: 'Job data is required' }, { status: 400 });
    }

    const startTime = Date.now()
    const jobData = body.jobData
    
    // Enhanced job analysis using scraped data
    console.log('=== ANALYZING JOB REQUIREMENTS ===')
    
    let jobAnalysis: any = {
      title: jobData.title || jobData.role || 'Position',
      company: jobData.company || 'Company',
      location: jobData.location || 'Location TBD',
      experienceLevel: jobData.experienceLevel || 'Not specified',
      jobType: jobData.jobType || 'Full-time',
      salary: jobData.salary || jobData.salaryRange || 'Not specified',
      requirements: jobData.requirements || [],
      skills: jobData.skills || [],
      responsibilities: jobData.responsibilities || [],
      benefits: jobData.benefits || [],
      content: jobData.content || jobData.description || '',
      url: jobData.url || '',
      hasStructuredData: !!(jobData.requirements && jobData.skills && jobData.responsibilities)
    }

    // If we have rich content, use AI to extract more insights
    if (jobData.content && jobData.content.length > 200) {
      try {
        console.log('🤖 === ENHANCING JOB ANALYSIS WITH AI ===')
        
        const prompt = `Analyze this job posting and extract key insights:

JOB POSTING CONTENT:
${jobData.content.substring(0, 3000)}

Extract and analyze:
1. Key technical requirements and skills needed
2. Experience level expectations (entry/mid/senior)
3. Company culture indicators
4. Growth opportunities mentioned
5. Interview process hints (if any)
6. Red flags or concerns to note

Provide insights in JSON format.`;

        const completion = await openai.chat.completions.create({
          model: 'gpt-4o-mini-2024-07-18',
          messages: [
            {
              role: 'system',
              content: 'You are an expert job market analyst. Provide detailed, actionable insights about job postings in JSON format.'
            },
            {
              role: 'user',
              content: prompt
            }
          ],
          response_format: { type: 'json_object' },
          max_tokens: 1000
        })

        const result = completion.choices[0].message.content
        if (result) {
          const aiInsights = JSON.parse(result)
          jobAnalysis = {
            ...jobAnalysis,
            aiInsights,
            technicalRequirements: aiInsights.technicalRequirements || [],
            cultureIndicators: aiInsights.cultureIndicators || [],
            growthOpportunities: aiInsights.growthOpportunities || [],
            interviewHints: aiInsights.interviewHints || [],
            concerns: aiInsights.concerns || []
          }
          console.log('✅ AI-enhanced job analysis completed')
        }
      } catch (aiError) {
        console.log('⚠️ AI enhancement failed, using basic analysis:', aiError)
      }
    }
    
    const endTime = Date.now()
    console.log(`✅ Job analysis complete in ${endTime - startTime}ms:`, jobAnalysis.title, 'at', jobAnalysis.company)

    return Response.json({
      success: true,
      jobAnalysis,
      processingTime: endTime - startTime,
      message: 'Job analysis completed successfully'
    });

  } catch (error) {
    console.error('❌ === JOB ANALYSIS ERROR ===', error)
    return Response.json({
      error: 'Job analysis failed',
      details: (error as any)?.message || 'Unknown error'
    }, { status: 500 });
  }
} 
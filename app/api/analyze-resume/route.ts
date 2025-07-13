import { NextRequest } from 'next/server'
import { parseResumeWithEnhancedAI } from '../../../lib/enhanced-resume-parser'
import { track } from '@vercel/analytics/server'

export async function POST(req: NextRequest) {
  console.log('🚀 === IMMEDIATE RESUME ANALYSIS: Starting ===')
  
  try {
    const body = await req.json();
    console.log('📄 Resume analysis request received:', {
      hasResumeText: !!body.resumeText,
      resumeTextLength: body.resumeText?.length || 0
    })
    
    if (!body.resumeText) {
      await track('Resume Analysis Failed', {
        error: 'No resume text provided',
        source: 'server'
      })
      return Response.json({ error: 'Resume text is required' }, { status: 400 });
    }

    const startTime = Date.now()
    
    // Step 1: Resume Analysis
    console.log('📊 === STEP 1: RESUME ANALYSIS ===')
    const resumeData = await parseResumeWithEnhancedAI(body.resumeText);
    
    const endTime = Date.now()
    const processingTime = endTime - startTime
    console.log(`✅ Resume analysis complete in ${processingTime}ms:`, resumeData.name, resumeData.currentRole)

    // Track successful resume analysis
    await track('Resume Analysis Server Success', {
      candidateName: resumeData.name || 'Unknown',
      currentRole: resumeData.currentRole || 'Unknown',
      experienceYears: resumeData.experienceYears || 0,
      processingTimeMs: processingTime,
      contentLength: body.resumeText.length,
      skillsCount: Object.values(resumeData.technicalSkills || {}).flat().length,
      projectsCount: (resumeData.projects || []).length
    })

    return Response.json({
      success: true,
      resumeData,
      processingTime: processingTime,
      message: 'Resume analysis completed successfully'
    });

  } catch (error) {
    console.error('❌ === RESUME ANALYSIS ERROR ===', error)
    
    // Track failed resume analysis
    await track('Resume Analysis Server Error', {
      error: (error as any)?.message || 'Unknown error',
      source: 'server'
    })
    
    return Response.json({
      error: 'Resume analysis failed',
      details: (error as any)?.message || 'Unknown error'
    }, { status: 500 });
  }
} 
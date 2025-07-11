import { NextRequest } from 'next/server'
import { parseResumeWithEnhancedAI } from '../../../lib/enhanced-resume-parser'

export async function POST(req: NextRequest) {
  console.log('🚀 === DIRECT ANALYZE: Starting ===')
  
  try {
    const body = await req.json();
    console.log('📄 Request received:', {
      hasResumeText: !!body.resumeText,
      resumeTextLength: body.resumeText?.length || 0
    })
    
    if (!body.resumeText) {
      return Response.json({ error: 'Resume text is required' }, { status: 400 });
    }

    console.log('🧠 === Calling parseResumeWithEnhancedAI ===')
    const startTime = Date.now()
    const resumeData = await parseResumeWithEnhancedAI(body.resumeText);
    const endTime = Date.now()
    
    console.log(`✅ === Analysis completed in ${endTime - startTime}ms ===`)
    console.log('📊 Results:', {
      name: resumeData.name,
      role: resumeData.currentRole,
      experience: resumeData.experienceYears
    })

    return Response.json({
      success: true,
      resumeData,
      processingTime: endTime - startTime,
      message: 'Analysis completed successfully'
    });

  } catch (error) {
    console.error('❌ === DIRECT ANALYZE ERROR ===', error)
    return Response.json({
      error: 'Analysis failed',
      details: (error as any)?.message || 'Unknown error'
    }, { status: 500 });
  }
} 
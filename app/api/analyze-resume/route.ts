import { NextRequest } from 'next/server'
import { parseResumeWithEnhancedAI } from '../../../lib/enhanced-resume-parser'

export async function POST(req: NextRequest) {
  console.log('🚀 === IMMEDIATE RESUME ANALYSIS: Starting ===')
  
  try {
    const body = await req.json();
    console.log('📄 Resume analysis request received:', {
      hasResumeText: !!body.resumeText,
      resumeTextLength: body.resumeText?.length || 0
    })
    
    if (!body.resumeText) {
      return Response.json({ error: 'Resume text is required' }, { status: 400 });
    }

    const startTime = Date.now()
    
    // Step 1: Resume Analysis
    console.log('📊 === STEP 1: RESUME ANALYSIS ===')
    const resumeData = await parseResumeWithEnhancedAI(body.resumeText);
    
    const endTime = Date.now()
    console.log(`✅ Resume analysis complete in ${endTime - startTime}ms:`, resumeData.name, resumeData.currentRole)

    return Response.json({
      success: true,
      resumeData,
      processingTime: endTime - startTime,
      message: 'Resume analysis completed successfully'
    });

  } catch (error) {
    console.error('❌ === RESUME ANALYSIS ERROR ===', error)
    return Response.json({
      error: 'Resume analysis failed',
      details: (error as any)?.message || 'Unknown error'
    }, { status: 500 });
  }
} 
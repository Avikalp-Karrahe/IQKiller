import { NextRequest } from 'next/server'
import { parseResumeWithEnhancedAI } from '../../../lib/enhanced-resume-parser'
import { track } from '@vercel/analytics/server'

// Feature flags for server-side tracking
const FEATURE_FLAGS = {
  PREMIUM_FEATURES_ENABLED: 'premium-features-enabled',
  AI_MODEL_VERSION: 'ai-model-version',
  QUESTION_GENERATION_V2: 'question-generation-v2',
  CUSTOM_COMPANY_RESEARCH: 'custom-company-research',
  ADVANCED_RESUME_PARSING: 'advanced-resume-parsing'
}

// Helper to report feature flag values
const reportFeatureFlags = () => {
  // Note: In a real app, you would use the actual reportValue from 'flags' package
  // For now, we'll simulate the flag values
  const flags = {
    [FEATURE_FLAGS.PREMIUM_FEATURES_ENABLED]: true,
    [FEATURE_FLAGS.AI_MODEL_VERSION]: 'gpt-4',
    [FEATURE_FLAGS.QUESTION_GENERATION_V2]: true,
    [FEATURE_FLAGS.CUSTOM_COMPANY_RESEARCH]: true,
    [FEATURE_FLAGS.ADVANCED_RESUME_PARSING]: true
  }
  
  // In a real implementation, you would call reportValue for each flag
  // reportValue('premium-features-enabled', flags.premiumFeaturesEnabled)
  // reportValue('ai-model-version', flags.aiModelVersion)
  // etc.
  
  return flags
}

export async function POST(req: NextRequest) {
  console.log('🚀 === IMMEDIATE RESUME ANALYSIS: Starting ===')
  
  // Report feature flags for this request
  const flags = reportFeatureFlags()
  
  try {
    const body = await req.json();
    console.log('📄 Resume analysis request received:', {
      hasResumeText: !!body.resumeText,
      resumeTextLength: body.resumeText?.length || 0
    })
    
    if (!body.resumeText) {
      await track('Resume Analysis Failed', {
        error: 'No resume text provided',
        source: 'server',
        timestamp: new Date().toISOString()
      }, { 
        flags: [
          FEATURE_FLAGS.ADVANCED_RESUME_PARSING,
          FEATURE_FLAGS.AI_MODEL_VERSION
        ]
      })
      return Response.json({ error: 'Resume text is required' }, { status: 400 });
    }

    const startTime = Date.now()
    
    // Step 1: Resume Analysis
    console.log('📊 === STEP 1: RESUME ANALYSIS ===')
    const resumeData = await parseResumeWithEnhancedAI(body.resumeText)
    console.log('✅ Resume analysis complete in 0ms:', resumeData.name, `${resumeData.experienceYears} years`, resumeData.currentRole)
    console.log('🔍 Debug - Experience Years:', resumeData.experienceYears, typeof resumeData.experienceYears)
    
    const processingTime = Date.now() - startTime
    
    // Track successful resume analysis with feature flags
    await track('Resume Analysis Complete', {
      processingTime,
      candidateName: resumeData.name || 'Unknown',
      experienceYears: resumeData.experienceYears || 0,
      skillsCount: resumeData.technicalSkills?.programmingLanguages?.length || 0,
      contentLength: body.resumeText.length,
      aiModelVersion: flags[FEATURE_FLAGS.AI_MODEL_VERSION],
      timestamp: new Date().toISOString()
    }, { 
      flags: [
        FEATURE_FLAGS.ADVANCED_RESUME_PARSING,
        FEATURE_FLAGS.AI_MODEL_VERSION
      ]
    })

    return Response.json({
      success: true,
      data: {
        resumeData,
        processingTime,
        metadata: {
          aiModelUsed: flags[FEATURE_FLAGS.AI_MODEL_VERSION],
          advancedParsingEnabled: flags[FEATURE_FLAGS.ADVANCED_RESUME_PARSING]
        }
      }
    })

  } catch (error) {
    console.error('❌ === RESUME ANALYSIS ERROR ===', error)
    
    // Track resume analysis failure with feature flags
    await track('Resume Analysis Failed', {
      error: error instanceof Error ? error.message : 'Unknown error',
      source: 'server',
      timestamp: new Date().toISOString()
    }, { 
      flags: [
        FEATURE_FLAGS.ADVANCED_RESUME_PARSING,
        FEATURE_FLAGS.AI_MODEL_VERSION
      ]
    })

    return Response.json(
      { 
        success: false, 
        error: error instanceof Error ? error.message : 'Resume analysis failed',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    )
  }
} 
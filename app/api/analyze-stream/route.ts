import { openai, getModel } from '@/lib/openai'
import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'
import { processQuestionBank, selectQuestionsByRole, type Question } from '@/lib/questions-processor'
import { researchCompanyInsights, generateSalaryInsights, type CompanyInsights } from '@/lib/company-research'
import { parseResumeWithEnhancedAI, type DetailedResumeData } from '@/lib/enhanced-resume-parser'
import { createHighlyPersonalizedQuestions, generatePersonalizedIntroduction, generatePersonalizedTalkingPoints, type PersonalizationContext } from '@/lib/enhanced-question-personalizer'
import fs from 'fs'
import path from 'path'

// Enhanced AI-powered resume analysis
async function analyzeResume(resumeText: string): Promise<DetailedResumeData> {
  console.log('🔍 === ANALYZE RESUME FUNCTION STARTED ===')
  console.log('📝 Resume text length:', resumeText.length)
  
  if (!resumeText || resumeText.trim().length === 0) {
    throw new Error('Resume text is empty or invalid')
  }
  
  try {
    console.log('🚀 === CALLING parseResumeWithEnhancedAI ===')
  // Use enhanced AI parsing for detailed extraction
    const result = await parseResumeWithEnhancedAI(resumeText)
    console.log('✅ === parseResumeWithEnhancedAI COMPLETED ===')
    console.log('📊 Resume analysis completed successfully:', {
      name: result.name,
      experienceYears: result.experienceYears,
      skillsCount: Object.keys(result.technicalSkills).length,
      projectsCount: result.projects.length
    })
    return result
  } catch (error) {
    console.error('❌ === ERROR in analyzeResume function ===')
    console.error('Error details:', error)
    if (error instanceof Error) {
      throw new Error(`Resume analysis failed: ${error.message}`)
    }
    throw new Error('Resume analysis failed due to unexpected error')
  }
}

async function analyzeJobMatch(resumeData: DetailedResumeData, jobDescription: string) {
  console.log('Starting job match analysis...')
  try {
    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini-2024-07-18',
      messages: [
        {
          role: 'system',
          content: 'You are an expert at analyzing job compatibility based on candidate background.'
        },
        {
          role: 'user',
          content: `
            Analyze the compatibility between this candidate's detailed background and the job requirements.
            
            CANDIDATE PROFILE:
            - Experience: ${resumeData.experienceDescription}
            - Education: ${resumeData.education.degree} in ${resumeData.education.field}
            - Technical Skills: ${Object.values(resumeData.technicalSkills).flat().join(', ')}
            - Projects: ${resumeData.projects.length} projects
            - Key Achievements: ${resumeData.achievements.map(a => a.description).join(', ')}
            
            JOB REQUIREMENTS:
            ${jobDescription}
            
            Provide a detailed compatibility analysis with precise scores and specific skill matching.
            Calculate exact percentages based on skills overlap, experience level, and education match.
          `
        }
      ],
      response_format: { type: 'json_object' }
    })
    
    const result = completion.choices[0].message.content
    if (!result) throw new Error('No content in response')
    
    const schema = z.object({
      overallMatch: z.number().min(0).max(100),
      skillsMatch: z.number().min(0).max(100),
      experienceMatch: z.number().min(0).max(100),
      educationMatch: z.number().min(0).max(100),
      missingSkills: z.array(z.string()),
      strongMatches: z.array(z.string()),
      partialMatches: z.array(z.string()),
      recommendedFocus: z.array(z.string())
    })
    
    const parsedResult = schema.parse(JSON.parse(result))
    console.log('Job match analysis completed:', {
      overallMatch: parsedResult.overallMatch,
      skillsMatch: parsedResult.skillsMatch,
      missingSkillsCount: parsedResult.missingSkills.length
    })
    return parsedResult
  } catch (error) {
    console.error('Error in job match analysis:', error)
    throw error
  }
}

async function generateInterviewQuestion(skillArea: string, difficulty: string) {
  console.log('Generating interview question:', { skillArea, difficulty })
  try {
  const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini-2024-07-18',
    messages: [
      {
        role: 'system',
        content: 'You are an expert at creating interview questions.'
      },
      {
        role: 'user',
        content: `Generate a ${difficulty} interview question about ${skillArea}. 
        Format: Question, Expected Answer, Follow-up Questions.
        Make it practical and specific.`
      }
    ],
      response_format: { type: 'json_object' }
    })
    console.log('Question generation completed for:', skillArea)
    return completion.choices[0].message.content
  } catch (error) {
    console.error('Error generating interview question:', error)
    throw error
  }
}

async function loadQuestionBank(): Promise<Question[]> {
  console.log('Loading question bank...')
  try {
    // Try to load the real CSV file
    const csvPath = path.join(process.cwd(), 'Question_bank_IQ_categorized/summary (1).csv')
    
    let csvData = ''
    try {
      csvData = fs.readFileSync(csvPath, 'utf-8')
      console.log('Successfully loaded question bank CSV')
    } catch (error) {
      console.warn('Failed to load CSV, using fallback data:', error)
      // Fallback to sample data if CSV not found
      csvData = `idx,title,type,summaries,link
0,Weekly Aggregation,python,"Summary: Group a list of sequential timestamps into weekly lists starting from the first timestamp.",interviewquery.com/questions/weekly-aggregation
1,Decreasing Comments,product metrics,"Summary: Identify reasons and metrics for decreasing average comments per user despite user growth in a new city.",interviewquery.com/questions/decreasing-comments
2,Employee Salaries,sql,"Summary: Select the top 3 departments with at least ten employees, ranked by the percentage of employees earning over 100K.",interviewquery.com/questions/employee-salaries
3,500 Cards,probability,"Summary: Determine the probability of drawing three cards in increasing order from a shuffled deck of 500 numbered cards.",interviewquery.com/questions/500-cards
4,Random Number,algorithms,"Summary: Select a random number from a stream with equal probability using O(1) space.",interviewquery.com/questions/random-number`
    }
    
    const questions = processQuestionBank(csvData)
    console.log('Question bank processed:', { questionCount: questions.length })
    return questions
  } catch (error) {
    console.error('Error loading question bank:', error)
    return []
  }
}

// Old personalization function removed - now using enhanced version from enhanced-question-personalizer.ts

export async function POST(req: NextRequest) {
  console.log('=== ANALYZE-STREAM: POST Request Started ===')
  const encoder = new TextEncoder();
  const stream = new TransformStream();
  const writer = stream.writable.getWriter();

  const writeToStream = async (data: any) => {
    console.log(`=== STREAMING: ${data.step} - ${data.status} ===`)
    try {
      // Add timeout to stream writing
      const writePromise = writer.write(encoder.encode('data: ' + JSON.stringify(data) + '\n\n'));
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Stream write timeout')), 5000)
      );
      
      await Promise.race([writePromise, timeoutPromise]);
      console.log(`✅ === STREAM WRITE SUCCESS: ${data.step} ===`)
    } catch (error) {
      console.error(`❌ === STREAM WRITE FAILED: ${data.step} ===`, error);
      throw error;
    }
  };

  try {
    console.log('=== PARSING REQUEST BODY ===')
    const body = await req.json();
    console.log('Request body parsed successfully:', {
      hasResumeText: !!body.resumeText,
      resumeTextLength: body.resumeText?.length || 0,
      hasJobDescription: !!body.jobDescription,
      hasJobData: !!body.jobData
    })
    
    // Validate request body
    if (!body.resumeText) {
      throw new Error('Resume text is required');
    }

    console.log('=== STARTING STEP 1: RESUME ANALYSIS ===')
    // Start resume analysis
    console.log('🎬 === ABOUT TO WRITE TO STREAM ===')
    await writeToStream({
      step: 'resume_analysis',
      status: 'processing',
      message: 'Analyzing resume...',
      progress: 10
    });
    console.log('✅ === STREAM WRITE COMPLETED ===')

    console.log('=== CALLING analyzeResume() ===')
    console.log('🔍 About to analyze resume with text length:', body.resumeText.length)
    
    let resumeData: DetailedResumeData;
    try {
      const resumeAnalysisStart = Date.now()
      resumeData = await analyzeResume(body.resumeText);
      const resumeAnalysisEnd = Date.now()
      console.log(`✅ === analyzeResume() COMPLETED in ${resumeAnalysisEnd - resumeAnalysisStart}ms ===`)
      console.log('📊 Resume data extracted:', {
        name: resumeData.name,
        role: resumeData.currentRole,
        experience: resumeData.experienceYears,
        skills: Object.values(resumeData.technicalSkills).flat().length
      })
      
      await writeToStream({
        step: 'resume_analysis',
        status: 'completed',
        message: 'Resume analysis complete',
        progress: 100,
        results: resumeData
      });
    } catch (resumeError) {
      console.error('❌ === RESUME ANALYSIS FAILED ===')
      console.error('Resume error type:', resumeError?.constructor?.name)
      console.error('Resume error message:', (resumeError as any)?.message)
      console.error('Resume error stack:', (resumeError as any)?.stack)
      
      await writeToStream({
        step: 'resume_analysis',
        status: 'error',
        message: `Resume analysis failed: ${(resumeError as any)?.message || 'Unknown error'}`,
        progress: 0,
        error: true
      });
      throw resumeError;
    }

    console.log('=== STARTING STEP 2: JOB MATCHING ===')
    // Start job matching
    await writeToStream({
      step: 'job_matching',
      status: 'processing',
      message: 'Analyzing job compatibility...',
      progress: 10
    });

    const jobData = body.jobData || {};
    const jobDescription = body.jobDescription || jobData.description || '';
    console.log('=== CALLING analyzeJobMatch() ===')
    const matchData = await analyzeJobMatch(resumeData, jobDescription);
    console.log('=== analyzeJobMatch() COMPLETED ===')

    await writeToStream({
      step: 'job_matching',
      status: 'completed',
      message: 'Job matching complete',
      progress: 100,
      results: matchData
    });

    console.log('=== STARTING STEP 3: QUESTION GENERATION ===')
    // Start question generation
    await writeToStream({
      step: 'question_generation',
      status: 'processing',
      message: 'Generating interview questions...',
      progress: 10
    });

    // Load and process questions
    console.log('=== CALLING loadQuestionBank() ===')
    const questionBank = await loadQuestionBank();
    console.log('=== loadQuestionBank() COMPLETED ===')
    console.log('Starting question selection and personalization')
    const selectedQuestions = await selectQuestionsByRole(questionBank, jobData.title || 'Software Engineer', 'technical');

    await writeToStream({
      step: 'question_generation',
      status: 'completed',
      message: 'Question generation complete',
      progress: 100,
      results: selectedQuestions
    });

    console.log('=== STARTING STEP 4: QUESTION PERSONALIZATION ===')
    // Step 4: Questions Ready
    await writeToStream({
      step: 'question_generated',
      status: 'processing',
      message: 'Preparing personalized questions...',
      progress: 10
    });

    // Personalize questions if we have enhanced context
    let personalizedQuestions = selectedQuestions;
    if (jobData.role && jobData.company) {
      try {
        console.log('=== PERSONALIZING QUESTIONS ===')
        const personalizationContext: PersonalizationContext = {
          resumeData,
          jobData: {
            role: jobData.role || jobData.title,
            company: jobData.company,
            location: jobData.location || '',
            description: jobDescription,
            requirements: jobData.requirements || []
          },
          matchScore: matchData.overallMatch
        };
        
        const technicalQuestions = selectQuestionsByRole(questionBank, jobData.role, 'technical').slice(0, 3);
        personalizedQuestions = await createHighlyPersonalizedQuestions(technicalQuestions, personalizationContext);
        console.log('=== QUESTION PERSONALIZATION COMPLETED ===')
      } catch (error) {
        console.log('Personalization failed, using selected questions:', error);
      }
    } else {
      console.log('=== SKIPPING PERSONALIZATION (no role/company) ===')
    }

    await writeToStream({
      step: 'question_generated',
      status: 'completed',
      message: 'Personalized questions ready',
      progress: 100,
      results: personalizedQuestions
    });

    console.log('=== STARTING STEP 5: FINAL ANALYSIS ===')
    // Step 5: Final Analysis
    await writeToStream({
      step: 'final_analysis',
      status: 'processing',
      message: 'Generating final analysis...',
      progress: 10
    });

    const finalAnalysis = await generateFinalAnalysis(resumeData, matchData);

    await writeToStream({
      step: 'final_analysis',
      status: 'completed',
      message: 'Final analysis complete',
      progress: 100,
      results: finalAnalysis
    });

    console.log('=== STARTING STEP 6: COMPREHENSIVE GUIDE ===')
    // Step 6: Comprehensive Guide
    await writeToStream({
      step: 'comprehensive_guide',
      status: 'processing',
      message: 'Creating comprehensive guide...',
      progress: 10
    });

    let comprehensiveGuide;
    try {
      console.log('=== CALLING generateComprehensiveGuide() ===')
      comprehensiveGuide = await generateComprehensiveGuide(finalAnalysis, jobData, resumeData);
      console.log('=== generateComprehensiveGuide() COMPLETED ===')
    } catch (error) {
      console.log('Guide generation failed, creating basic guide:', error);
      comprehensiveGuide = {
        title: `Interview Guide - ${jobData.role || 'Position'}`,
        summary: 'Basic interview preparation guide',
        questions: personalizedQuestions,
        analysis: finalAnalysis
      };
    }

    await writeToStream({
      step: 'comprehensive_guide',
      status: 'completed',
      message: 'Comprehensive guide ready',
      progress: 100,
      results: comprehensiveGuide
    });

    console.log('=== STARTING STEP 7: COMPLETION ===')
    // Step 7: Completion
    await writeToStream({
      step: 'completed',
      status: 'completed',
      message: 'Analysis complete! All steps finished successfully.',
      progress: 100,
      results: {
        resumeData,
        matchData,
        selectedQuestions: personalizedQuestions,
        finalAnalysis,
        comprehensiveGuide,
        summary: {
          overallMatch: matchData.overallMatch,
          questionsGenerated: personalizedQuestions.length,
          completedAt: new Date().toISOString()
        }
      }
    });

    console.log('=== CLOSING STREAM ===')
    writer.close();
    console.log('=== ANALYZE-STREAM: REQUEST COMPLETED SUCCESSFULLY ===')
    
    return new Response(stream.readable, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });
  } catch (error) {
    console.error('=== ERROR IN ANALYZE-STREAM ===', error)
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    
    try {
      await writeToStream({
        step: 'error',
        status: 'error',
        message: errorMessage,
        error: true
      });
    } catch (streamError) {
      console.error('Error writing to stream:', streamError);
    }
    
    try {
      writer.close();
    } catch (writerError) {
      console.error('Error closing writer:', writerError);
    }
    
    return new Response(stream.readable, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });
  }
}

async function generateFinalAnalysis(resumeData: DetailedResumeData, matchData: any) {
  return {
    overallMatch: matchData.overallMatch,
    skillsBreakdown: {
      technical: matchData.skillsMatch,
      experience: matchData.experienceMatch,
      education: matchData.educationMatch || 85,
      culture: 78
    },
    salaryInsights: {
      range: { min: '95k', max: '135k' },
      median: '115k',
      percentile: '75th',
      tip: `Consider negotiating 10-15% above base offer based on your ${resumeData.experienceDescription} and ${resumeData.education.degree}`
    }
  }
}

async function generateComprehensiveGuide(finalAnalysis: any, jobData: any, resumeData: DetailedResumeData) {
  try {
    // Load question bank and research company insights
    const [questionBank, companyInsights] = await Promise.all([
      loadQuestionBank(),
      researchCompanyInsights(jobData.company, jobData.role || jobData.title, jobData.location)
    ])
    
    // Create personalization context
    const personalizationContext: PersonalizationContext = {
      resumeData,
      jobData: {
        role: jobData.role || jobData.title,
        company: jobData.company,
        location: jobData.location,
        description: jobData.description || jobData.fullContent || '',
        requirements: jobData.requirements || []
      },
      matchScore: finalAnalysis.overallMatch
    }

    // Select and personalize questions
    const technicalQuestions = selectQuestionsByRole(questionBank, jobData.role, 'technical').slice(0, 4)
    const behavioralQuestions = selectQuestionsByRole(questionBank, jobData.role, 'behavioral').slice(0, 3)
    const caseStudyQuestions = selectQuestionsByRole(questionBank, jobData.role, 'caseStudy').slice(0, 3)
    
    const [personalizedTechnical, personalizedBehavioral, personalizedCaseStudy] = await Promise.all([
      createHighlyPersonalizedQuestions(technicalQuestions, personalizationContext),
      createHighlyPersonalizedQuestions(behavioralQuestions, personalizationContext),
      createHighlyPersonalizedQuestions(caseStudyQuestions, personalizationContext)
    ])

    // Generate personalized introduction and talking points
    const personalizedIntro = generatePersonalizedIntroduction(resumeData, jobData, finalAnalysis.overallMatch)
    const talkingPoints = generatePersonalizedTalkingPoints(resumeData)

    // Generate comprehensive guide
    return {
      title: `${jobData.role} Interview Guide - ${jobData.company}`,
      introduction: {
        roleOverview: personalizedIntro,
        culture: `${jobData.company}'s culture: ${companyInsights.culture}`,
        whyThisRole: `This role offers unique opportunities to leverage your ${resumeData.experienceDescription} and ${resumeData.education.degree} background.`
      },
      interviewProcess: {
        diagram: `Interview Process:\n${companyInsights.interviewProcess.stages.map((stage, idx) => `${idx + 1}. **${stage.name}** (${stage.duration}) - ${stage.description}`).join('\n')}`,
        stages: companyInsights.interviewProcess.stages,
        levelDifferences: `**${resumeData.experienceYears} Years Experience Level**: Given your ${resumeData.experienceDescription}, expect questions that test both foundational knowledge and practical application.`
      },
      questions: {
        technical: personalizedTechnical,
        behavioral: personalizedBehavioral,
        caseStudy: personalizedCaseStudy
      },
      preparation: {
        tips: [
          {
            title: 'Technical Preparation',
            description: `Focus on your experience with ${resumeData.technicalSkills.programmingLanguages.slice(0, 3).join(', ')}.`
          },
          {
            title: 'Project Examples',
            description: `Prepare detailed examples from your ${resumeData.stats.totalProjects} projects.`
          }
        ],
        studyPlan: 'Customized study plan based on your background and the role requirements.',
        mockInterviews: 'Practice with peers or use interview preparation services.'
      },
      talkingPoints,
      metadata: {
        generatedAt: new Date().toISOString(),
        personalizedFor: resumeData.name,
        targetRole: jobData.role,
        targetCompany: jobData.company,
        matchScore: `${Math.floor(finalAnalysis.overallMatch)}%`
      }
    }
  } catch (error) {
    console.error('Guide generation error:', error)
    throw error
  }
}
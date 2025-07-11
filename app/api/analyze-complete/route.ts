import { NextRequest } from 'next/server'
import { parseResumeWithEnhancedAI } from '../../../lib/enhanced-resume-parser'
import { generateEnhancedQuestions, type EnhancedResumeData, type JobContext } from '../../../lib/enhanced-question-generator'
import { generatePremiumContent, type PremiumPreparationPlan } from '../../../lib/premium-content-enhancer'
import { generatePremiumCoaching, type PremiumCoachingFeatures } from '../../../lib/premium-coaching-engine'
import { openai } from '@/lib/openai'

// Helper function to normalize question categories
function normalizeCategory(category: string): string {
  const cat = category.toLowerCase().trim()
  if (cat.includes('technical')) return 'technical'
  if (cat.includes('behavioral')) return 'behavioral'  
  if (cat.includes('system') || cat.includes('design')) return 'system-design'
  return 'technical' // default fallback
}

// Generate exactly 5 personalized questions for each category (15 total)
async function generatePersonalizedQuestionsByCategory(resumeData: any, jobData: any, jobContext: any) {
  try {
    console.log('🎯 === GENERATING 5 QUESTIONS PER CATEGORY ===')
    
    // Generate Technical Questions (5)
    const technicalPrompt = `You are conducting a technical interview for a ${jobContext.role} position at ${jobContext.company}. 

Generate exactly 5 personalized technical questions based on the candidate's specific background.

CANDIDATE'S TECHNICAL BACKGROUND:
- Name: ${resumeData.name}
- Experience: ${resumeData.experienceYears} years
- Programming Languages: ${resumeData.technicalSkills.programmingLanguages.join(', ')}
- Frameworks: ${resumeData.technicalSkills.frameworks.join(', ')}
- Databases: ${resumeData.technicalSkills.databases.join(', ')}
- Tools: ${resumeData.technicalSkills.tools.join(', ')}
- Key Projects: ${resumeData.projects.map((p: any) => `${p.title} (${p.technologies.join(', ')})`).join('; ')}

JOB REQUIREMENTS:
- Role: ${jobContext.role}
- Required Skills: ${jobData.skills ? jobData.skills.join(', ') : 'General development'}
- Experience Level: ${jobData.experienceLevel || 'Mid-level'}

Generate 5 technical questions that:
1. Reference their specific technologies and projects
2. Test problem-solving abilities relevant to the role
3. Are appropriate for ${resumeData.experienceYears} years of experience
4. Feel conversational and personal

Examples:
- "I see you used ${resumeData.technicalSkills.programmingLanguages[0]} in your ${resumeData.projects[0]?.title} project. Can you walk me through..."
- "Your experience with ${resumeData.technicalSkills.frameworks[0]} is interesting. How would you..."

Return JSON format: {"questions": [{"question": "...", "reasoning": "..."}]}`

    const behavioralPrompt = `You are conducting a behavioral interview for a ${jobContext.role} position at ${jobContext.company}.

Generate exactly 5 personalized behavioral questions based on the candidate's specific experiences.

CANDIDATE'S BACKGROUND:
- Name: ${resumeData.name}
- Current Role: ${resumeData.currentRole}
- Experience: ${resumeData.experienceYears} years
- Education: ${resumeData.education.degree} in ${resumeData.education.field}
- Achievements: ${resumeData.achievements.map((a: { description: string }) => a.description).join('; ')}
- Projects: ${resumeData.projects.map((p: { title: string }) => p.title).join(', ')}

Generate 5 behavioral questions that:
1. Reference their specific achievements and experiences
2. Use STAR method (Situation, Task, Action, Result)
3. Are relevant to ${jobContext.role} responsibilities
4. Feel personal and specific to their background

Examples:
- "You mentioned ${resumeData.achievements[0]?.description}. Can you tell me about a time when..."
- "In your role as ${resumeData.currentRole}, describe a challenging situation where..."

Return JSON format: {"questions": [{"question": "...", "reasoning": "..."}]}`

    const systemDesignPrompt = `You are conducting a system design interview for a ${jobContext.role} position at ${jobContext.company}.

Generate exactly 5 system design questions appropriate for someone with ${resumeData.experienceYears} years of experience.

CANDIDATE'S BACKGROUND:
- Experience Level: ${resumeData.experienceYears} years
- Technical Skills: ${resumeData.technicalSkills.programmingLanguages.join(', ')}
- System Experience: ${resumeData.technicalSkills.frameworks.join(', ')}
- Database Knowledge: ${resumeData.technicalSkills.databases.join(', ')}
- Project Scale: ${resumeData.projects.map((p: { title: string }) => p.title).join(', ')}

Generate 5 system design questions that:
1. Are appropriate for ${resumeData.experienceYears <= 2 ? 'junior' : resumeData.experienceYears <= 5 ? 'mid' : 'senior'} level
2. Reference technologies they've worked with
3. Are relevant to ${jobContext.role} responsibilities
4. Scale appropriately with their experience

For ${resumeData.experienceYears <= 2 ? 'junior' : 'experienced'} candidates:
${resumeData.experienceYears <= 2 ? 
  '- Focus on basic architecture concepts and simple system design' : 
  '- Include scalability, performance, and complex distributed systems'}

Return JSON format: {"questions": [{"question": "...", "reasoning": "..."}]}`

    // Make parallel API calls for all three categories
    const [technicalResponse, behavioralResponse, systemDesignResponse] = await Promise.all([
      openai.chat.completions.create({
        model: 'gpt-4o-mini-2024-07-18',
        messages: [
          { role: 'system', content: 'You are an expert technical interviewer. Generate exactly 5 personalized questions in JSON format.' },
          { role: 'user', content: technicalPrompt }
        ],
        response_format: { type: 'json_object' },
        max_tokens: 1000
      }),
      openai.chat.completions.create({
        model: 'gpt-4o-mini-2024-07-18',
        messages: [
          { role: 'system', content: 'You are an expert behavioral interviewer. Generate exactly 5 personalized questions in JSON format.' },
          { role: 'user', content: behavioralPrompt }
        ],
        response_format: { type: 'json_object' },
        max_tokens: 1000
      }),
      openai.chat.completions.create({
        model: 'gpt-4o-mini-2024-07-18',
        messages: [
          { role: 'system', content: 'You are an expert system design interviewer. Generate exactly 5 personalized questions in JSON format.' },
          { role: 'user', content: systemDesignPrompt }
        ],
        response_format: { type: 'json_object' },
        max_tokens: 1000
      })
    ])

    // Parse responses
    const technicalQuestions = JSON.parse(technicalResponse.choices[0].message.content || '{"questions": []}').questions || []
    const behavioralQuestions = JSON.parse(behavioralResponse.choices[0].message.content || '{"questions": []}').questions || []
    const systemDesignQuestions = JSON.parse(systemDesignResponse.choices[0].message.content || '{"questions": []}').questions || []

    // Combine with normalized categories and transform to match UI interface
    const allQuestions = [
      ...technicalQuestions.map((q: any, idx: number) => ({ 
        idx: idx + 1,
        title: q.question,
        summaries: q.reasoning || 'Personalized question based on your background',
        type: 'technical',
        category: 'technical',
        difficulty: (resumeData.experienceYears <= 2 ? 'junior' : resumeData.experienceYears <= 5 ? 'mid' : 'senior') as 'junior' | 'mid' | 'senior',
        link: '',
        isPersonalized: true,
        approach: `Focus on demonstrating your practical experience with ${resumeData.technicalSkills.programmingLanguages.slice(0, 2).join(' and ')}.`,
        relevance: `This question is tailored to your ${resumeData.experienceYears} years of experience and technical background.`,
        followUps: [
          'Can you walk me through your thought process?',
          'How would you optimize this solution?',
          'What alternative approaches did you consider?'
        ]
      })),
      ...behavioralQuestions.map((q: any, idx: number) => ({ 
        idx: idx + 1,
        title: q.question,
        summaries: q.reasoning || 'Behavioral question based on your specific experiences',
        type: 'behavioral',
        category: 'behavioral',
        difficulty: (resumeData.experienceYears <= 2 ? 'junior' : resumeData.experienceYears <= 5 ? 'mid' : 'senior') as 'junior' | 'mid' | 'senior',
        link: '',
        isPersonalized: true,
        approach: 'Use the STAR method (Situation, Task, Action, Result) to structure your response.',
        relevance: `This question references your specific achievements and project experience.`,
        followUps: [
          'What would you do differently next time?',
          'How did you measure success?',
          'What did you learn from this experience?'
        ]
      })),
      ...systemDesignQuestions.map((q: any, idx: number) => ({ 
        idx: idx + 1,
        title: q.question,
        summaries: q.reasoning || 'System design question appropriate for your experience level',
        type: 'system-design',
        category: 'system-design',
        difficulty: (resumeData.experienceYears <= 2 ? 'junior' : resumeData.experienceYears <= 5 ? 'mid' : 'senior') as 'junior' | 'mid' | 'senior',
        link: '',
        isPersonalized: true,
        approach: `Start with high-level architecture, then dive into components. Consider scalability appropriate for ${resumeData.experienceYears <= 2 ? 'early-career' : 'experienced'} level.`,
        relevance: `Scaled to your ${resumeData.experienceYears} years of experience and technical background.`,
        followUps: [
          'How would you handle increased load?',
          'What are the potential failure points?',
          'How would you monitor this system?'
        ]
      }))
    ]

    console.log(`✅ Generated ${allQuestions.length} personalized questions:`)
    console.log(`   • Technical: ${technicalQuestions.length}`)
    console.log(`   • Behavioral: ${behavioralQuestions.length}`)
    console.log(`   • System Design: ${systemDesignQuestions.length}`)

    return allQuestions

  } catch (error) {
    console.error('❌ Personalized question generation failed:', error)
    // Fallback to ensure we always have some questions
    return [
      { category: 'technical', question: 'Tell me about your experience with the technologies listed on your resume.', reasoning: 'Fallback question', isPersonalized: false },
      { category: 'behavioral', question: 'Describe a challenging project you worked on and how you overcame obstacles.', reasoning: 'Fallback question', isPersonalized: false },
      { category: 'system-design', question: 'How would you design a simple web application architecture?', reasoning: 'Fallback question', isPersonalized: false }
    ]
  }
}

// Enhanced job matching using AI with scraped structured data
async function generateEnhancedJobMatch(resumeData: any, jobData: any, jobDescription: string) {
  try {
    console.log('🤖 === GENERATING ENHANCED JOB MATCH WITH AI ===')
    
    const structuredJobData = jobData.structuredData || {};
    const jobContent = jobData.content || jobDescription || '';
    
    const prompt = `Analyze the compatibility between this candidate and the job posting using the structured data:

CANDIDATE PROFILE:
- Name: ${resumeData.name}
- Experience: ${resumeData.experienceYears} years
- Current Role: ${resumeData.currentRole}
- Education: ${resumeData.education.degree} in ${resumeData.education.field}
- Technical Skills: ${Object.values(resumeData.technicalSkills).flat().join(', ')}
- Projects: ${resumeData.projects.map((p: { title: string; technologies: string[] }) => `${p.title} (${p.technologies.join(', ')})`).join('; ')}
- Achievements: ${resumeData.achievements.map((a: { description: string }) => a.description).join('; ')}

JOB DETAILS:
- Title: ${jobData.title || 'Not specified'}
- Company: ${jobData.company || 'Not specified'}
- Location: ${jobData.location || 'Not specified'}
- Experience Level: ${jobData.experienceLevel || 'Not specified'}
- Job Type: ${jobData.jobType || 'Not specified'}
- Salary: ${jobData.salary || 'Not specified'}
- Required Skills: ${(jobData.skills || []).join(', ') || 'Not specified'}
- Requirements: ${(jobData.requirements || []).join('; ') || 'Not specified'}
- Responsibilities: ${(jobData.responsibilities || []).join('; ') || 'Not specified'}

FULL JOB CONTENT:
${jobContent.substring(0, 2000)}

Provide a detailed compatibility analysis with precise scores based on:
1. Technical skills overlap (candidate skills vs required skills)
2. Experience level alignment (years and role progression)
3. Education relevance to the role
4. Project experience relevance to responsibilities
5. Overall cultural and role fit

Return specific missing skills, strong matches, and personalized recommendations in JSON format.`;

    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini-2024-07-18',
      messages: [
        {
          role: 'system',
          content: 'You are an expert at analyzing job compatibility using structured data. Provide precise, actionable analysis based on specific requirements and candidate background.'
        },
        {
          role: 'user',
          content: prompt
        }
      ],
      response_format: { type: 'json_object' },
      max_tokens: 1500
    })

    const result = completion.choices[0].message.content
    if (!result) {
      throw new Error('No AI response received')
    }

    const analysis = JSON.parse(result)
    
    console.log('✅ Enhanced job matching successful:', {
      overallMatch: analysis.overallMatch || 85,
      skillsMatch: analysis.skillsMatch || 80,
      missingSkillsCount: analysis.missingSkills?.length || 0,
      strongMatchesCount: analysis.strongMatches?.length || 0
    })

    return {
      overallMatch: analysis.overallMatch || 85,
      skillsMatch: analysis.skillsMatch || 80,
      experienceMatch: analysis.experienceMatch || 85,
      educationMatch: analysis.educationMatch || 90,
      missingSkills: analysis.missingSkills || [],
      strongMatches: analysis.strongMatches || resumeData.technicalSkills.programmingLanguages,
      partialMatches: analysis.partialMatches || [],
      recommendedFocus: analysis.recommendedFocus || ['System Design', 'Technical Skills'],
      personalizedInsights: analysis.personalizedInsights || `Your ${resumeData.experienceYears} years of experience aligns well with this role.`,
      companyFit: analysis.companyFit || 85,
      roleSpecificMatch: analysis.roleSpecificMatch || 80
    }
  } catch (error) {
    console.error('❌ Enhanced job matching failed:', error)
    // Fallback to basic analysis
    return {
      overallMatch: 85,
      skillsMatch: 80,
      experienceMatch: 85,
      educationMatch: 90,
      missingSkills: [],
      strongMatches: resumeData.technicalSkills.programmingLanguages,
      partialMatches: [],
      recommendedFocus: ['Technical Skills', 'Experience'],
      personalizedInsights: `Your background shows strong alignment with this position.`,
      companyFit: 85,
      roleSpecificMatch: 80
    }
  }
}

export async function POST(req: NextRequest) {
  console.log('🚀 === COMPLETE ANALYSIS: Starting ===')
  
  try {
    const body = await req.json();
    console.log('📄 Request received:', {
      hasResumeText: !!body.resumeText,
      resumeTextLength: body.resumeText?.length || 0,
      hasJobDescription: !!body.jobDescription,
      hasJobData: !!body.jobData,
      hasPreProcessedResumeData: !!body.resumeAnalysisData,
      hasPreProcessedJobData: !!body.jobAnalysisData
    })

    // === DEBUG: LOG FULL JOB DATA STRUCTURE ===
    console.log('🔍 === DETAILED JOB DATA DEBUG ===')
    console.log('Full jobData object:', JSON.stringify(body.jobData, null, 2))
    console.log('jobData keys:', body.jobData ? Object.keys(body.jobData) : 'No jobData')
    console.log('jobData.title:', body.jobData?.title)
    console.log('jobData.company:', body.jobData?.company)
    console.log('jobData.role:', body.jobData?.role)
    console.log('jobData.source:', body.jobData?.source)
    console.log('jobData.structuredData:', body.jobData?.structuredData ? 'Present' : 'Missing')
    console.log('jobDescription length:', (body.jobDescription || '').length)
    
    if (!body.resumeText) {
      return Response.json({ error: 'Resume text is required' }, { status: 400 });
    }

    const startTime = Date.now()
    
    // Step 1: Resume Analysis (use pre-processed data if available)
    console.log('📊 === STEP 1: RESUME ANALYSIS ===')
    let resumeData;
    if (body.resumeAnalysisData) {
      console.log('🚀 Using pre-processed resume data')
      resumeData = body.resumeAnalysisData;
    } else {
      console.log('🧠 Processing resume with AI...')
      resumeData = await parseResumeWithEnhancedAI(body.resumeText);
    }
    console.log('✅ Resume analysis complete:', resumeData.name, resumeData.currentRole)

    // Step 2: Enhanced Job Matching with Scraped Data (use pre-processed if available)
    console.log('🎯 === STEP 2: ENHANCED JOB MATCHING ===')
    const jobData = body.jobData || {};
    
    // === DEBUG: LOG JOB DATA AFTER ASSIGNMENT ===
    console.log('🔍 === JOB DATA AFTER ASSIGNMENT ===')
    console.log('jobData after assignment:', JSON.stringify(jobData, null, 2))
    
    // If we have pre-processed job analysis, use it
    if (body.jobAnalysisData) {
      console.log('🚀 Using pre-processed job analysis data')
      // Merge job analysis insights into jobData
      Object.assign(jobData, body.jobAnalysisData);
      console.log('🔍 === JOB DATA AFTER MERGE ===')
      console.log('jobData after merge:', JSON.stringify(jobData, null, 2))
    }
    
    console.log('📊 Using enhanced job data:', {
      hasTitle: !!jobData.title,
      hasCompany: !!jobData.company,
      hasLocation: !!jobData.location,
      hasRequirements: !!(jobData.requirements && jobData.requirements.length > 0),
      hasSkills: !!(jobData.skills && jobData.skills.length > 0),
      contentLength: (jobData.content || body.jobDescription || '').length,
      hasAIInsights: !!jobData.aiInsights,
      actualTitle: jobData.title,
      actualCompany: jobData.company
    })
    
    const matchData = await generateEnhancedJobMatch(resumeData, jobData, body.jobDescription);
    console.log('✅ Enhanced job matching complete:', matchData.overallMatch + '%')
    console.log('🎯 Match details:', {
      skillsMatch: matchData.skillsMatch + '%',
      experienceMatch: matchData.experienceMatch + '%',
      missingSkillsCount: matchData.missingSkills.length,
      strongMatchesCount: matchData.strongMatches.length
    })

    // Step 3: Question Generation (Enhanced)
    console.log('❓ === STEP 3: ENHANCED QUESTION GENERATION ===')
    
    // Convert resumeData to EnhancedResumeData format
    const enhancedResumeData: EnhancedResumeData = {
      name: resumeData.name,
      currentRole: resumeData.currentRole,
      experienceYears: resumeData.experienceYears,
      technicalSkills: resumeData.technicalSkills,
      projects: resumeData.projects,
      education: resumeData.education,
      stats: {
        totalProjects: resumeData.stats.totalProjects,
        totalTechnologies: resumeData.stats.technologiesUsed // Map technologiesUsed to totalTechnologies
      }
    }

    // Create enhanced job context using scraped data
    const jobContext: JobContext = {
      role: jobData.title || jobData.role || 'Software Engineer',
      company: jobData.company || 'Target Company',
      description: jobData.content || body.jobDescription || 'No job description provided',
      level: resumeData.experienceYears <= 2 ? 'junior' : 
             resumeData.experienceYears <= 5 ? 'mid' : 'senior'
    }
    
    console.log('🎯 Enhanced job context created:', {
      role: jobContext.role,
      company: jobContext.company,
      level: jobContext.level,
             hasRichDescription: (jobContext.description || '').length > 100,
      scraped: {
        hasStructuredData: !!(jobData.structuredData),
        hasSkills: !!(jobData.skills && jobData.skills.length > 0),
        hasRequirements: !!(jobData.requirements && jobData.requirements.length > 0)
      }
    })

    // Generate exactly 5 personalized questions per category (15 total)
    const combinedQuestions = await generatePersonalizedQuestionsByCategory(resumeData, jobData, jobContext)
    
    console.log(`✅ Enhanced question generation complete: ${combinedQuestions.length} questions across ${new Set(combinedQuestions.map((q: any) => q.category)).size} categories`)
    console.log(`📊 Question breakdown: Technical: ${combinedQuestions.filter((q: any) => q.category === 'technical').length}, Behavioral: ${combinedQuestions.filter((q: any) => q.category === 'behavioral').length}, System Design: ${combinedQuestions.filter((q: any) => q.category === 'system-design').length}`)
    console.log(`🎯 Role detected: ${jobContext.role} (${jobContext.level} level)`)
    console.log(`💡 Questions personalized with: Resume-specific details and ${resumeData.technicalSkills.programmingLanguages.slice(0, 2).join(', ')} experience`)

    // Step 4: Final Analysis
    console.log('📈 === STEP 4: FINAL ANALYSIS ===')
    const finalAnalysis = {
      overallMatch: matchData.overallMatch,
      skillsBreakdown: {
        technical: matchData.skillsMatch,
        experience: matchData.experienceMatch,
        education: matchData.educationMatch,
        culture: 85
      },
      salaryInsights: {
        range: { min: '95k', max: '135k' },
        median: '115k',
        percentile: '75th',
        tip: `Based on your ${resumeData.experienceYears} years of experience and ${resumeData.education.degree} background.`
      },
      interviewTips: [
        `Highlight your experience with ${resumeData.technicalSkills.programmingLanguages.slice(0, 2).join(' and ')}.`,
        `Prepare examples from your ${resumeData.stats.totalProjects} projects.`,
        `Emphasize your ${resumeData.experienceDescription}.`
      ]
    };
    console.log('✅ Final analysis complete')

    // Step 5: Comprehensive Guide
    console.log('📚 === STEP 5: COMPREHENSIVE GUIDE ===')
    const comprehensiveGuide = {
      title: `${jobData.title || jobData.role || 'Software Engineer'} Interview Guide - ${jobData.company || 'Target Company'}`,
      personalizedFor: resumeData.name,
      targetRole: jobData.title || jobData.role || 'Software Engineer',
      targetCompany: jobData.company || 'Target Company',
      location: jobData.location || 'Location TBD',
      jobType: jobData.jobType || 'Full-time',
      experienceLevel: jobData.experienceLevel || (resumeData.experienceYears <= 2 ? 'Entry Level' : resumeData.experienceYears <= 5 ? 'Mid Level' : 'Senior Level'),
      matchScore: `${matchData.overallMatch}%`,
      
      introduction: {
        roleOverview: `This ${jobData.title || jobData.role || 'role'} position at ${jobData.company || 'the company'}${jobData.location ? ` in ${jobData.location}` : ''} aligns well with your ${resumeData.experienceDescription}. With ${resumeData.experienceYears} years of experience in ${resumeData.technicalSkills.programmingLanguages.slice(0, 2).join(' and ')}, you bring valuable technical expertise to this ${jobData.experienceLevel || jobData.jobType || 'opportunity'}.`,
        culture: `Based on the role requirements${jobData.company ? ` at ${jobData.company}` : ''}, this position values innovation, collaboration, and technical excellence. ${jobData.company ? `${jobData.company}` : 'Companies'} seeking ${jobData.title || jobData.role || 'Software Engineers'} typically prioritize continuous learning, problem-solving skills, and the ability to work effectively in cross-functional teams. Your background in ${resumeData.technicalSkills.frameworks.slice(0, 2).join(' and ')} demonstrates alignment with modern development practices.`,
        whyThisRole: `Your background in ${resumeData.technicalSkills.programmingLanguages.join(', ')} makes you a strong candidate for this ${jobData.title || 'role'}. ${jobData.requirements && jobData.requirements.length > 0 ? `The position requires skills in ${jobData.requirements.slice(0, 3).join(', ')}, which aligns well with your expertise. ` : ''}The role offers opportunities to leverage your ${resumeData.experienceDescription} while growing in areas like ${matchData.recommendedFocus.join(' and ')}. With your ${resumeData.education.degree} background and ${resumeData.stats.totalProjects} project portfolio, you're well-positioned to contribute immediately.`,
        keyStrengths: resumeData.technicalSkills.programmingLanguages.slice(0, 3),
        salaryRange: jobData.salary || 'Competitive compensation package',
        remotePolicy: jobData.location?.toLowerCase().includes('remote') ? 'Remote work available' : jobData.location ? `Based in ${jobData.location}` : 'Location details to be confirmed'
      },
      
      interviewProcess: {
        diagram: `The interview process typically follows these stages, designed to assess both technical skills and cultural fit:`,
        stages: [
          { name: 'Phone Screen', duration: '30 min', description: 'Technical discussion and background review with a hiring manager or technical lead' },
          { name: 'Technical Interview', duration: '60 min', description: 'Coding challenges and algorithm questions relevant to the role' },
          { name: 'System Design', duration: '45 min', description: 'Architecture and design discussion for larger scale problems' },
          { name: 'Behavioral Interview', duration: '45 min', description: 'Culture fit, leadership scenarios, and team collaboration' },
          { name: 'Final Round', duration: '30 min', description: 'Meet the team, ask questions, and final evaluation' }
        ],
        levelDifferences: (() => {
          // Determine the candidate's level based on experience
          const candidateLevel = resumeData.experienceYears <= 2 ? 'entry' : 
                                 resumeData.experienceYears <= 5 ? 'mid' : 'senior'
          
          // Determine the job's target level from the job posting
          const jobLevelString = jobData.experienceLevel || 'mid' // Default to mid if not specified
          const targetLevel = jobLevelString.toLowerCase().includes('senior') ? 'senior' :
                             jobLevelString.toLowerCase().includes('entry') || jobLevelString.toLowerCase().includes('junior') ? 'entry' : 'mid'

          // Generate level-specific description based on the job's target level
          let levelDescription = ''
          if (targetLevel === 'entry') {
            levelDescription = '**Entry Level (0-2 years):** Focus on coding fundamentals, basic algorithms, and eagerness to learn. System design may be simplified or skipped. Emphasis on potential, learning ability, and foundational programming concepts.'
          } else if (targetLevel === 'senior') {
            levelDescription = '**Senior Level (5+ years):** Strong system design skills, mentorship capabilities, and strategic thinking. Expected to handle architecture decisions, team leadership scenarios, and complex problem-solving with minimal guidance.'
          } else {
            levelDescription = '**Mid Level (3-5 years):** Expected to handle complex coding problems, some system design, and demonstrate project leadership experience. Should show independent problem-solving and ability to guide junior developers.'
          }

          // Add personalized advice based on candidate vs job level alignment
          let experienceNote = ''
          if (candidateLevel === targetLevel) {
            experienceNote = ` Your ${resumeData.experienceYears} years of experience aligns well with this ${targetLevel}-level role.`
          } else if (candidateLevel === 'entry' && targetLevel === 'mid') {
            experienceNote = ` Your ${resumeData.experienceYears} years places you in the entry-level category, so focus on demonstrating growth potential, strong fundamentals, and eagerness to take on mid-level responsibilities.`
          } else if (candidateLevel === 'mid' && targetLevel === 'senior') {
            experienceNote = ` Your ${resumeData.experienceYears} years places you in the mid-level category, so emphasize leadership experiences, system design thinking, and mentoring capabilities to match senior expectations.`
          } else if (candidateLevel === 'senior' && targetLevel === 'mid') {
            experienceNote = ` Your ${resumeData.experienceYears} years gives you an advantage for this mid-level role - highlight your mentoring abilities and strategic contributions while showing you can work effectively at this level.`
          } else if (candidateLevel === 'entry' && targetLevel === 'senior') {
            experienceNote = ` Your ${resumeData.experienceYears} years places you in entry-level, which is a significant gap for a senior role. Focus on showcasing exceptional projects, rapid learning ability, and any leadership or mentoring experiences.`
          } else if (candidateLevel === 'senior' && targetLevel === 'entry') {
            experienceNote = ` Your ${resumeData.experienceYears} years of experience significantly exceeds entry-level requirements. Highlight your ability to mentor, lead projects, and contribute strategic value while showing enthusiasm for the role.`
          }

          return levelDescription + experienceNote
        })()
      },
      
      questions: {
        technical: combinedQuestions.filter((q: any) => q.category === 'technical'),
        behavioral: combinedQuestions.filter((q: any) => q.category === 'behavioral'),
        caseStudy: combinedQuestions.filter((q: any) => q.category === 'system-design'), // UI expects caseStudy, not systemDesign
        systemDesign: combinedQuestions.filter((q: any) => q.category === 'system-design') // Keep both for compatibility
      },
      
      preparation: {
        tips: [
          {
            title: "Technical Preparation",
            description: `Focus on ${resumeData.technicalSkills.programmingLanguages.join(', ')} fundamentals and practice coding problems on LeetCode and HackerRank. Review data structures and algorithms relevant to your experience level.`
          },
          {
            title: "System Design Study",
            description: "Study scalable system architectures, database design, and microservices patterns. Practice explaining complex systems clearly and concisely."
          },
          {
            title: "Behavioral Stories",
            description: `Prepare STAR method examples from your ${resumeData.stats.totalProjects} projects. Focus on leadership, problem-solving, and collaboration experiences.`
          },
          {
            title: "Company Research",
            description: `Research the company's tech stack, recent news, and engineering culture. Understand how your ${resumeData.experienceDescription} aligns with their needs.`
          }
        ],
        studyPlan: `**Week 1-2:** Review ${resumeData.technicalSkills.programmingLanguages.slice(0, 2).join(' and ')} fundamentals and practice 2-3 coding problems daily. **Week 3:** Focus on system design concepts and practice whiteboarding. **Week 4:** Mock interviews and behavioral question practice. **Final Week:** Company-specific research and final review of your ${resumeData.stats.totalProjects} key projects.`,
        mockInterviews: `Schedule practice sessions with peers or use platforms like Pramp, InterviewBuddy, or LeetCode Mock Interview. Focus on explaining your thought process clearly and handling follow-up questions. Practice presenting your ${resumeData.projects.slice(0, 2).map((p: { title: string }) => p.title).join(' and ')} projects concisely.`,
        technicalPrep: `Focus on ${resumeData.technicalSkills.programmingLanguages.join(', ')} and system design concepts relevant to ${jobData.role || 'software development'}.`,
        behavioralPrep: `Prepare STAR method examples from your ${resumeData.stats.totalProjects} projects, emphasizing leadership, problem-solving, and collaboration.`,
        projectExamples: resumeData.projects.map((p: { title: string; technologies: string[] }) => ({
          title: p.title,
          technologies: p.technologies,
          highlights: [`Built with ${p.technologies.join(', ')}`, `Demonstrates expertise in ${p.technologies.slice(0, 2).join(' and ')}`, `Showcases problem-solving and technical implementation skills`]
        }))
      },
      
      talkingPoints: [
        `${resumeData.experienceYears} years of hands-on experience in ${resumeData.technicalSkills.programmingLanguages.slice(0, 2).join(' and ')}`,
        `Expertise in modern technologies including ${resumeData.technicalSkills.frameworks.slice(0, 2).join(', ')}`,
        `${resumeData.education.degree} in ${resumeData.education.field} providing strong foundation`,
        `Proven track record with ${resumeData.stats.totalProjects} successful projects demonstrating end-to-end delivery`,
        `Strong problem-solving skills evidenced by diverse project portfolio`
      ],
      
      faqs: {
        salary: jobData.salary || jobData.salaryRange || `Based on your ${resumeData.experienceYears} years of experience and ${resumeData.education.degree} background, you can expect a salary range of $${resumeData.experienceYears <= 2 ? '75,000 - 105,000' : resumeData.experienceYears <= 5 ? '95,000 - 135,000' : '120,000 - 180,000'}. Your expertise in ${resumeData.technicalSkills.programmingLanguages.slice(0, 2).join(' and ')} puts you in a competitive position. Location, company size, and specific role requirements will influence the final offer. Consider the total compensation package including equity, benefits, and growth opportunities.`,
        experiences: 'Research interview experiences on Glassdoor, Blind, and LeetCode Discuss for company-specific insights. Look for recent posts about the specific role and team to understand current interview trends and expectations. Pay attention to the interview format (virtual vs. in-person) and any unique aspects of their process.',
        jobPostings: 'Check LinkedIn, Indeed, AngelList, and the company career page for similar roles. Pay attention to required vs. preferred qualifications to better understand what skills to emphasize. Look for patterns in job descriptions to identify the most valued technologies and soft skills.'
      },
      
      conclusion: {
        summary: `You are well-positioned for this ${jobData.role || 'role'} with your ${resumeData.experienceYears} years of experience and strong technical background in ${resumeData.technicalSkills.programmingLanguages.slice(0, 2).join(' and ')}. Your ${resumeData.education.degree} education and hands-on experience with ${resumeData.stats.totalProjects} projects demonstrate both theoretical knowledge and practical application. Focus your preparation on highlighting your technical expertise, preparing compelling project examples, and demonstrating your ability to grow with the role. The ${matchData.overallMatch}% compatibility score indicates strong alignment with the position requirements.`,
        resources: {
          successStory: { 
            title: 'Interview Success Stories', 
            link: 'https://www.glassdoor.com/Interview/index.htm' 
          },
          questionList: { 
            title: 'Technical Interview Questions', 
            link: 'https://leetcode.com/discuss/interview-question' 
          },
          learningPath: { 
            title: 'System Design Interview Prep', 
            link: 'https://github.com/donnemartin/system-design-primer' 
          }
        }
      },

      // Add metadata for better component compatibility
      metadata: {
        generatedAt: new Date().toISOString(),
        personalizedFor: resumeData.name,
        targetRole: jobData.role || 'Software Engineer',
        targetCompany: jobData.company || 'Target Company'
      }
    };

    // Step 6: Premium Content Enhancement
    console.log('🎯 === STEP 6: PREMIUM CONTENT ENHANCEMENT ===')
    const premiumContent = generatePremiumContent(enhancedResumeData, jobContext, combinedQuestions);
    console.log('✅ Premium content enhancement complete: preparation timelines, company research, STAR method guide')
    console.log(`📊 Premium features: ${Object.keys(premiumContent.timelineOptions).length} timeline options, ${premiumContent.companyResearch.researchAreas.length} research areas, ${Object.keys(premiumContent.starMethodGuide.storyBank).length} STAR story categories`)
    
    // Step 7: Premium Coaching Features
    console.log('🎖️ === STEP 7: PREMIUM COACHING FEATURES ===')
    const premiumCoaching = generatePremiumCoaching(enhancedResumeData, jobContext, resumeData.experienceYears <= 2 ? 'junior' : resumeData.experienceYears <= 5 ? 'mid' : 'senior');
    console.log('✅ Premium coaching complete: smart questions, competitive advantage, personal branding, advanced strategies')
    console.log(`🎯 Coaching features: ${premiumCoaching.smartQuestions.strategicQuestions.length} strategic question categories, ${premiumCoaching.competitiveAdvantage.uniqueValueProposition.coreStrengths.length} core strengths, ${premiumCoaching.personalBranding.brandArchetype.primaryArchetype} brand archetype`)
    console.log('🎉 === COMPREHENSIVE GUIDE COMPLETE ===');

    const endTime = Date.now()
    const totalTime = endTime - startTime

    console.log(`🎉 === ANALYSIS COMPLETE in ${totalTime}ms ===`)

    return Response.json({
      success: true,
      processingTime: totalTime,
      message: 'Complete analysis finished successfully',
      
      results: {
        resumeData,
        matchData,
        questions: combinedQuestions,
        finalAnalysis,
        comprehensiveGuide,
        premiumContent, // Add premium content to response
        premiumCoaching, // Add premium coaching to response
        
        summary: {
          candidateName: resumeData.name,
          targetRole: jobData.role || 'Software Engineer',
          overallMatch: matchData.overallMatch,
          questionsGenerated: combinedQuestions.length,
          keyStrengths: resumeData.technicalSkills.programmingLanguages.slice(0, 3),
          completedAt: new Date().toISOString(),
          processingSteps: 7 // Updated to reflect new step count
        }
      }
    });

  } catch (error) {
    console.error('❌ === COMPLETE ANALYSIS ERROR ===', error)
    return Response.json({
      error: 'Analysis failed',
      details: (error as any)?.message || 'Unknown error',
      timestamp: new Date().toISOString()
    }, { status: 500 });
  }
} 
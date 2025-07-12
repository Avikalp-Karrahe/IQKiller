// TypeScript fix version - Thu Jul 10 10:35:30 PDT 2025
// Premium Coaching Engine for Elite Interview Preparation
// TypeScript interfaces for premium coaching
interface EnhancedResumeData {
  name: string
  currentRole: string
  experienceYears: number
  technicalSkills: {
    programmingLanguages: string[]
    frameworks: string[]
    databases: string[]
    tools: string[]
  }
  projects: Array<{
    title: string
    technologies: string[]
    description?: string
  }>
  workExperience?: Array<{
    company: string
    role: string
    duration?: string
  }>
  education: {
    degree: string
    field: string
    school?: string
  }
  stats: {
    totalProjects: number
    totalTechnologies: number
  }
}

interface JobContext {
  role?: string
  company?: string
  description?: string
  level?: 'junior' | 'mid' | 'senior' | 'staff'
}

export interface PremiumCoachingFeatures {
  smartQuestions: SmartQuestionFramework
  competitiveAdvantage: CompetitiveAdvantagePositioning
  personalBranding: PersonalBrandingGuidance
  advancedStrategies: AdvancedPreparationStrategies
  executivePresence: ExecutivePresenceCoaching
}

export interface SmartQuestionFramework {
  strategicQuestions: Array<{
    category: string
    purpose: string
    questions: string[]
    timing: string
    followUp: string[]
    redFlags: string[]
  }>
  roleSpecificQuestions: Array<{
    role: string
    questions: string[]
    businessImpact: string
    decisionFactors: string[]
  }>
  companyIntelQuestions: Array<{
    area: string
    questions: string[]
    insights: string[]
    positioning: string
  }>
  negotiationQuestions: Array<{
    topic: string
    questions: string[]
    strategy: string
    timing: string
  }>
}

export interface CompetitiveAdvantagePositioning {
  uniqueValueProposition: {
    coreStrengths: string[]
    differentiators: string[]
    marketPosition: string
    valueStatement: string
  }
  competitorAnalysis: {
    typicalCandidates: string[]
    yourAdvantages: string[]
    addressingWeaknesses: string[]
    positioning: string[]
  }
  marketingMessage: {
    elevatorPitch: string
    keyTalkingPoints: string[]
    evidencePoints: string[]
    storyArc: string
  }
  strategicPositioning: {
    roleAlignment: string[]
    companyFit: string[]
    futureValue: string[]
    riskMitigation: string[]
  }
}

export interface PersonalBrandingGuidance {
  brandArchetype: {
    primaryArchetype: string
    characteristics: string[]
    messagingTone: string
    visualIdentity: string[]
  }
  digitalPresence: {
    linkedinOptimization: string[]
    portfolioEnhancement: string[]
    thoughtLeadership: string[]
    networkingStrategy: string[]
  }
  storytellingFramework: {
    originStory: string
    transformationJourney: string[]
    futureBio: string
    signatureStories: string[]
  }
  executiveCommunication: {
    languagePatterns: string[]
    presenceBuilders: string[]
    influenceFactors: string[]
    credibilityMarkers: string[]
  }
}

export interface AdvancedPreparationStrategies {
  psychologicalPreparation: {
    mentalModels: string[]
    biasAwareness: string[]
    confidenceHacks: string[]
    stressInoculation: string[]
  }
  negotiationPreparation: {
    salaryResearch: SalaryResearchGuide
    negotiationTactics: string[]
    leveragePoints: string[]
    walkAwayPower: string[]
  }
  strategicNetworking: {
    preInterviewOutreach: string[]
    duringInterviewConnections: string[]
    postInterviewFollowUp: string[]
    longTermRelationships: string[]
  }
  performanceOptimization: {
    peakPerformanceRoutines: string[]
    energyManagement: string[]
    focusEnhancement: string[]
    recoveryStrategies: string[]
  }
}

export interface SalaryResearchGuide {
  marketRates: {
    baseRange: string
    bonusStructure: string
    equityExpectations: string
    totalCompRange: string
  }
  negotiationStrategy: {
    anchoring: string
    bundling: string
    timing: string
    alternatives: string[]
  }
  leverageFactors: string[]
  riskFactors: string[]
}

export interface ExecutivePresenceCoaching {
  communicationMastery: {
    executiveLanguage: string[]
    powerPhrases: string[]
    voiceModulation: string[]
    pauseUsage: string[]
  }
  bodyLanguage: {
    powerPoses: string[]
    gestureControl: string[]
    eyeContact: string[]
    spatialAwareness: string[]
  }
  mentalFramework: {
    executiveMindset: string[]
    decisionMaking: string[]
    riskAssessment: string[]
    strategicThinking: string[]
  }
  presenceIndicators: {
    authorityMarkers: string[]
    competenceSignals: string[]
    trustBuilders: string[]
    influence: string[]
  }
}

export function generatePremiumCoaching(
  resumeData: EnhancedResumeData,
  jobContext: JobContext,
  experienceLevel: string
): PremiumCoachingFeatures {
  
  const roleCategory = getRoleCategory(jobContext.role || resumeData.currentRole)
  const seniorityLevel = resumeData.experienceYears >= 5 ? 'senior' : 
                        resumeData.experienceYears >= 3 ? 'mid' : 'junior'
  
  return {
    smartQuestions: generateSmartQuestions(jobContext, roleCategory, seniorityLevel),
    competitiveAdvantage: generateCompetitiveAdvantage(resumeData, jobContext, roleCategory),
    personalBranding: generatePersonalBranding(resumeData, jobContext, seniorityLevel),
    advancedStrategies: generateAdvancedStrategies(resumeData, jobContext, seniorityLevel),
    executivePresence: generateExecutivePresence(resumeData, seniorityLevel)
  }
}

function generateSmartQuestions(
  jobContext: JobContext,
  roleCategory: string,
  seniorityLevel: string
): SmartQuestionFramework {
  const companyName = jobContext.company || 'the company'
  
  return {
    strategicQuestions: [
      {
        category: 'Strategic Direction',
        purpose: 'Understand company vision and your role in achieving it',
        questions: [
          `What are ${companyName}'s biggest strategic priorities for the next 2-3 years?`,
          'How does this role contribute to those strategic objectives?',
          'What would success in this position look like in 12 months?',
          'What are the biggest challenges the team is facing right now?'
        ],
        timing: 'Mid to late in interview',
        followUp: [
          'How do you measure progress on those priorities?',
          'What resources would be available to help achieve these goals?',
          'How does leadership view the importance of this role?'
        ],
        redFlags: [
          'Vague answers about company direction',
          'No clear success metrics',
          'Lack of leadership support for the role'
        ]
      },
      {
        category: 'Team Dynamics & Culture',
        purpose: 'Assess team fit and collaboration opportunities',
        questions: [
          'Can you tell me about the team I\'d be working with?',
          'How does this team collaborate with other departments?',
          'What\'s the management style like here?',
          'How do you handle conflicts or disagreements within the team?'
        ],
        timing: 'Early to mid interview',
        followUp: [
          'What makes someone successful on this team?',
          'How do you celebrate wins and learn from failures?',
          'What professional development opportunities are available?'
        ],
        redFlags: [
          'High turnover mentioned',
          'Unclear reporting structure',
          'Limited development opportunities'
        ]
      },
      {
        category: 'Growth & Innovation',
        purpose: 'Show forward-thinking and growth mindset',
        questions: [
          'How is the company staying ahead of industry trends?',
          'What new technologies or methodologies is the team exploring?',
          'How does the company foster innovation?',
          'What opportunities are there for professional growth in this role?'
        ],
        timing: 'Mid interview when discussing role details',
        followUp: [
          'How do you encourage experimentation and learning?',
          'What\'s the typical career progression for this role?',
          'How does the company invest in employee development?'
        ],
        redFlags: [
          'No innovation initiatives',
          'Limited growth opportunities',
          'Resistance to change or new ideas'
        ]
      }
    ],

    roleSpecificQuestions: generateRoleSpecificQuestions(roleCategory, seniorityLevel, companyName),

    companyIntelQuestions: [
      {
        area: 'Market Position',
        questions: [
          `How does ${companyName} differentiate itself from competitors?`,
          'What market opportunities is the company pursuing?',
          'How do you see the competitive landscape evolving?'
        ],
        insights: [
          'Shows business acumen and strategic thinking',
          'Demonstrates research and preparation',
          'Indicates long-term perspective'
        ],
        positioning: 'Position yourself as someone who thinks strategically about business impact'
      },
      {
        area: 'Technology & Innovation',
        questions: [
          'What technology investments is the company making?',
          'How do you balance innovation with operational stability?',
          'What emerging technologies are you most excited about?'
        ],
        insights: [
          'Shows technical curiosity and forward-thinking',
          'Demonstrates understanding of tech strategy',
          'Indicates ability to balance innovation with execution'
        ],
        positioning: 'Position yourself as someone who can drive technological advancement'
      }
    ],

    negotiationQuestions: [
      {
        topic: 'Compensation Structure',
        questions: [
          'How is compensation structured for this role?',
          'What does the performance review and promotion process look like?',
          'Are there opportunities for equity participation?'
        ],
        strategy: 'Gather information before making any negotiations',
        timing: 'After initial fit is established, before offer'
      },
      {
        topic: 'Role Flexibility',
        questions: [
          'Is there flexibility in how this role evolves over time?',
          'What opportunities are there to take on additional responsibilities?',
          'How does the company support work-life balance?'
        ],
        strategy: 'Understand scope for growth and personal needs',
        timing: 'Late in process when mutual interest is clear'
      }
    ]
  }
}

function generateRoleSpecificQuestions(
  roleCategory: string,
  seniorityLevel: string,
  companyName: string
): Array<{ role: string, questions: string[], businessImpact: string, decisionFactors: string[] }> {
  
  const baseQuestions = {
    'data-scientist': {
      role: 'Data Scientist',
      questions: [
        'What data infrastructure and tools does the team currently use?',
        'How does the company measure the ROI of data science initiatives?',
        'What are the biggest data challenges the organization is facing?',
        'How do data science insights get translated into business decisions?',
        'What opportunities are there to work on cutting-edge ML/AI projects?'
      ],
      businessImpact: 'Demonstrates understanding of data science business value and technical infrastructure',
      decisionFactors: [
        'Quality of data infrastructure',
        'Leadership support for data-driven decisions',
        'Opportunities for impact and innovation',
        'Team technical sophistication'
      ]
    },
    'software-engineer': {
      role: 'Software Engineer',
      questions: [
        'What does the software development lifecycle look like here?',
        'How do you handle technical debt and code quality?',
        'What opportunities are there to influence architecture decisions?',
        'How does the team stay current with new technologies?',
        'What\'s the deployment and DevOps strategy?'
      ],
      businessImpact: 'Shows technical leadership and systematic thinking about software engineering',
      decisionFactors: [
        'Code quality standards',
        'Technical growth opportunities',
        'Development process maturity',
        'Innovation and learning culture'
      ]
    },
    'product-manager': {
      role: 'Product Manager',
      questions: [
        'How does product strategy align with overall business objectives?',
        'What does the product discovery and validation process look like?',
        'How do you measure product success and user satisfaction?',
        'What\'s the relationship between product, engineering, and design?',
        'How does customer feedback influence product decisions?'
      ],
      businessImpact: 'Demonstrates product thinking and customer-centric approach',
      decisionFactors: [
        'Product strategy clarity',
        'Customer feedback integration',
        'Cross-functional collaboration',
        'Metrics and measurement approach'
      ]
    }
  }

  const defaultQuestions = {
    role: 'Professional',
    questions: [
      'What are the key success metrics for this role?',
      'How does this position contribute to overall business objectives?',
      'What opportunities are there for cross-functional collaboration?',
      'How does the company invest in professional development?',
      'What\'s the typical career progression from this role?'
    ],
    businessImpact: 'Shows business acumen and growth mindset',
    decisionFactors: [
      'Clear success metrics',
      'Growth opportunities',
      'Company investment in people',
      'Role impact and visibility'
    ]
  }

  return [baseQuestions[roleCategory as keyof typeof baseQuestions] || defaultQuestions]
}

function generateCompetitiveAdvantage(
  resumeData: EnhancedResumeData,
  jobContext: JobContext,
  roleCategory: string
): CompetitiveAdvantagePositioning {
  
  const primarySkills = resumeData.technicalSkills.programmingLanguages.slice(0, 3)
  const experienceYears = resumeData.experienceYears
  
  return {
    uniqueValueProposition: {
      coreStrengths: [
        `${experienceYears} years of proven experience in ${primarySkills.join(', ')}`,
        `${resumeData.education.degree} background providing strong analytical foundation`,
        `Track record of ${resumeData.stats.totalProjects} successful projects demonstrating execution ability`,
        `Expertise in modern technologies including ${resumeData.technicalSkills.frameworks.slice(0, 2).join(', ')}`
      ],
      differentiators: [
        'Combination of technical depth and business understanding',
        'Strong track record of project delivery and execution',
        'Continuous learning mindset evidenced by diverse technology stack',
        'Cross-functional collaboration experience'
      ],
      marketPosition: `Experienced ${resumeData.currentRole} with strong technical skills and proven delivery track record`,
      valueStatement: `I bring ${experienceYears} years of hands-on experience in ${primarySkills.join(' and ')}, with a proven ability to deliver complex projects from conception to completion. My ${resumeData.education.degree} background combined with practical experience in ${resumeData.stats.totalProjects} projects positions me to drive immediate impact while contributing to long-term strategic objectives.`
    },

    competitorAnalysis: {
      typicalCandidates: [
        'Recent graduates with strong academic background but limited practical experience',
        'Senior professionals with deep expertise but potentially less adaptability',
        'Career changers with adjacent skills but lacking direct industry experience',
        'Specialists with narrow focus but limited breadth'
      ],
      yourAdvantages: [
        `Perfect balance of ${experienceYears} years experience with continued learning and adaptation`,
        'Proven project delivery track record with measurable business impact',
        'Broad technology stack demonstrating versatility and quick learning',
        'Strong educational foundation combined with practical application'
      ],
      addressingWeaknesses: [
        'If lacking specific technology: "I have demonstrated ability to quickly master new technologies, as evidenced by my diverse tech stack"',
        'If lacking industry experience: "My transferable skills and proven learning ability will enable rapid domain knowledge acquisition"',
        'If lacking seniority: "My hands-on experience and project delivery track record demonstrate readiness for increased responsibility"'
      ],
      positioning: [
        'Position as the "safe choice" - proven delivery with growth potential',
        'Emphasize adaptability and continuous learning over just current skills',
        'Highlight unique combination of technical and business understanding',
        'Demonstrate cultural fit through collaboration examples'
      ]
    },

    marketingMessage: {
      elevatorPitch: `I'm a ${resumeData.currentRole} with ${experienceYears} years of experience building scalable solutions using ${primarySkills.slice(0, 2).join(' and ')}. I've successfully delivered ${resumeData.stats.totalProjects} projects that have driven measurable business impact, and I'm passionate about leveraging technology to solve complex problems. What excites me most about this role is the opportunity to apply my experience in ${primarySkills[0]} to help ${jobContext.company || 'your company'} achieve its strategic objectives.`,
      keyTalkingPoints: [
        `${experienceYears} years of hands-on experience with proven results`,
        `Expertise in ${primarySkills.join(', ')} with ${resumeData.stats.totalProjects} successful project deliveries`,
        `Strong educational foundation (${resumeData.education.degree}) combined with practical application`,
        'Demonstrated ability to work cross-functionally and deliver business value',
        'Continuous learner with adaptability to new technologies and challenges'
      ],
      evidencePoints: [
        `Successfully delivered ${resumeData.stats.totalProjects} projects using ${primarySkills.join(', ')}`,
        `${resumeData.education.degree} education providing analytical and problem-solving foundation`,
        `Proficiency in modern technology stack including ${resumeData.technicalSkills.frameworks.join(', ')}`,
        'Track record of adapting to new technologies and methodologies'
      ],
      storyArc: 'Started with strong technical foundation → Applied skills in real-world projects → Delivered measurable business impact → Ready for next level of responsibility and challenge'
    },

    strategicPositioning: {
      roleAlignment: [
        'Technical skills directly match role requirements',
        'Experience level appropriate for role responsibilities',
        'Project delivery experience aligns with role expectations',
        'Growth trajectory matches role development opportunities'
      ],
      companyFit: [
        'Values alignment with company culture and mission',
        'Technical approach compatible with company methodologies',
        'Collaboration style fits with team dynamics',
        'Career goals align with company growth opportunities'
      ],
      futureValue: [
        'Potential to grow into technical leadership roles',
        'Ability to mentor junior team members',
        'Capacity to drive innovation and process improvements',
        'Long-term commitment to company and industry'
      ],
      riskMitigation: [
        'Proven delivery track record reduces execution risk',
        'Broad technology experience reduces technical risk',
        'Strong learning ability reduces adaptation risk',
        'Good cultural fit reduces team integration risk'
      ]
    }
  }
}

function generatePersonalBranding(
  resumeData: EnhancedResumeData,
  jobContext: JobContext,
  seniorityLevel: string
): PersonalBrandingGuidance {
  
  const primaryArchetype = determineArchetype(resumeData, seniorityLevel)
  
  return {
    brandArchetype: {
      primaryArchetype,
      characteristics: getArchetypeCharacteristics(primaryArchetype),
      messagingTone: getMessagingTone(primaryArchetype),
      visualIdentity: getVisualIdentity(primaryArchetype)
    },

    digitalPresence: {
      linkedinOptimization: [
        `Headline: "${resumeData.currentRole} | ${resumeData.technicalSkills.programmingLanguages.slice(0, 2).join(' & ')} Expert | ${resumeData.stats.totalProjects}+ Projects Delivered"`,
        `Summary: Lead with your unique value proposition and quantified achievements`,
        'Skills: Prioritize top 3-5 skills relevant to target roles',
        'Experience: Use action verbs and quantify impact where possible',
        'Recommendations: Seek recommendations that highlight your key strengths',
        'Activity: Share insights and engage with industry content regularly'
      ],
      portfolioEnhancement: [
        'Showcase your top 3 projects with clear business impact',
        'Include technical details for credibility with technical reviewers',
        'Add before/after metrics to demonstrate value creation',
        'Include testimonials or feedback from stakeholders',
        'Create case studies showing your problem-solving approach'
      ],
      thoughtLeadership: [
        `Write about trends in ${resumeData.technicalSkills.programmingLanguages[0]} development`,
        'Share insights from your project experiences',
        'Comment thoughtfully on industry posts and discussions',
        'Participate in relevant online communities and forums',
        'Speak at meetups or conferences about your expertise'
      ],
      networkingStrategy: [
        'Connect with industry professionals in your target companies',
        'Engage with content from thought leaders in your field',
        'Join professional groups related to your expertise',
        'Attend virtual and in-person industry events',
        'Offer value before asking for anything in return'
      ]
    },

    storytellingFramework: {
      originStory: `Started my journey in technology with a ${resumeData.education.degree}, discovering a passion for ${resumeData.technicalSkills.programmingLanguages[0]} and problem-solving. What began as academic curiosity evolved into a mission to build solutions that create real business value.`,
      transformationJourney: [
        `From student to practitioner: Applied academic knowledge to real-world challenges`,
        `From individual contributor to collaborator: Learned to work effectively in cross-functional teams`,
        `From task executor to solution architect: Developed ability to see big picture and design comprehensive solutions`,
        `From technology user to technology evaluator: Gained expertise in choosing right tools for specific problems`
      ],
      futureBio: `Aspiring to become a technical leader who bridges the gap between complex technology and business value, with a focus on ${resumeData.technicalSkills.programmingLanguages[0]} innovation and team development.`,
      signatureStories: [
        'The project that taught me the importance of stakeholder communication',
        'How I solved a critical technical challenge under tight deadline pressure',
        'The time I had to learn a new technology quickly to meet project requirements',
        'A collaboration that taught me the value of diverse perspectives'
      ]
    },

    executiveCommunication: {
      languagePatterns: [
        'Use "We" when discussing team achievements, "I" when discussing personal contributions',
        'Frame technical decisions in terms of business impact',
        'Use specific metrics and data points to support statements',
        'Avoid jargon unless audience is technical'
      ],
      presenceBuilders: [
        'Speak with conviction while remaining open to feedback',
        'Use pauses effectively to emphasize important points',
        'Maintain eye contact to build trust and connection',
        'Use gestures to support and enhance your message'
      ],
      influenceFactors: [
        'Build credibility through demonstrated expertise',
        'Create connection through shared values and experiences',
        'Use logic and data to support recommendations',
        'Show empathy and understanding of others\' perspectives'
      ],
      credibilityMarkers: [
        'Reference specific project outcomes and metrics',
        'Mention recognition or positive feedback received',
        'Cite industry best practices and standards',
        'Demonstrate continuous learning and adaptation'
      ]
    }
  }
}

function generateAdvancedStrategies(
  resumeData: EnhancedResumeData,
  jobContext: JobContext,
  seniorityLevel: string
): AdvancedPreparationStrategies {
  
  return {
    psychologicalPreparation: {
      mentalModels: [
        'Growth Mindset: View challenges as learning opportunities',
        'Abundance Mindset: Believe there are many good opportunities available',
        'Contribution Mindset: Focus on how you can add value, not just what you can get',
        'Long-term Perspective: Think beyond just getting the job to building a career'
      ],
      biasAwareness: [
        'Confirmation Bias: Seek information that challenges your assumptions',
        'Anchoring Bias: Don\'t let first impressions overly influence your judgment',
        'Halo Effect: Evaluate all aspects of the opportunity, not just the exciting parts',
        'Availability Bias: Don\'t overweight recent or memorable experiences'
      ],
      confidenceHacks: [
        'Power Pose for 2 minutes before the interview',
        'Visualize successful interview scenarios',
        'Review your accomplishments and positive feedback',
        'Practice positive self-talk and affirmations'
      ],
      stressInoculation: [
        'Practice answering difficult questions under time pressure',
        'Do mock interviews in stressful conditions',
        'Use breathing techniques to manage anxiety',
        'Develop contingency plans for unexpected scenarios'
      ]
    },

    negotiationPreparation: {
      salaryResearch: generateSalaryResearch(resumeData, jobContext, seniorityLevel),
      negotiationTactics: [
        'Anchor high but remain within reasonable market range',
        'Bundle compensation elements (base, bonus, equity, benefits)',
        'Use competing offers as leverage (if you have them)',
        'Focus on mutual value creation, not just taking'
      ],
      leveragePoints: [
        `${resumeData.experienceYears} years of relevant experience`,
        'Proven track record of project delivery',
        'In-demand skills in high-growth technology areas',
        'Strong cultural fit and team integration ability'
      ],
      walkAwayPower: [
        'Have multiple opportunities in pipeline',
        'Know your minimum acceptable terms',
        'Understand your current situation\'s value',
        'Be prepared to decline gracefully if terms don\'t align'
      ]
    },

    strategicNetworking: {
      preInterviewOutreach: [
        'Connect with current employees in similar roles',
        'Engage with company content on social media',
        'Attend company events or webinars',
        'Research interviewer backgrounds and find common connections'
      ],
      duringInterviewConnections: [
        'Ask for business cards or LinkedIn connections',
        'Express genuine interest in people you meet',
        'Find common ground and shared experiences',
        'Show appreciation for their time and insights'
      ],
      postInterviewFollowUp: [
        'Send personalized thank you notes within 24 hours',
        'Connect on LinkedIn with thoughtful messages',
        'Share relevant articles or insights if appropriate',
        'Maintain professional relationship regardless of outcome'
      ],
      longTermRelationships: [
        'Stay in touch with valuable connections',
        'Offer help and value to your network',
        'Keep contacts updated on your career progress',
        'Leverage relationships for future opportunities'
      ]
    },

    performanceOptimization: {
      peakPerformanceRoutines: [
        'Consistent sleep schedule in days leading up to interview',
        'Light exercise to boost energy and confidence',
        'Healthy meals to maintain stable energy levels',
        'Meditation or mindfulness practice to stay centered'
      ],
      energyManagement: [
        'Schedule interviews at your peak energy times if possible',
        'Take breaks between back-to-back interviews',
        'Stay hydrated and maintain blood sugar levels',
        'Use positive visualization to maintain motivation'
      ],
      focusEnhancement: [
        'Eliminate distractions in your interview environment',
        'Practice active listening techniques',
        'Use note-taking to stay engaged and remember key points',
        'Prepare mentally for different interview formats'
      ],
      recoveryStrategies: [
        'Debrief after each interview to capture insights',
        'Practice self-compassion if things don\'t go perfectly',
        'Use setbacks as learning opportunities',
        'Maintain perspective on the bigger picture of your career'
      ]
    }
  }
}

function generateSalaryResearch(
  resumeData: EnhancedResumeData,
  jobContext: JobContext,
  seniorityLevel: string
): SalaryResearchGuide {
  
  const baseRanges = {
    junior: { min: 75000, max: 105000 },
    mid: { min: 95000, max: 135000 },
    senior: { min: 120000, max: 180000 }
  }
  
  const range = baseRanges[seniorityLevel as keyof typeof baseRanges] || baseRanges.mid
  
  return {
    marketRates: {
      baseRange: `$${range.min.toLocaleString()} - $${range.max.toLocaleString()}`,
      bonusStructure: '10-20% of base salary for performance bonus',
      equityExpectations: '0.1-1% equity depending on company stage and role level',
      totalCompRange: `$${Math.round(range.min * 1.15).toLocaleString()} - $${Math.round(range.max * 1.3).toLocaleString()} including benefits and equity`
    },
    negotiationStrategy: {
      anchoring: `Anchor at 75th percentile of market range: $${Math.round(range.min + (range.max - range.min) * 0.75).toLocaleString()}`,
      bundling: 'Negotiate total compensation package, not just base salary',
      timing: 'Wait for initial offer before discussing specific numbers',
      alternatives: [
        'Additional vacation time',
        'Professional development budget',
        'Flexible working arrangements',
        'Early equity vesting'
      ]
    },
    leverageFactors: [
      `${resumeData.experienceYears} years of relevant experience`,
      'In-demand technical skills',
      'Strong project delivery track record',
      'Cultural fit and team integration ability'
    ],
    riskFactors: [
      'Limited experience with specific technologies',
      'Competitive job market conditions',
      'Company budget constraints',
      'Internal equity considerations'
    ]
  }
}

function generateExecutivePresence(
  resumeData: EnhancedResumeData,
  seniorityLevel: string
): ExecutivePresenceCoaching {
  
  return {
    communicationMastery: {
      executiveLanguage: [
        'Use strategic terminology: "drive," "execute," "optimize," "scale"',
        'Frame discussions in terms of business impact and outcomes',
        'Speak about systems and processes, not just tasks',
        'Reference industry best practices and benchmarks'
      ],
      powerPhrases: [
        '"In my experience with [specific situation]..."',
        '"The way I approach this is..."',
        '"Based on the data/feedback I\'ve seen..."',
        '"The strategic benefit of this approach is..."'
      ],
      voiceModulation: [
        'Lower your voice slightly to convey authority',
        'Vary pace to emphasize important points',
        'Use pauses to create impact and allow processing',
        'Project confidence through clear articulation'
      ],
      pauseUsage: [
        'Pause after asking questions to allow thoughtful responses',
        'Use silence to emphasize key points',
        'Take a breath before answering difficult questions',
        'Allow processing time for complex topics'
      ]
    },

    bodyLanguage: {
      powerPoses: [
        'Stand with feet shoulder-width apart',
        'Keep shoulders back and chest open',
        'Maintain upright posture without rigidity',
        'Use open gestures with palms visible'
      ],
      gestureControl: [
        'Use purposeful gestures to support your message',
        'Keep movements controlled and deliberate',
        'Avoid fidgeting or repetitive movements',
        'Use hand gestures to emphasize key points'
      ],
      eyeContact: [
        'Maintain appropriate eye contact (3-5 seconds at a time)',
        'Look at each person in group settings',
        'Use eye contact to build connection and trust',
        'Break eye contact naturally, not abruptly'
      ],
      spatialAwareness: [
        'Respect personal space boundaries',
        'Use proximity to build rapport appropriately',
        'Position yourself to be seen by all participants',
        'Move with purpose and confidence'
      ]
    },

    mentalFramework: {
      executiveMindset: [
        'Think in terms of systems and scalability',
        'Consider multiple stakeholder perspectives',
        'Focus on outcomes and measurable impact',
        'Balance short-term execution with long-term vision'
      ],
      decisionMaking: [
        'Gather relevant data and stakeholder input',
        'Consider risks and mitigation strategies',
        'Make decisions promptly when enough information is available',
        'Take ownership of decisions and their consequences'
      ],
      riskAssessment: [
        'Identify potential failure points and contingencies',
        'Weigh probability and impact of different scenarios',
        'Consider both technical and business risks',
        'Plan for various outcomes and adaptation strategies'
      ],
      strategicThinking: [
        'Connect tactical decisions to strategic objectives',
        'Consider long-term implications of current choices',
        'Think about competitive advantages and market positioning',
        'Anticipate future trends and their implications'
      ]
    },

    presenceIndicators: {
      authorityMarkers: [
        'Speaking with conviction while remaining open to input',
        'Taking initiative in problem-solving discussions',
        'Referencing relevant experience and expertise',
        'Making clear recommendations based on analysis'
      ],
      competenceSignals: [
        'Asking insightful questions that show deep understanding',
        'Connecting concepts across different domains',
        'Providing specific examples and quantified results',
        'Demonstrating knowledge of industry best practices'
      ],
      trustBuilders: [
        'Acknowledging limitations and areas for growth',
        'Giving credit to team members and collaborators',
        'Following through on commitments made',
        'Showing genuine interest in others\' perspectives'
      ],
      influence: [
        'Building consensus through logical persuasion',
        'Using storytelling to make complex concepts accessible',
        'Finding win-win solutions that benefit multiple parties',
        'Inspiring others through vision and passion'
      ]
    }
  }
}

// Helper functions
function getRoleCategory(role: string): string {
  const roleStr = role.toLowerCase()
  if (roleStr.includes('data scientist') || roleStr.includes('machine learning') || roleStr.includes('ml engineer')) {
    return 'data-scientist'
  }
  if (roleStr.includes('software engineer') || roleStr.includes('developer') || roleStr.includes('backend') || roleStr.includes('frontend')) {
    return 'software-engineer'
  }
  if (roleStr.includes('product manager') || roleStr.includes('product owner')) {
    return 'product-manager'
  }
  return 'technical'
}

function determineArchetype(resumeData: EnhancedResumeData, seniorityLevel: string): string {
  // Determine brand archetype based on experience and skills
  if (seniorityLevel === 'senior') return 'The Leader'
  if (resumeData.stats.totalProjects >= 5) return 'The Builder'
  if (resumeData.technicalSkills.programmingLanguages.length >= 4) return 'The Innovator'
  return 'The Expert'
}

function getArchetypeCharacteristics(archetype: string): string[] {
  if (archetype === "The Leader") return ["Visionary", "Strategic", "Inspiring", "Results-oriented"]
  if (archetype === "The Builder") return ["Reliable", "Execution-focused", "Collaborative", "Solution-oriented"]
  if (archetype === "The Innovator") return ["Creative", "Adaptable", "Forward-thinking", "Technology-enthusiast"]
  return ["Knowledgeable", "Precise", "Analytical", "Detail-oriented"] // The Expert (default)
}

function getMessagingTone(archetype: string): string {
  if (archetype === "The Leader") return "Confident and inspiring with focus on vision and results"
  if (archetype === "The Builder") return "Practical and reliable with emphasis on execution and collaboration"
  if (archetype === "The Innovator") return "Enthusiastic and forward-thinking with focus on possibilities"
  return "Authoritative and precise with emphasis on knowledge and accuracy" // The Expert (default)
}

function getVisualIdentity(archetype: string): string[] {
  if (archetype === "The Leader") return ["Professional attire", "Confident posture", "Clear communication", "Executive presence"]
  if (archetype === "The Builder") return ["Approachable style", "Collaborative demeanor", "Practical focus", "Team-oriented"]
  if (archetype === "The Innovator") return ["Modern style", "Dynamic energy", "Creative thinking", "Tech-forward"]
  return ["Polished appearance", "Authoritative presence", "Detailed focus", "Professional credibility"] // The Expert (default)
}

// Legacy exports for backward compatibility
export interface CoachingInsights {
  personalizedTips?: string[]
  practiceQuestions?: any[]
  improvementAreas?: string[]
}

export async function generateCoachingInsights(resumeData: any, jobData: any): Promise<CoachingInsights> {
  // Basic implementation - can be enhanced later
  return {
    personalizedTips: [],
    practiceQuestions: [],
    improvementAreas: []
  }
}

export function createPersonalizedCoaching(data: any): any {
  return {}
}
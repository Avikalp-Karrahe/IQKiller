// Enhanced Question Generator for Role-Specific Interview Questions
import { type Question } from './questions-processor'

export interface EnhancedResumeData {
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

export interface JobContext {
  role?: string
  company?: string
  description?: string
  level?: 'junior' | 'mid' | 'senior' | 'staff'
}

interface QuestionTemplate {
  template: string
  whyTheyAsk: string
  approach: string
  followUpTemplates: string[]
}

interface RoleQuestions {
  technical?: QuestionTemplate[]
  behavioral?: QuestionTemplate[]
  systemDesign?: QuestionTemplate[]
}

// Role-specific question templates
const ROLE_QUESTION_BANKS: Record<string, RoleQuestions> = {
  'data-scientist': {
    technical: [
      {
        template: "Walk me through how you would approach a machine learning problem from start to finish, using a specific project from your experience.",
        whyTheyAsk: "Interviewers want to assess your end-to-end ML workflow understanding, from problem definition to model deployment and monitoring.",
        approach: "Use the CRISP-DM methodology: Business Understanding → Data Understanding → Data Preparation → Modeling → Evaluation → Deployment. Reference specific projects from your background.",
        followUpTemplates: [
          "How would you handle missing data in this scenario?",
          "What metrics would you use to evaluate model performance?",
          "How would you explain your model results to non-technical stakeholders?",
          "What would you do if your model performance degraded in production?"
        ]
      },
      {
        template: "Explain the difference between supervised and unsupervised learning, and give examples of when you've used each.",
        whyTheyAsk: "Tests fundamental ML knowledge and practical application experience. Shows depth of understanding beyond theoretical knowledge.",
        approach: "Define both clearly, then provide specific examples from your projects. Discuss the business context and why you chose each approach.",
        followUpTemplates: [
          "When would you choose one over the other?",
          "How do you evaluate the success of unsupervised learning models?",
          "Can you walk through a specific clustering project you've worked on?"
        ]
      },
      {
        template: "How do you handle feature engineering and selection in your machine learning pipeline?",
        whyTheyAsk: "Feature engineering often makes the biggest impact on model performance. Interviewers want to see your practical experience with this critical step.",
        approach: "Discuss your systematic approach: domain knowledge application, statistical methods, automated selection techniques. Use specific examples from your projects.",
        followUpTemplates: [
          "How do you deal with categorical variables with high cardinality?",
          "What techniques do you use to detect feature importance?",
          "How do you handle feature engineering for time series data?"
        ]
      }
    ],
    behavioral: [
      {
        template: "Tell me about a time when your initial data analysis led to unexpected insights that changed the direction of a project.",
        whyTheyAsk: "Data scientists must be adaptable and able to pivot based on data findings. This tests analytical thinking and communication skills.",
        approach: "Use STAR method. Focus on your analytical process, how you communicated findings, and the business impact of the pivot.",
        followUpTemplates: [
          "How did you communicate these findings to stakeholders?",
          "What resistance did you face when proposing the direction change?",
          "How did you validate your new hypothesis?"
        ]
      },
      {
        template: "Describe a situation where you had to work with messy, incomplete data. How did you approach cleaning and preparing it?",
        whyTheyAsk: "Real-world data is always messy. Interviewers want to see your problem-solving skills and attention to data quality.",
        approach: "Detail your data exploration process, quality assessment methods, and cleaning strategies. Emphasize the impact on final results.",
        followUpTemplates: [
          "How did you document your data cleaning process?",
          "What tools did you use for data quality assessment?",
          "How did you handle stakeholder expectations about timeline delays?"
        ]
      },
      {
        template: "Tell me about a time when you had to explain complex statistical concepts or model results to non-technical stakeholders.",
        whyTheyAsk: "Communication is crucial for data scientists. You need to translate technical insights into business value.",
        approach: "Focus on your storytelling approach, use of visualizations, and how you tailored the message to your audience.",
        followUpTemplates: [
          "What visual aids did you use to make the data more understandable?",
          "How did you handle pushback or skepticism about your findings?",
          "What questions did the stakeholders ask that you didn't expect?"
        ]
      }
    ],
    systemDesign: [
      {
        template: "Design a machine learning system to recommend products for an e-commerce platform with millions of users.",
        whyTheyAsk: "Tests ability to design scalable ML systems, considering data pipeline, model serving, and business constraints.",
        approach: "Start with requirements gathering, then design data pipeline → model training → serving → monitoring. Consider scalability, latency, and feedback loops.",
        followUpTemplates: [
          "How would you handle cold start problems for new users?",
          "What would you do if the recommendation quality suddenly dropped?",
          "How would you A/B test different recommendation algorithms?",
          "How would you scale this system to handle 10x more traffic?"
        ]
      },
      {
        template: "Design a real-time fraud detection system for a financial services company.",
        whyTheyAsk: "Combines ML knowledge with systems design, emphasizing real-time processing and high-stakes decision making.",
        approach: "Focus on real-time data ingestion, feature engineering, model serving with low latency, and handling false positives/negatives.",
        followUpTemplates: [
          "How would you handle the trade-off between false positives and false negatives?",
          "What would you do if legitimate transactions started getting flagged?",
          "How would you retrain models with new fraud patterns?"
        ]
      }
    ]
  },

  'software-engineer': {
    technical: [
      {
        template: "Walk me through how you would design and implement a rate limiting system for an API.",
        whyTheyAsk: "Tests understanding of system design principles, algorithms (token bucket, sliding window), and practical implementation skills.",
        approach: "Discuss different algorithms, trade-offs, implementation details, and how you'd handle edge cases. Reference your experience with similar systems.",
        followUpTemplates: [
          "How would you implement this in a distributed system?",
          "What would you do if the rate limiter itself became a bottleneck?",
          "How would you handle different rate limits for different user tiers?"
        ]
      },
      {
        template: "Explain how you've optimized application performance in a recent project. What tools and techniques did you use?",
        whyTheyAsk: "Performance optimization is crucial for user experience. Shows practical experience with profiling, monitoring, and optimization techniques.",
        approach: "Describe your systematic approach: identify bottlenecks → profile → optimize → measure. Use specific examples and metrics.",
        followUpTemplates: [
          "What was the most surprising performance bottleneck you discovered?",
          "How do you balance code readability with performance optimization?",
          "What monitoring tools do you use to track performance in production?"
        ]
      },
      {
        template: "Describe your approach to handling errors and exceptions in a distributed system.",
        whyTheyAsk: "Error handling is critical in distributed systems. Tests understanding of resilience patterns and operational concerns.",
        approach: "Discuss error categories, retry strategies, circuit breakers, and graceful degradation. Reference specific implementations.",
        followUpTemplates: [
          "How do you decide between fail-fast vs. retry strategies?",
          "What's your approach to handling partial failures?",
          "How do you ensure error messages are useful for debugging?"
        ]
      }
    ],
    behavioral: [
      {
        template: "Tell me about a time when you had to refactor a large, legacy codebase. How did you approach it?",
        whyTheyAsk: "Refactoring skills are essential for maintaining code quality. Tests planning, risk management, and execution skills.",
        approach: "Describe your assessment process, prioritization strategy, and incremental approach. Emphasize testing and risk mitigation.",
        followUpTemplates: [
          "How did you ensure you didn't break existing functionality?",
          "How did you get buy-in from stakeholders for the refactoring effort?",
          "What tools did you use to assess code quality and technical debt?"
        ]
      },
      {
        template: "Describe a situation where you disagreed with a technical decision made by your team or manager. How did you handle it?",
        whyTheyAsk: "Tests communication skills, technical judgment, and ability to influence without authority.",
        approach: "Focus on respectful disagreement, data-driven arguments, and collaborative problem-solving. Show emotional intelligence.",
        followUpTemplates: [
          "How did you present your alternative solution?",
          "What data or evidence did you use to support your position?",
          "How did you maintain a good working relationship after the disagreement?"
        ]
      }
    ],
    systemDesign: [
      {
        template: "Design a chat application like WhatsApp that supports millions of concurrent users.",
        whyTheyAsk: "Classic system design question testing scalability, real-time communication, and distributed systems knowledge.",
        approach: "Cover user requirements → high-level architecture → detailed components → scalability considerations → trade-offs.",
        followUpTemplates: [
          "How would you implement message delivery guarantees?",
          "How would you handle users going offline and coming back online?",
          "How would you implement group chats with thousands of participants?"
        ]
      }
    ]
  },

  'product-manager': {
    behavioral: [
      {
        template: "Tell me about a time when you had to make a product decision with incomplete data. How did you approach it?",
        whyTheyAsk: "Product managers often work with uncertainty. Tests decision-making frameworks and comfort with ambiguity.",
        approach: "Describe your framework for decision-making under uncertainty, how you gathered available data, and how you managed risks.",
        followUpTemplates: [
          "How did you communicate the uncertainty to stakeholders?",
          "What would you have done differently with more time or data?",
          "How did you measure success after the decision was implemented?"
        ]
      }
    ]
  },

  'default': {
    technical: [
      {
        template: "Describe a challenging technical problem you solved recently. Walk me through your thought process.",
        whyTheyAsk: "General problem-solving assessment. Tests analytical thinking and technical depth.",
        approach: "Use a structured approach: problem definition → analysis → solution exploration → implementation → results.",
        followUpTemplates: [
          "What alternative solutions did you consider?",
          "How did you validate your solution?",
          "What would you do differently if you had to solve it again?"
        ]
      }
    ],
    behavioral: [
      {
        template: "Tell me about a time when you had to learn a new technology or skill quickly for a project.",
        whyTheyAsk: "Tests adaptability and learning ability, which are crucial in fast-changing tech environments.",
        approach: "Describe your learning strategy, resources used, and how you applied the knowledge practically.",
        followUpTemplates: [
          "What resources did you find most helpful for learning?",
          "How did you balance learning with project deadlines?",
          "How do you stay updated with new technologies in your field?"
        ]
      }
    ]
  }
}

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
  return 'default'
}

export function generateEnhancedQuestions(
  resumeData: EnhancedResumeData,
  jobContext: JobContext = {}
): Question[] {
  const roleCategory = getRoleCategory(jobContext.role || resumeData.currentRole)
  const questionBank = ROLE_QUESTION_BANKS[roleCategory]
  
  const questions: Question[] = []
  let questionId = 1

  // Generate 3+ technical questions
  const technicalTemplates = questionBank.technical || ROLE_QUESTION_BANKS.default.technical || []
  technicalTemplates.forEach((template: QuestionTemplate, index: number) => {
    const question = createPersonalizedQuestion(
      questionId++,
      template,
      'technical',
      resumeData,
      jobContext
    )
    questions.push(question)
  })

  // Generate 3+ behavioral questions
  const behavioralTemplates = questionBank.behavioral || ROLE_QUESTION_BANKS.default.behavioral || []
  behavioralTemplates.forEach((template: QuestionTemplate, index: number) => {
    const question = createPersonalizedQuestion(
      questionId++,
      template,
      'behavioral',
      resumeData,
      jobContext
    )
    questions.push(question)
  })

  // Generate 2+ system design questions (if available for role)
  if (questionBank.systemDesign) {
    questionBank.systemDesign.forEach((template: QuestionTemplate, index: number) => {
      const question = createPersonalizedQuestion(
        questionId++,
        template,
        'system-design',
        resumeData,
        jobContext
      )
      questions.push(question)
    })
  }

  return questions
}

function createPersonalizedQuestion(
  id: number,
  template: QuestionTemplate,
  category: string,
  resumeData: EnhancedResumeData,
  jobContext: JobContext
): Question {
  // Personalize the question text with resume-specific details
  let personalizedTitle = template.template
  
  // Replace placeholders with actual resume data
  const primaryTech = resumeData.technicalSkills.programmingLanguages[0] || 'your primary technology'
  const frameworks = resumeData.technicalSkills.frameworks.slice(0, 2).join(' and ') || 'modern frameworks'
  const projectCount = resumeData.stats.totalProjects

  // Create personalized talking points from resume
  const talkingPoints = extractTalkingPoints(resumeData, category)
  
  // Generate personalized follow-ups
  const personalizedFollowUps = template.followUpTemplates.map((followUp: string) => 
    followUp.replace(/\{primaryTech\}/g, primaryTech)
             .replace(/\{frameworks\}/g, frameworks)
  )

  // Create difficulty based on experience
  const difficulty: 'junior' | 'mid' | 'senior' = resumeData.experienceYears <= 1 ? 'junior' : 
                    resumeData.experienceYears <= 4 ? 'mid' : 'senior'

  return {
    id: id.toString(),
    title: personalizedTitle,
    summaries: template.whyTheyAsk,
    type: category,
    link: '',
    difficulty,
    approach: template.approach,
    relevance: template.whyTheyAsk,
    followUps: personalizedFollowUps
  }
}

function extractTalkingPoints(resumeData: EnhancedResumeData, category: string): string {
  const points: string[] = []

  if (category === 'technical') {
    // Technical talking points
    if (resumeData.technicalSkills.programmingLanguages.length > 0) {
      points.push(`Highlight your expertise in ${resumeData.technicalSkills.programmingLanguages.slice(0, 2).join(' and ')}`)
    }
    if (resumeData.projects.length > 0) {
      const topProject = resumeData.projects[0]
      points.push(`Reference your "${topProject.title}" project which used ${topProject.technologies.slice(0, 2).join(' and ')}`)
    }
    if (resumeData.technicalSkills.frameworks.length > 0) {
      points.push(`Mention your experience with ${resumeData.technicalSkills.frameworks[0]}`)
    }
  } else if (category === 'behavioral') {
    // Behavioral talking points
    points.push(`Draw examples from your ${resumeData.experienceYears} years as a ${resumeData.currentRole}`)
    if (resumeData.projects.length >= 2) {
      points.push(`Use examples from projects like "${resumeData.projects[0].title}" and "${resumeData.projects[1].title}"`)
    }
    points.push(`Emphasize your collaborative experience across ${resumeData.stats.totalProjects} projects`)
  } else if (category === 'system-design') {
    // System design talking points
    if (resumeData.technicalSkills.databases.length > 0) {
      points.push(`Reference your database experience with ${resumeData.technicalSkills.databases.slice(0, 2).join(' and ')}`)
    }
    points.push(`Apply lessons learned from scaling challenges in your projects`)
    if (resumeData.experienceYears >= 3) {
      points.push(`Leverage your senior-level perspective on architecture decisions`)
    }
  }

  return points.join('. ')
}

// Enhanced question categories with better structure
export const ENHANCED_QUESTION_CATEGORIES = {
  technical: {
    name: 'Technical Questions',
    description: 'Deep-dive into your technical skills and problem-solving abilities',
    icon: '🔧',
    count: 3
  },
  behavioral: {
    name: 'Behavioral Questions', 
    description: 'Assess your soft skills, teamwork, and cultural fit',
    icon: '👥',
    count: 3
  },
  systemDesign: {
    name: 'System Design Questions',
    description: 'Evaluate your ability to design scalable, robust systems',
    icon: '🏗️',
    count: 2
  }
} 
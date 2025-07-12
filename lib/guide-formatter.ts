// Guide formatting utilities
import { getRoleFamily, type RoleFamily } from './enhanced-question-generator'

export interface ComprehensiveGuide {
  introduction?: {
    roleOverview?: string
    culture?: string
    whyThisRole?: string
  }
  preparation?: {
    tips?: Array<{ title: string; description: string }>
    studyPlan?: string
  }
  questions?: {
    technical?: Array<any>
    behavioral?: Array<any>
    caseStudy?: Array<any>
  }
  conclusion?: {
    summary?: string
    resources?: Record<string, { title: string; link: string }>
  }
  faqs?: {
    salary?: string
    experiences?: string
    jobPostings?: string
  }
  interviewProcess?: {
    stages?: Array<{ name: string; duration: string; description: string }>
    levelDifferences?: string
  }
  // Add role context for dynamic labeling
  roleContext?: {
    title?: string
    company?: string
    description?: string
  }
}

export function getGuideStats(guide: ComprehensiveGuide) {
  const technicalCount = guide?.questions?.technical?.length || 0
  const behavioralCount = guide?.questions?.behavioral?.length || 0
  const caseStudyCount = guide?.questions?.caseStudy?.length || 0
  const totalQuestions = technicalCount + behavioralCount + caseStudyCount
  
  return {
    totalQuestions,
    technicalCount,
    behavioralCount,
    caseStudyCount,
    preparationTips: guide?.preparation?.tips?.length || 0,
    resourceCount: Object.keys(guide?.conclusion?.resources || {}).length
  }
}

// Role-aware question category labels
function getQuestionCategoryLabels(roleFamily: RoleFamily): {
  technical: string
  behavioral: string
  systemDesign: string
} {
  const labelMappings: Record<RoleFamily, { technical: string; behavioral: string; systemDesign: string }> = {
    'data-scientist': {
      technical: 'SQL & Analytics Questions',
      behavioral: 'Behavioral Questions', 
      systemDesign: 'Machine Learning Questions'
    },
    'software-engineer': {
      technical: 'Technical Questions',
      behavioral: 'Behavioral Questions',
      systemDesign: 'System Design Questions'
    },
    'product-manager': {
      technical: 'Technical Questions',
      behavioral: 'Behavioral Questions',
      systemDesign: 'Product Strategy Questions'
    },
    'engineering-manager': {
      technical: 'Technical Questions',
      behavioral: 'Leadership & Behavioral Questions',
      systemDesign: 'System Design Questions'
    },
    'director': {
      technical: 'Technical Questions',
      behavioral: 'Leadership & Behavioral Questions',
      systemDesign: 'Strategic Questions'
    },
    'business-analyst': {
      technical: 'Technical Questions',
      behavioral: 'Behavioral Questions',
      systemDesign: 'Business Analysis Questions'
    },
    'devops': {
      technical: 'Technical Questions',
      behavioral: 'Behavioral Questions',
      systemDesign: 'DevOps & Infrastructure Questions'
    },
    'security': {
      technical: 'Security & Technical Questions',
      behavioral: 'Behavioral Questions',
      systemDesign: 'System Design Questions'
    },
    'designer': {
      technical: 'Technical Questions',
      behavioral: 'Behavioral Questions',
      systemDesign: 'Design & UX Questions'
    },
    'consultant': {
      technical: 'Technical Questions',
      behavioral: 'Behavioral Questions',
      systemDesign: 'Business Strategy Questions'
    },
    'default': {
      technical: 'Technical Questions',
      behavioral: 'Behavioral Questions',
      systemDesign: 'System Design Questions'
    }
  }

  return labelMappings[roleFamily] || labelMappings['default']
}

export function generateQuestionSummary(guide: ComprehensiveGuide, roleTitle?: string, roleDescription?: string): string {
  const stats = getGuideStats(guide)
  
  // Determine role family for dynamic labeling
  const roleFamily = roleTitle ? getRoleFamily(roleTitle, roleDescription) : 'default'
  const labels = getQuestionCategoryLabels(roleFamily)
  
  return `## Question Overview

**Total Questions: ${stats.totalQuestions}**

- **${labels.technical}:** ${stats.technicalCount}
- **${labels.behavioral}:** ${stats.behavioralCount}  
- **${labels.systemDesign}:** ${stats.caseStudyCount}

### Question Distribution
This personalized question set covers the key areas you'll encounter in your interview process.

${stats.technicalCount > 0 ? `**${labels.technical}** focus on your technical skills and domain knowledge relevant to the role.` : ''}

${stats.behavioralCount > 0 ? `**${labels.behavioral}** explore your past experiences and how you approach workplace situations.` : ''}

${stats.caseStudyCount > 0 ? `**${labels.systemDesign}** test your ability to ${getRoleSpecificDescription(roleFamily)}.` : ''}

### Preparation Approach
- Review each question category thoroughly
- Practice explaining your thought process out loud
- Prepare specific examples from your experience
- Focus on the STAR method for behavioral questions
`
}

// Get role-specific description for the third category
function getRoleSpecificDescription(roleFamily: RoleFamily): string {
  const descriptions: Record<RoleFamily, string> = {
    'data-scientist': 'build and evaluate machine learning models for real-world problems',
    'software-engineer': 'architect and design scalable solutions',
    'product-manager': 'develop strategic product roadmaps and launch successful features',
    'engineering-manager': 'lead teams and design system architectures',
    'director': 'think strategically and make high-level decisions',
    'business-analyst': 'analyze business requirements and design solutions',
    'devops': 'design infrastructure and deployment strategies',
    'security': 'architect secure systems and assess risks',
    'designer': 'create user-centered designs and solve UX challenges',
    'consultant': 'develop strategic business solutions',
    'default': 'architect and design scalable solutions'
  }
  
  return descriptions[roleFamily] || descriptions['default']
}

export function formatComprehensiveGuide(guide: ComprehensiveGuide): string {
  // Basic formatting - can be enhanced later
  return JSON.stringify(guide, null, 2)
}

// Export the role-aware labeling function for use in UI components
export function getUILabelsForRole(roleTitle?: string, roleDescription?: string): {
  technical: string
  behavioral: string
  systemDesign: string
} {
  const roleFamily = roleTitle ? getRoleFamily(roleTitle, roleDescription) : 'default'
  return getQuestionCategoryLabels(roleFamily)
}

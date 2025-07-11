// Guide formatting utilities
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

export function generateQuestionSummary(guide: ComprehensiveGuide): string {
  const stats = getGuideStats(guide)
  
  return `## Question Overview

**Total Questions: ${stats.totalQuestions}**

- **Technical Questions:** ${stats.technicalCount}
- **Behavioral Questions:** ${stats.behavioralCount}  
- **System Design/Case Study:** ${stats.caseStudyCount}

### Question Distribution
This personalized question set covers the key areas you'll encounter in your interview process.

${stats.technicalCount > 0 ? '**Technical questions** focus on your programming skills and technical knowledge relevant to the role.' : ''}

${stats.behavioralCount > 0 ? '**Behavioral questions** explore your past experiences and how you approach workplace situations.' : ''}

${stats.caseStudyCount > 0 ? '**System design questions** test your ability to architect and design scalable solutions.' : ''}

### Preparation Approach
- Review each question category thoroughly
- Practice explaining your thought process out loud
- Prepare specific examples from your experience
- Focus on the STAR method for behavioral questions
`
}

export function formatComprehensiveGuide(guide: ComprehensiveGuide): string {
  // Basic formatting - can be enhanced later
  return JSON.stringify(guide, null, 2)
}

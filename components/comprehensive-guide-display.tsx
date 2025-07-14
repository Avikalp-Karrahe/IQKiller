import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  Clock, 
  BookOpen, 
  Users, 
  Target, 
  ExternalLink,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Briefcase,
  Building,
  Network,
  HelpCircle,
  Star,
  MessageSquare,
  Github,
  Linkedin,
  Mail
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { formatComprehensiveGuide, generateQuestionSummary, getGuideStats, getUILabelsForRole, type ComprehensiveGuide } from '@/lib/guide-formatter'
import { type Question } from '@/lib/questions-processor'

interface ComprehensiveGuideDisplayProps {
  guide: ComprehensiveGuide
  isGenerating?: boolean
}

export function ComprehensiveGuideDisplay({ guide, isGenerating = false }: ComprehensiveGuideDisplayProps) {
  const [activeTab, setActiveTab] = useState('overview')
  const stats = getGuideStats(guide)

  if (isGenerating) {
    return <GeneratingGuideLoader />
  }

  // Extract role information for dynamic labeling
  const roleTitle = guide.roleContext?.title
  const roleDescription = guide.roleContext?.description
  const uiLabels = getUILabelsForRole(roleTitle, roleDescription)

  return (
    <div className="w-full max-w-5xl mx-auto space-y-6">
      {/* Header Section */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20 rounded-xl p-6 border border-blue-200 dark:border-blue-800">
        <div className="mb-4">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {roleTitle ? `${roleTitle} Interview Guide` : 'Interview Preparation Guide'}
          </h1>
          <p className="text-gray-600 dark:text-gray-300 mb-4">
            Personalized for {(guide as any).personalizedFor || 'You'} • Generated on {new Date().toLocaleDateString()}
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard
            icon={<BookOpen className="w-5 h-5" />}
            label="Questions"
            value={stats.totalQuestions.toString()}
            subtitle="Personalized"
          />
          <StatCard
            icon={<Clock className="w-5 h-5" />}
            label="Reading Time"
            value={`${Math.max(5, Math.ceil(stats.totalQuestions * 0.5))} min`}
            subtitle="Estimated"
          />
          <StatCard
            icon={<Target className="w-5 h-5" />}
            label="Prep Tips"
            value={stats.preparationTips.toString()}
            subtitle="Actionable"
          />
          <StatCard
            icon={<TrendingUp className="w-5 h-5" />}
            label="Difficulty"
            value="Matched"
            subtitle="To experience"
          />
        </div>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-9">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="process">Process</TabsTrigger>
          <TabsTrigger value="questions">Questions</TabsTrigger>
          <TabsTrigger value="preparation">Preparation</TabsTrigger>
          <TabsTrigger value="timeline">Timeline</TabsTrigger>
          <TabsTrigger value="star-method">STAR Method</TabsTrigger>
          <TabsTrigger value="smart-questions">Smart Questions</TabsTrigger>
          <TabsTrigger value="branding">Branding</TabsTrigger>
          <TabsTrigger value="resources">Resources</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <OverviewSection guide={guide} roleTitle={roleTitle} roleDescription={roleDescription} />
        </TabsContent>

        <TabsContent value="process" className="space-y-6">
          <InterviewProcessSection guide={guide} />
        </TabsContent>

        <TabsContent value="questions" className="space-y-6">
          <QuestionsSection guide={guide} uiLabels={uiLabels} />
        </TabsContent>

        <TabsContent value="preparation" className="space-y-6">
          <PreparationSection guide={guide} />
        </TabsContent>

        <TabsContent value="timeline" className="space-y-6">
          <TimelineSection premiumContent={(guide as any).premiumContent} />
        </TabsContent>

        <TabsContent value="star-method" className="space-y-6">
          <STARMethodSection premiumContent={(guide as any).premiumContent} />
        </TabsContent>

        <TabsContent value="smart-questions" className="space-y-6">
          <SmartQuestionsSection premiumContent={(guide as any).premiumContent} />
        </TabsContent>

        <TabsContent value="branding" className="space-y-6">
          <BrandingSection premiumContent={(guide as any).premiumContent} />
        </TabsContent>

        <TabsContent value="resources" className="space-y-6">
          <ResourcesSection guide={guide} />
          <CompanyResearchSection premiumContent={(guide as any).premiumContent} />
        </TabsContent>
      </Tabs>
    </div>
  )
}

function StatCard({ icon, label, value, subtitle }: {
  icon: React.ReactNode
  label: string
  value: string
  subtitle: string
}) {
  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
      <div className="flex items-center gap-3">
        <div className="text-blue-600 dark:text-blue-400">
          {icon}
        </div>
        <div>
          <div className="text-lg font-semibold text-gray-900 dark:text-white">
            {value}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-300">
            {label}
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400">
            {subtitle}
          </div>
        </div>
      </div>
    </div>
  )
}

function OverviewSection({ guide, roleTitle, roleDescription }: { 
  guide: ComprehensiveGuide
  roleTitle?: string
  roleDescription?: string 
}) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="w-5 h-5" />
            Interview Overview
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h4 className="font-semibold mb-2">Role Overview</h4>
            <p className="text-gray-700 dark:text-gray-300">{guide.introduction?.roleOverview || 'Role overview information will be provided during analysis.'}</p>
          </div>
          <Separator />
          <div>
            <h4 className="font-semibold mb-2">Company Culture</h4>
            <p className="text-gray-700 dark:text-gray-300">{guide.introduction?.culture || 'Company culture insights will be provided during analysis.'}</p>
          </div>
          <Separator />
          <div>
            <h4 className="font-semibold mb-2">Why This Opportunity?</h4>
            <p className="text-gray-700 dark:text-gray-300">{guide.introduction?.whyThisRole || 'Opportunity insights will be provided during analysis.'}</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Quick Question Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <ReactMarkdown className="prose prose-sm dark:prose-invert max-w-none">
            {generateQuestionSummary(guide, roleTitle, roleDescription)}
          </ReactMarkdown>
        </CardContent>
      </Card>

      {/* Community & Creator Section */}
      <div className="space-y-8">
        {/* Community Engagement */}
        <Card className="border-2 border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950/20">
          <CardContent className="p-6 text-center">
            <div className="flex justify-center mb-4">
              <MessageSquare className="w-8 h-8 text-blue-600 dark:text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Join the Community Building This
            </h3>
            
            {/* Stats and Community Info */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">1,000+</div>
                <div className="text-sm text-gray-600 dark:text-gray-300">Job Seekers Helped</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600 dark:text-green-400">100%</div>
                <div className="text-sm text-gray-600 dark:text-gray-300">Free & Open Source</div>
              </div>
            </div>
            
            <div className="flex gap-3 justify-center">
              <Button 
                className="bg-blue-600 hover:bg-blue-700 text-white"
                onClick={() => window.open('https://github.com/Avikalp-Karrahe/iqkiller-vercel', '_blank')}
              >
                <Github className="w-4 h-4 mr-2" />
                Star on GitHub
              </Button>
              <Button 
                variant="outline"
                onClick={() => window.open('https://discord.gg/sEAEu6abdn', '_blank')}
              >
                <MessageSquare className="w-4 h-4 mr-2" />
                Send Feedback
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Creator Section */}
        <Card className="border-2 border-amber-200 dark:border-amber-800 bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-950/20 dark:to-orange-950/20">
          <CardContent className="p-8">
            <div className="grid md:grid-cols-2 gap-8 items-center">
              {/* Left Side - About Creator */}
              <div>
                <div className="flex items-center gap-4 mb-6">
                  <img 
                    src="https://github.com/Avikalp-Karrahe.png?size=256" 
                    alt="Avikalp Karrahe" 
                    className="w-16 h-16 rounded-full border-2 border-amber-300 dark:border-amber-600"
                  />
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900 dark:text-white">About the Creator</h3>
                    <p className="text-amber-700 dark:text-amber-300 font-medium">Avikalp Karrahe</p>
                    <p className="text-gray-600 dark:text-gray-300 text-sm">AI Engineer & 3x San Francisco Bay Area Hackathon Winner</p>
                  </div>
                </div>
                
                <p className="text-gray-700 dark:text-gray-300 mb-6 leading-relaxed">
                  I've been through 50+ interviews at companies like Google, Microsoft, and startups. 
                  I know the frustration of generic prep materials that don't match what you actually get asked. 
                  That's why IQKiller generates questions tailored to YOUR specific background and the exact role you want.
                </p>
                
                <div className="mb-6">
                  <p className="text-gray-900 dark:text-white font-medium mb-3">Connect with me:</p>
                  <div className="flex gap-3">
                    <Button 
                      className="bg-blue-600 hover:bg-blue-700 text-white flex-1"
                      onClick={() => window.open('https://www.linkedin.com/in/avikalp/', '_blank')}
                    >
                      <Linkedin className="w-4 h-4 mr-2" />
                      LinkedIn
                    </Button>
                    <Button 
                      className="bg-gray-800 hover:bg-gray-900 text-white flex-1"
                      onClick={() => window.open('https://github.com/Avikalp-Karrahe', '_blank')}
                    >
                      <Github className="w-4 h-4 mr-2" />
                      GitHub
                    </Button>
                  </div>
                </div>
              </div>

              {/* Right Side - Want to Reach Job Seekers */}
              <div>
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Want to Reach Job Seekers?</h3>
                
                <p className="text-gray-700 dark:text-gray-300 mb-6 leading-relaxed">
                  IQKiller reaches professionals actively preparing for interviews at top companies. If you build tools, courses, or services for job seekers, this is where they're looking.
                </p>

                <div className="mb-6">
                  <Button 
                    variant="outline"
                    className="w-full justify-center mb-4"
                    onClick={() => window.open('https://discord.gg/sEAEu6abdn', '_blank')}
                  >
                    <MessageSquare className="w-4 h-4 mr-2" />
                    Partner with Us
                  </Button>
                </div>


              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

function InterviewProcessSection({ guide }: { guide: ComprehensiveGuide }) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5" />
            Interview Process Flow
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {(guide.interviewProcess?.stages || []).map((stage, idx) => (
              <div key={idx} className="flex gap-4">
                <div className="flex flex-col items-center">
                  <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center text-sm font-semibold text-blue-600 dark:text-blue-400">
                    {idx + 1}
                  </div>
                  {idx < (guide.interviewProcess?.stages || []).length - 1 && (
                    <div className="w-px h-12 bg-gray-300 dark:bg-gray-600 mt-2" />
                  )}
                </div>
                <div className="flex-1 pb-6">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-gray-900 dark:text-white">{stage.name}</h4>
                    <Badge variant="secondary">{stage.duration}</Badge>
                  </div>
                  <p className="text-gray-600 dark:text-gray-300 text-sm">{stage.description}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Format: Virtual/In-person</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Level-Specific Expectations</CardTitle>
        </CardHeader>
        <CardContent>
          <ReactMarkdown className="prose prose-sm dark:prose-invert max-w-none">
            {guide.interviewProcess?.levelDifferences || 'Interview expectations will vary based on your experience level and the specific role requirements.'}
          </ReactMarkdown>
        </CardContent>
      </Card>
    </div>
  )
}

function QuestionsSection({ guide, uiLabels }: { 
  guide: ComprehensiveGuide
  uiLabels: { technical: string; behavioral: string; systemDesign: string }
}) {
  return (
    <div className="space-y-6">
      <QuestionCategoryCard 
        title={uiLabels.technical}
        questions={guide.questions?.technical || []}
        icon={<Target className="w-5 h-5" />}
        color="blue"
      />
      <QuestionCategoryCard 
        title={uiLabels.behavioral}
        questions={guide.questions?.behavioral || []}
        icon={<Users className="w-5 h-5" />}
        color="green"
      />
      <QuestionCategoryCard 
        title={uiLabels.systemDesign}
        questions={guide.questions?.caseStudy || []}
        icon={<BookOpen className="w-5 h-5" />}
        color="purple"
      />
    </div>
  )
}

function QuestionCategoryCard({ 
  title, 
  questions, 
  icon, 
  color 
}: { 
  title: string
  questions: Question[]
  icon: React.ReactNode
  color: 'blue' | 'green' | 'purple'
}) {
  const colorClasses = {
    blue: 'border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950/20',
    green: 'border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-950/20',
    purple: 'border-purple-200 dark:border-purple-800 bg-purple-50 dark:bg-purple-950/20'
  }

  return (
    <Card className={colorClasses[color]}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {icon}
          {title}
          <Badge variant="secondary">{questions.length}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {questions.map((question, idx) => (
            <QuestionDisplay key={idx} question={question} index={idx + 1} />
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

function QuestionDisplay({ question, index }: { question: Question; index: number }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-white dark:bg-gray-900">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h4 className="font-semibold text-gray-900 dark:text-white mb-1">
            {index}. {question.title}
          </h4>
          <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
            {question.summaries}
          </p>
          <div className="flex items-center gap-3">
            <Badge variant="outline" className="text-xs">
              {question.type}
            </Badge>
            <Badge variant="outline" className="text-xs">
              {question.difficulty}
            </Badge>
            {question.link && (
              <Button 
                variant="ghost" 
                size="sm" 
                className="text-xs p-1 h-auto"
                onClick={() => window.open(`https://${question.link}`, '_blank')}
              >
                <ExternalLink className="w-3 h-3 mr-1" />
                View Original
              </Button>
            )}
          </div>
        </div>
        <Button 
          variant="ghost" 
          size="sm"
          onClick={() => setExpanded(!expanded)}
          className="ml-4"
        >
          {expanded ? 'Less' : 'More'}
        </Button>
      </div>

      {expanded && (
        <div className="border-t border-gray-200 dark:border-gray-700 pt-3 space-y-3">
          {question.approach && (
            <div>
              <h5 className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                💡 Approach
              </h5>
              <p className="text-sm text-gray-600 dark:text-gray-300">
                {question.approach}
              </p>
            </div>
          )}
          
          {question.relevance && (
            <div>
              <h5 className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                Why This Matters
              </h5>
              <p className="text-sm text-gray-600 dark:text-gray-300">
                {question.relevance}
              </p>
            </div>
          )}

          {question.followUps && question.followUps.length > 0 && (
            <div>
              <h5 className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                ❓ Follow-up Questions
              </h5>
              <ul className="text-sm text-gray-600 dark:text-gray-300 space-y-1">
                {question.followUps.map((followUp, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-gray-400 mt-1">•</span>
                    <span>{followUp}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function TimelineSection({ premiumContent }: { premiumContent?: any }) {
  if (!premiumContent?.timelineOptions) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Preparation Timelines</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600 dark:text-gray-300">
            Premium preparation timelines will be available soon.
          </p>
        </CardContent>
      </Card>
    )
  }

  const { oneWeek, twoWeeks, oneMonth } = premiumContent.timelineOptions

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="w-5 h-5" />
            Preparation Timeline Options
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600 dark:text-gray-300 mb-6">
            Choose the timeline that best fits your schedule and preparation needs.
          </p>
          
          <Tabs defaultValue="twoWeeks" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="oneWeek">1 Week (Intensive)</TabsTrigger>
              <TabsTrigger value="twoWeeks">2 Weeks (Balanced)</TabsTrigger>
              <TabsTrigger value="oneMonth">1 Month (Comprehensive)</TabsTrigger>
            </TabsList>
            
            <TabsContent value="oneWeek" className="space-y-4">
              <TimelineDisplay timeline={oneWeek} />
            </TabsContent>
            
            <TabsContent value="twoWeeks" className="space-y-4">
              <TimelineDisplay timeline={twoWeeks} />
            </TabsContent>
            
            <TabsContent value="oneMonth" className="space-y-4">
              <TimelineDisplay timeline={oneMonth} />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}

function TimelineDisplay({ timeline }: { timeline: any }) {
  return (
    <div className="space-y-6">
      <div className="bg-blue-50 dark:bg-blue-950/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
        <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
          {timeline.duration} Preparation Plan
        </h4>
        <p className="text-blue-800 dark:text-blue-200 text-sm">
          Daily Commitment: {timeline.dailyCommitment}
        </p>
      </div>

      <div className="space-y-4">
        {timeline.phases?.map((phase: any, idx: number) => (
          <Card key={idx} className="border-l-4 border-l-blue-500">
            <CardHeader>
              <CardTitle className="text-lg">{phase.phase}</CardTitle>
              <p className="text-sm text-gray-600 dark:text-gray-300">
                {phase.duration} • Focus: {phase.focus}
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h5 className="font-medium mb-2">Activities:</h5>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  {phase.activities?.map((activity: string, actIdx: number) => (
                    <li key={actIdx} className="text-gray-700 dark:text-gray-300">
                      {activity}
                    </li>
                  ))}
                </ul>
              </div>
              
              <div>
                <h5 className="font-medium mb-2">Success Criteria:</h5>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  {phase.successCriteria?.map((criteria: string, critIdx: number) => (
                    <li key={critIdx} className="text-gray-700 dark:text-gray-300">
                      {criteria}
                    </li>
                  ))}
                </ul>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

function STARMethodSection({ premiumContent }: { premiumContent?: any }) {
  if (!premiumContent?.starMethodGuide) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>STAR Method Guide</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600 dark:text-gray-300">
            Premium STAR method guidance will be available soon.
          </p>
        </CardContent>
      </Card>
    )
  }

  const { framework, storyBank } = premiumContent.starMethodGuide

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="w-5 h-5" />
            STAR Method Framework
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600 dark:text-gray-300 mb-6">
            Master the STAR method to deliver compelling behavioral interview responses.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(framework).map(([key, component]: [string, any]) => (
              <Card key={key} className="border-l-4 border-l-green-500">
                <CardHeader>
                  <CardTitle className="text-lg capitalize">{key}</CardTitle>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    {component.timeAllocation}
                  </p>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-sm">{component.definition}</p>
                  
                  <div>
                    <h5 className="font-medium text-sm mb-1">Key Elements:</h5>
                    <ul className="list-disc list-inside text-xs space-y-1">
                      {component.keyElements?.map((element: string, idx: number) => (
                        <li key={idx} className="text-gray-600 dark:text-gray-300">
                          {element}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div>
                    <h5 className="font-medium text-sm mb-1">Power Words:</h5>
                    <div className="flex flex-wrap gap-1">
                      {component.powerWords?.map((word: string, idx: number) => (
                        <Badge key={idx} variant="secondary" className="text-xs">
                          {word}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Story Bank Categories</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(storyBank).map(([category, stories]: [string, any]) => (
              <Card key={category} className="border border-gray-200 dark:border-gray-700">
                <CardHeader>
                  <CardTitle className="text-base capitalize">{category.replace(/([A-Z])/g, ' $1')}</CardTitle>
                </CardHeader>
                <CardContent>
                  {Array.isArray(stories) && stories.length > 0 && (
                    <div className="space-y-2">
                      <h5 className="font-medium text-sm">Sample Questions:</h5>
                      <ul className="list-disc list-inside text-xs space-y-1">
                        {stories[0].promptQuestions?.slice(0, 2).map((question: string, idx: number) => (
                          <li key={idx} className="text-gray-600 dark:text-gray-300">
                            {question}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function SmartQuestionsSection({ premiumContent }: { premiumContent?: any }) {
  const premiumCoaching = (premiumContent as any)?.premiumCoaching
  
  if (!premiumCoaching?.smartQuestions) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Smart Questions to Ask Interviewer</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600 dark:text-gray-300">
            Premium smart questions guidance will be available soon.
          </p>
        </CardContent>
      </Card>
    )
  }

  const { strategicQuestions, roleSpecificQuestions, companyIntelQuestions } = premiumCoaching.smartQuestions

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <HelpCircle className="w-5 h-5" />
            Smart Questions to Ask Your Interviewer
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600 dark:text-gray-300 mb-6">
            Demonstrate your strategic thinking and genuine interest with these thoughtfully crafted questions.
          </p>
          
          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-semibold mb-4">Strategic Questions</h3>
              <div className="space-y-4">
                {strategicQuestions?.map((category: any, idx: number) => (
                  <Card key={idx} className="border-l-4 border-l-blue-500">
                    <CardHeader>
                      <CardTitle className="text-lg">{category.category}</CardTitle>
                      <p className="text-sm text-gray-600 dark:text-gray-300">
                        Purpose: {category.purpose}
                      </p>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div>
                        <h5 className="font-medium text-sm mb-2">Questions to Ask:</h5>
                        <ul className="list-disc list-inside text-sm space-y-1">
                          {category.questions?.map((question: string, qIdx: number) => (
                            <li key={qIdx} className="text-gray-700 dark:text-gray-300">
                              {question}
                            </li>
                          ))}
                        </ul>
                      </div>
                      
                      <div>
                        <h5 className="font-medium text-sm mb-2">Best Timing:</h5>
                        <p className="text-sm text-gray-600 dark:text-gray-300">{category.timing}</p>
                      </div>
                      
                      {category.redFlags && (
                        <div>
                          <h5 className="font-medium text-sm mb-2">Red Flags to Watch For:</h5>
                          <ul className="list-disc list-inside text-xs space-y-1">
                            {category.redFlags.map((flag: string, fIdx: number) => (
                              <li key={fIdx} className="text-red-600 dark:text-red-400">
                                {flag}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-xl font-semibold mb-4">Role-Specific Questions</h3>
              <div className="space-y-4">
                {roleSpecificQuestions?.map((roleQuestions: any, idx: number) => (
                  <Card key={idx} className="border-l-4 border-l-green-500">
                    <CardHeader>
                      <CardTitle className="text-lg">{roleQuestions.role} Questions</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div>
                        <h5 className="font-medium text-sm mb-2">Questions:</h5>
                        <ul className="list-disc list-inside text-sm space-y-1">
                          {roleQuestions.questions?.map((question: string, qIdx: number) => (
                            <li key={qIdx} className="text-gray-700 dark:text-gray-300">
                              {question}
                            </li>
                          ))}
                        </ul>
                      </div>
                      
                      <div>
                        <h5 className="font-medium text-sm mb-2">Business Impact:</h5>
                        <p className="text-sm text-gray-600 dark:text-gray-300">{roleQuestions.businessImpact}</p>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function BrandingSection({ premiumContent }: { premiumContent?: any }) {
  const premiumCoaching = (premiumContent as any)?.premiumCoaching
  
  if (!premiumCoaching?.personalBranding) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Personal Branding Guide</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600 dark:text-gray-300">
            Premium personal branding guidance will be available soon.
          </p>
        </CardContent>
      </Card>
    )
  }

  const { brandArchetype, digitalPresence, storytellingFramework, executiveCommunication } = premiumCoaching.personalBranding

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Star className="w-5 h-5" />
            Personal Brand Strategy
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600 dark:text-gray-300 mb-6">
            Build a compelling personal brand that differentiates you from other candidates.
          </p>
          
          <div className="space-y-6">
            <Card className="border-l-4 border-l-purple-500">
              <CardHeader>
                <CardTitle className="text-lg">Your Brand Archetype: {brandArchetype?.primaryArchetype}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <h5 className="font-medium text-sm mb-2">Key Characteristics:</h5>
                  <div className="flex flex-wrap gap-2">
                    {brandArchetype?.characteristics?.map((char: string, idx: number) => (
                      <Badge key={idx} variant="secondary">{char}</Badge>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h5 className="font-medium text-sm mb-2">Messaging Tone:</h5>
                  <p className="text-sm text-gray-600 dark:text-gray-300">{brandArchetype?.messagingTone}</p>
                </div>
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-blue-500">
              <CardHeader>
                <CardTitle className="text-lg">Digital Presence Optimization</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <h5 className="font-medium text-sm mb-2">LinkedIn Optimization:</h5>
                  <ul className="list-disc list-inside text-sm space-y-1">
                    {digitalPresence?.linkedinOptimization?.slice(0, 3).map((tip: string, idx: number) => (
                      <li key={idx} className="text-gray-700 dark:text-gray-300">{tip}</li>
                    ))}
                  </ul>
                </div>
                
                <div>
                  <h5 className="font-medium text-sm mb-2">Thought Leadership:</h5>
                  <ul className="list-disc list-inside text-sm space-y-1">
                    {digitalPresence?.thoughtLeadership?.slice(0, 3).map((tip: string, idx: number) => (
                      <li key={idx} className="text-gray-700 dark:text-gray-300">{tip}</li>
                    ))}
                  </ul>
                </div>
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-green-500">
              <CardHeader>
                <CardTitle className="text-lg">Your Professional Story</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <h5 className="font-medium text-sm mb-2">Origin Story:</h5>
                  <p className="text-sm text-gray-600 dark:text-gray-300">{storytellingFramework?.originStory}</p>
                </div>
                
                <div>
                  <h5 className="font-medium text-sm mb-2">Future Vision:</h5>
                  <p className="text-sm text-gray-600 dark:text-gray-300">{storytellingFramework?.futureBio}</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function PreparationSection({ guide }: { guide: ComprehensiveGuide }) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Preparation Tips</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {guide.preparation?.tips?.length ? (
              guide.preparation.tips.map((tip, idx) => (
                <div key={idx} className="border-l-4 border-blue-500 pl-4 py-2">
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-1">{tip.title}</h4>
                  <p className="text-gray-600 dark:text-gray-300 text-sm">{tip.description}</p>
                </div>
              ))
            ) : (
              <p className="text-gray-600 dark:text-gray-300">
                Preparation tips will be customized based on your specific role and experience.
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Study Plan</CardTitle>
        </CardHeader>
        <CardContent>
          <ReactMarkdown className="prose prose-sm dark:prose-invert max-w-none">
            {guide.preparation?.studyPlan || 'A personalized study plan will be generated based on your interview timeline and the specific role requirements.'}
          </ReactMarkdown>
        </CardContent>
      </Card>
    </div>
  )
}

function ResourcesSection({ guide }: { guide: ComprehensiveGuide }) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Frequently Asked Questions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <h4 className="font-semibold mb-2">Salary Information</h4>
            <ReactMarkdown className="prose prose-sm dark:prose-invert max-w-none">
              {guide.faqs?.salary || 'Salary information will be researched based on the specific role and location.'}
            </ReactMarkdown>
          </div>
          <Separator />
          <div>
            <h4 className="font-semibold mb-2">Interview Experiences</h4>
            <ReactMarkdown className="prose prose-sm dark:prose-invert max-w-none">
              {guide.faqs?.experiences || 'Interview experiences from similar roles will be compiled.'}
            </ReactMarkdown>
          </div>
          <Separator />
          <div>
            <h4 className="font-semibold mb-2">Job Postings</h4>
            <ReactMarkdown className="prose prose-sm dark:prose-invert max-w-none">
              {guide.faqs?.jobPostings || 'Related job postings and requirements will be analyzed.'}
            </ReactMarkdown>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Additional Resources</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h4 className="font-semibold mb-2">Learning Resources</h4>
            {guide.conclusion?.resources ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {Object.entries(guide.conclusion.resources).map(([key, resource]) => (
                  <a
                    key={key}
                    href={resource.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-gray-900 dark:text-white">
                        {resource.title}
                      </span>
                      <ExternalLink className="w-4 h-4 text-gray-400" />
                    </div>
                  </a>
                ))}
              </div>
            ) : (
              <p className="text-gray-600 dark:text-gray-300">
                Curated learning resources will be provided based on the role requirements.
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Conclusion</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-700 dark:text-gray-300 mb-4">
            {guide.conclusion?.summary || 'Your personalized interview preparation guide has been tailored to help you succeed in your upcoming interviews.'}
          </p>
          
          <div className="bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 mt-0.5" />
              <div>
                <p className="font-medium text-green-800 dark:text-green-200 mb-2">
                  You're Ready to Excel!
                </p>
                <p className="text-sm text-green-700 dark:text-green-300">
                  With personalized questions, company insights, and strategic preparation tips, 
                  you have everything needed to make a strong impression. Remember: confidence 
                  comes from preparation, and you're now well-prepared.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function CompanyResearchSection({ premiumContent }: { premiumContent?: any }) {
  if (!premiumContent?.companyResearch) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Company Research Guide</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600 dark:text-gray-300">
            Premium company research guide will be available soon.
          </p>
        </CardContent>
      </Card>
    )
  }

  const { researchAreas, networkingStrategy } = premiumContent.companyResearch

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building className="w-5 h-5" />
            Enhanced Company Research Guide
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600 dark:text-gray-300 mb-6">
            Comprehensive research framework to understand the company's culture, market position, and strategic direction.
          </p>
          
          <div className="space-y-4">
            {researchAreas?.map((area: any, idx: number) => (
              <Card key={idx} className="border-l-4 border-l-purple-500">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{area.area}</CardTitle>
                    <div className="flex items-center gap-2">
                      <Badge variant={area.importance === 'Critical' ? 'destructive' : area.importance === 'High' ? 'default' : 'secondary'}>
                        {area.importance}
                      </Badge>
                      <span className="text-sm text-gray-500">{area.timeInvestment}</span>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <h5 className="font-medium text-sm mb-1">Key Research Questions:</h5>
                    <ul className="list-disc list-inside text-xs space-y-1">
                      {area.keyQuestions?.map((question: string, qIdx: number) => (
                        <li key={qIdx} className="text-gray-600 dark:text-gray-300">
                          {question}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div>
                    <h5 className="font-medium text-sm mb-1">Sources:</h5>
                    <div className="flex flex-wrap gap-1">
                      {area.sources?.map((source: string, sIdx: number) => (
                        <Badge key={sIdx} variant="outline" className="text-xs">
                          {source}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h5 className="font-medium text-sm mb-1">Talking Points:</h5>
                    <ul className="list-disc list-inside text-xs space-y-1">
                      {area.talkingPoints?.slice(0, 2).map((point: string, pIdx: number) => (
                        <li key={pIdx} className="text-gray-600 dark:text-gray-300">
                          {point}
                        </li>
                      ))}
                    </ul>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Network className="w-5 h-5" />
            Strategic Networking Approach
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h4 className="font-semibold text-gray-900 dark:text-white mb-2">LinkedIn Strategy</h4>
            <p className="text-sm text-gray-600 dark:text-gray-300">
              {networkingStrategy?.linkedinApproach}
            </p>
          </div>
          
          <div>
            <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Informational Interviews</h4>
            <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-300 space-y-1">
              {networkingStrategy?.informationalInterviews?.map((tip: string, idx: number) => (
                <li key={idx}>{tip}</li>
              ))}
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Insider Tips</h4>
            <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-300 space-y-1">
              {networkingStrategy?.insiderTips?.map((tip: string, idx: number) => (
                <li key={idx}>{tip}</li>
              ))}
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* Community Engagement */}
      <Card className="border-2 border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950/20">
        <CardContent className="p-6 text-center">
          <div className="flex justify-center mb-4">
            <MessageSquare className="w-8 h-8 text-blue-600 dark:text-blue-400" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Join the Community Building This
          </h3>
          <p className="text-gray-600 dark:text-gray-300 mb-6 max-w-2xl mx-auto">
            This tool gets better with every user. Share your interview experience, suggest features, 
            or just let us know how your prep went. Your input directly shapes what we build next.
          </p>
          
          <div className="flex justify-center gap-4">
            <Button 
              variant="default"
              className="bg-indigo-600 hover:bg-indigo-700"
              onClick={() => window.open('https://discord.gg/sEAEu6abdn', '_blank')}
            >
              Join Discord
            </Button>
            <Button 
              variant="outline"
              onClick={() => window.open('https://github.com/Avikalp-Karrahe/IQKiller', '_blank')}
            >
              <Github className="w-4 h-4 mr-2" />
              Star on GitHub
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function GeneratingGuideLoader() {
  return (
    <div className="w-full max-w-5xl mx-auto space-y-6">
      <Card>
        <CardContent className="p-8 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h3 className="text-lg font-semibold mb-2">Generating Your Interview Guide</h3>
          <p className="text-gray-600 dark:text-gray-300">
            Creating personalized questions, researching company insights, and building your comprehensive preparation guide...
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

 
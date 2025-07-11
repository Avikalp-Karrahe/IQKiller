'use client'

import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'

interface AnalysisResult {
  matchScore: number
  technicalSkills: string[]
  softSkills: string[]
  matchingSkills: string[]
  interviewQuestions: Array<{
    category: 'technical' | 'behavioral' | 'culture'
    question: string
  }>
  recommendations: string[]
}

interface InterviewAnalysisProps {
  analysis: AnalysisResult
}

export function InterviewAnalysis({ analysis }: InterviewAnalysisProps) {
  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-green-600'
    if (score >= 70) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreLabel = (score: number) => {
    if (score >= 85) return '🟢 Excellent Match'
    if (score >= 70) return '🟡 Strong Match'
    return '🔴 Developing Match'
  }

  return (
    <div className="space-y-6">
      {/* Match Score */}
      <Card>
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-bold">
            <span className={getScoreColor(analysis.matchScore)}>
              {analysis.matchScore}%
            </span>
          </CardTitle>
          <CardDescription className="text-lg">
            {getScoreLabel(analysis.matchScore)}
          </CardDescription>
          <Progress value={analysis.matchScore} className="w-full mt-4" />
        </CardHeader>
      </Card>

      {/* Skills Analysis */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Technical Skills Match</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {analysis.matchingSkills.slice(0, 8).map((skill, index) => (
                <Badge key={index} variant="secondary" className="mr-2 mb-2">
                  {skill}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Recommendations</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {analysis.recommendations.slice(0, 4).map((rec, index) => (
                <li key={index} className="text-sm text-gray-600 flex items-start">
                  <span className="text-blue-500 mr-2">•</span>
                  {rec}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* Interview Questions */}
      <Card>
        <CardHeader>
          <CardTitle>Essential Interview Questions</CardTitle>
          <CardDescription>
            Practice these questions to ace your interview
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {['technical', 'behavioral', 'culture'].map((category) => {
              const questions = analysis.interviewQuestions.filter(q => q.category === category)
              if (questions.length === 0) return null
              
              return (
                <div key={category}>
                  <h4 className="font-semibold capitalize mb-2 text-sm">
                    {category} Questions
                  </h4>
                  <div className="space-y-2">
                    {questions.slice(0, 2).map((q, index) => (
                      <div key={index} className="p-3 bg-gray-50 rounded-md text-sm">
                        {q.question}
                      </div>
                    ))}
                  </div>
                  {category !== 'culture' && <Separator className="mt-4" />}
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 
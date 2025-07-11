'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import StreamingAnalysis from '@/components/streaming-analysis'

export default function StreamingDemoPage() {
  const [resumeText, setResumeText] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [showAnalysis, setShowAnalysis] = useState(false)

  const sampleResume = `John Smith
Software Engineer | 5+ years experience

SKILLS:
• Programming: Python, JavaScript, TypeScript, Java
• Frameworks: React, Next.js, Django, FastAPI
• Databases: PostgreSQL, MongoDB, Redis
• Cloud: AWS (EC2, S3, Lambda), Docker, Kubernetes
• Machine Learning: TensorFlow, PyTorch, Scikit-learn

EXPERIENCE:
Senior Software Engineer @ TechCorp (2021-2024)
• Led development of microservices architecture serving 1M+ users
• Implemented ML recommendation system improving user engagement by 35%
• Mentored 3 junior developers and established code review processes

Software Engineer @ StartupXYZ (2019-2021)
• Built full-stack web applications using React and Python
• Developed RESTful APIs and integrated third-party services
• Optimized database queries reducing response time by 60%

EDUCATION:
B.S. Computer Science, University of California (2019)`

  const sampleJob = `Senior Machine Learning Engineer
Location: San Francisco, CA | Remote

We're looking for a Senior ML Engineer to join our AI team building next-generation recommendation systems.

REQUIREMENTS:
• 5+ years of software engineering experience
• 3+ years of machine learning experience
• Strong programming skills in Python
• Experience with TensorFlow, PyTorch, or similar ML frameworks
• Knowledge of recommendation systems and NLP
• Experience with cloud platforms (AWS, GCP, or Azure)
• Strong understanding of software engineering best practices

NICE TO HAVE:
• Experience with Kubernetes and containerization
• Knowledge of MLOps and model deployment
• Experience with large-scale distributed systems
• Background in deep learning and neural networks

RESPONSIBILITIES:
• Design and implement ML models for recommendation systems
• Collaborate with data scientists and product teams
• Build scalable ML infrastructure and pipelines
• Mentor junior team members
• Drive technical decisions and architecture choices`

  const handleStartDemo = () => {
    if (!resumeText.trim() || !jobDescription.trim()) {
      alert('Please provide both resume and job description')
      return
    }
    setShowAnalysis(true)
  }

  const loadSampleData = () => {
    setResumeText(sampleResume)
    setJobDescription(sampleJob)
  }

  if (showAnalysis) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto py-8">
          <div className="mb-6">
            <Button 
              onClick={() => setShowAnalysis(false)} 
              variant="outline"
            >
              ← Back to Setup
            </Button>
          </div>
          <StreamingAnalysis 
            resumeText={resumeText}
            jobDescription={jobDescription}
            onComplete={(result) => {
              console.log('Analysis completed:', result)
            }}
          />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto py-8 px-4">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              🎯 IQKiller Streaming Demo
            </h1>
            <p className="text-xl text-gray-600 mb-6">
              Experience real-time AI analysis that breaks through Vercel's 10-second limit
            </p>
            <div className="flex justify-center space-x-4">
              <div className="bg-green-100 text-green-800 px-4 py-2 rounded-lg">
                ✅ Serverless Compatible
              </div>
              <div className="bg-blue-100 text-blue-800 px-4 py-2 rounded-lg">
                ⚡ Real-time Updates
              </div>
              <div className="bg-purple-100 text-purple-800 px-4 py-2 rounded-lg">
                🚀 2+ Minute Analysis
              </div>
            </div>
          </div>

          {/* Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <Card className="border-red-200">
              <CardHeader>
                <CardTitle className="text-red-600">❌ Gradio (Current)</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  <li>• 2 minutes = timeout crash</li>
                  <li>• No progress feedback</li>
                  <li>• Server keeps crashing</li>
                  <li>• Won't work on Vercel</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-green-200">
              <CardHeader>
                <CardTitle className="text-green-600">✅ Streaming (New)</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  <li>• Real-time progress updates</li>
                  <li>• Results appear instantly</li>
                  <li>• Serverless compatible</li>
                  <li>• Perfect for Vercel</li>
                </ul>
              </CardContent>
            </Card>
          </div>

          {/* Input Form */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <Card>
              <CardHeader>
                <CardTitle>📄 Resume/CV Text</CardTitle>
                <CardDescription>
                  Paste your resume content or use the sample data
                </CardDescription>
              </CardHeader>
              <CardContent>
                <textarea
                  placeholder="Paste your resume text here..."
                  value={resumeText}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setResumeText(e.target.value)}
                  className="w-full min-h-[300px] text-sm p-3 border border-gray-300 rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>💼 Job Description</CardTitle>
                <CardDescription>
                  Paste the job posting you're applying for
                </CardDescription>
              </CardHeader>
              <CardContent>
                <textarea
                  placeholder="Paste job description here..."
                  value={jobDescription}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setJobDescription(e.target.value)}
                  className="w-full min-h-[300px] text-sm p-3 border border-gray-300 rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </CardContent>
            </Card>
          </div>

          {/* Action Buttons */}
          <div className="text-center space-y-4">
            <div className="space-x-4">
              <Button 
                onClick={loadSampleData}
                variant="outline"
                size="lg"
              >
                📋 Load Sample Data
              </Button>
              <Button 
                onClick={handleStartDemo}
                size="lg"
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                disabled={!resumeText.trim() || !jobDescription.trim()}
              >
                🚀 Start Streaming Analysis
              </Button>
            </div>
            
            <p className="text-sm text-gray-500">
              This demo will show you how streaming responses solve the 2-minute analysis problem
            </p>
          </div>

          {/* Features Preview */}
          <div className="mt-12">
            <h2 className="text-2xl font-bold text-center mb-8">What You'll Experience</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="pt-6 text-center">
                  <div className="text-2xl mb-2">🧠</div>
                  <h3 className="font-semibold">Resume Analysis</h3>
                  <p className="text-sm text-gray-600">Skills extraction & parsing</p>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="pt-6 text-center">
                  <div className="text-2xl mb-2">🎯</div>
                  <h3 className="font-semibold">Job Matching</h3>
                  <p className="text-sm text-gray-600">Compatibility scoring</p>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="pt-6 text-center">
                  <div className="text-2xl mb-2">❓</div>
                  <h3 className="font-semibold">Live Questions</h3>
                  <p className="text-sm text-gray-600">Real-time generation</p>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="pt-6 text-center">
                  <div className="text-2xl mb-2">📊</div>
                  <h3 className="font-semibold">Final Report</h3>
                  <p className="text-sm text-gray-600">Comprehensive guide</p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 
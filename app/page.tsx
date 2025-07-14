'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { HeaderControls } from '@/components/ui/header-controls'
import { Upload, FileText, Globe, Sparkles, Target, Brain, Trophy, Users, CheckCircle, Clock, Loader, Calendar, Zap } from 'lucide-react'
import StreamingAnalysis from '@/components/streaming-analysis'
import { FileUpload } from '@/components/file-upload'
import { JobAnalysis } from '@/components/job-analysis'
import { track } from '@vercel/analytics'

// Feature flags for IQKiller
const FEATURE_FLAGS = {
  PREMIUM_FEATURES_ENABLED: 'premium-features-enabled',
  AI_MODEL_VERSION: 'ai-model-version',
  QUESTION_GENERATION_V2: 'question-generation-v2',
  CUSTOM_COMPANY_RESEARCH: 'custom-company-research',
  ADVANCED_RESUME_PARSING: 'advanced-resume-parsing'
}

// Emit feature flags to DOM for Web Analytics
const emitFeatureFlags = () => {
  if (typeof window !== 'undefined') {
    // Set feature flags as data attributes on the body
    document.body.setAttribute('data-flag-premium-features-enabled', 'true')
    document.body.setAttribute('data-flag-ai-model-version', 'gpt-4')
    document.body.setAttribute('data-flag-question-generation-v2', 'true')
    document.body.setAttribute('data-flag-custom-company-research', 'true')
    document.body.setAttribute('data-flag-advanced-resume-parsing', 'true')
  }
}

// Countdown Timer Component
function CountdownTimer({ targetDate, title, isHovered }: { targetDate: Date; title: string; isHovered: boolean }) {
  const [timeLeft, setTimeLeft] = useState({ days: 0, hours: 0, minutes: 0, seconds: 0 })
  const [isAccelerating, setIsAccelerating] = useState(false)
  const dayCounterRef = useRef(0)

  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date().getTime()
      const distance = targetDate.getTime() - now

      if (distance > 0) {
        const newTimeLeft = {
          days: Math.floor(distance / (1000 * 60 * 60 * 24)),
          hours: Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
          minutes: Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60)),
          seconds: Math.floor((distance % (1000 * 60)) / 1000)
        }
        
        if (isHovered && !isAccelerating) {
          setIsAccelerating(true)
                     // Start cascading countdown with gradual decreasing
           const accelerate = () => {
             setTimeLeft(current => {
               if (current.seconds > 0) {
                 return { ...current, seconds: Math.max(0, current.seconds - 1) }
               } else if (current.minutes > 0) {
                 return { ...current, minutes: Math.max(0, current.minutes - 1) }
               } else if (current.hours > 0) {
                 return { ...current, hours: Math.max(0, current.hours - 1) }
               } else if (current.days > 0) {
                 return { ...current, days: Math.max(0, current.days - 1) }
               }
               return current
             })
           }
          
                     // Run acceleration with different speeds for different units
           const accelInterval = setInterval(() => {
             setTimeLeft(current => {
               if (current.seconds > 0) {
                 return { ...current, seconds: Math.max(0, current.seconds - 1) }
               } else if (current.minutes > 0) {
                 return { ...current, minutes: Math.max(0, current.minutes - 1) }
               } else if (current.hours > 0) {
                 return { ...current, hours: Math.max(0, current.hours - 1) }
               } else if (current.days > 0) {
                 // Slow down days - only decrease every 5th call (500ms)
                 dayCounterRef.current += 1
                 if (dayCounterRef.current >= 5) {
                   dayCounterRef.current = 0
                   return { ...current, days: Math.max(0, current.days - 1) }
                 }
               }
               return current
             })
           }, 100)
           setTimeout(() => {
             clearInterval(accelInterval)
             setIsAccelerating(false)
           }, 10000) // Stop after 10 seconds
        } else if (!isHovered) {
          setTimeLeft(newTimeLeft)
          setIsAccelerating(false)
        } else if (!isAccelerating) {
          setTimeLeft(newTimeLeft)
        }
      } else {
        setTimeLeft({ days: 0, hours: 0, minutes: 0, seconds: 0 })
        setIsAccelerating(false)
      }
    }, 1000) // Update every second

    return () => clearInterval(timer)
  }, [targetDate, isHovered, isAccelerating])

  const isReleased = timeLeft.days === 0 && timeLeft.hours === 0 && timeLeft.minutes === 0 && timeLeft.seconds === 0

  // Calculate dynamic date based on current countdown
  const getDynamicDate = () => {
    const currentDate = new Date()
    const daysFromNow = timeLeft.days
    const futureDate = new Date(currentDate.getTime() + (daysFromNow * 24 * 60 * 60 * 1000))
    
    const months = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    const month = months[futureDate.getMonth()]
    const day = futureDate.getDate()
    
    // Add ordinal suffix (st, nd, rd, th)
    const getOrdinalSuffix = (day: number) => {
      if (day > 3 && day < 21) return 'th'
      switch (day % 10) {
        case 1: return 'st'
        case 2: return 'nd'
        case 3: return 'rd'
        default: return 'th'
      }
    }
    
    return `${month} ${day}${getOrdinalSuffix(day)}`
  }

  return (
    <div className="space-y-3">
      {isReleased ? (
        <div className="flex items-center justify-center">
          <button 
            onClick={() => window.open('https://www.linkedin.com/in/avikalp/', '_blank')}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors duration-200"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
            </svg>
            Connect
          </button>
        </div>
      ) : (
        <>
          <div className="text-xs text-amber-600 dark:text-amber-400 font-medium">
            {isHovered 
              ? `Releases ${getDynamicDate()} (ACCELERATING!)` 
              : `Releases ${title}`
            }
          </div>
          <div className="grid grid-cols-4 gap-2 text-xs">
            <div className="text-center">
              <div className={`font-bold text-amber-600 dark:text-amber-400 ${isHovered ? 'animate-pulse' : ''}`}>{timeLeft.days}</div>
              <div className="text-gray-500 dark:text-gray-400">days</div>
            </div>
            <div className="text-center">
              <div className={`font-bold text-amber-600 dark:text-amber-400 ${isHovered ? 'animate-pulse' : ''}`}>{timeLeft.hours}</div>
              <div className="text-gray-500 dark:text-gray-400">hrs</div>
            </div>
            <div className="text-center">
              <div className={`font-bold text-amber-600 dark:text-amber-400 ${isHovered ? 'animate-pulse' : ''}`}>{timeLeft.minutes}</div>
              <div className="text-gray-500 dark:text-gray-400">min</div>
            </div>
            <div className="text-center">
              <div className={`font-bold text-amber-600 dark:text-amber-400 ${isHovered ? 'animate-pulse' : ''}`}>{timeLeft.seconds}</div>
              <div className="text-gray-500 dark:text-gray-400">sec</div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default function IQKillerMainPage() {
  const [resumeText, setResumeText] = useState('')
  const [jobData, setJobData] = useState<any>(null)
  const [showAnalysis, setShowAnalysis] = useState(false)

  const [analysisComplete, setAnalysisComplete] = useState(false)
  
  // Parallel processing states
  const [resumeAnalysisStatus, setResumeAnalysisStatus] = useState<'idle' | 'processing' | 'completed' | 'error'>('idle')
  const [jobAnalysisStatus, setJobAnalysisStatus] = useState<'idle' | 'processing' | 'completed' | 'error'>('idle')
  const [resumeAnalysisData, setResumeAnalysisData] = useState<any>(null)
  const [jobAnalysisData, setJobAnalysisData] = useState<any>(null)
  
  // Background comprehensive analysis states
  const [comprehensiveAnalysisStatus, setComprehensiveAnalysisStatus] = useState<'idle' | 'processing' | 'completed' | 'error'>('idle')
  const [comprehensiveAnalysisData, setComprehensiveAnalysisData] = useState<any>(null)

  // Hover states for feature cards
  const [card1Hovered, setCard1Hovered] = useState(false)
  const [card2Hovered, setCard2Hovered] = useState(false)
  const [card3Hovered, setCard3Hovered] = useState(false)

  // Emit feature flags on component mount
  useEffect(() => {
    emitFeatureFlags()
  }, [])

  // Handle resume upload and immediately start analysis
  const handleResumeUpload = async (text: string) => {
    // Track resume upload event
    track('Resume Upload', {
      hasContent: text.length > 0,
      contentLength: text.length,
      source: 'file_upload',
      timestamp: new Date().toISOString()
    }, { 
      flags: [
        FEATURE_FLAGS.ADVANCED_RESUME_PARSING,
        FEATURE_FLAGS.AI_MODEL_VERSION
      ]
    })
    
    setResumeText(text)
    
    // Start resume analysis immediately
    if (text.trim()) {
      setResumeAnalysisStatus('processing')
      
      try {
        console.log('🚀 Starting immediate resume analysis...')
        const response = await fetch('/api/analyze-resume', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ resumeText: text })
        })

        if (!response.ok) {
          // Track failed resume analysis
          track('Resume Analysis Failed', {
            error: response.statusText,
            contentLength: text.length,
            timestamp: new Date().toISOString()
          }, { 
            flags: [
              FEATURE_FLAGS.ADVANCED_RESUME_PARSING,
              FEATURE_FLAGS.AI_MODEL_VERSION
            ]
          })
          throw new Error(`Resume analysis failed: ${response.statusText}`)
        }

        const data = await response.json()
        console.log('✅ Resume analysis completed:', data)
        
        // Extract resume data from the nested structure
        const resumeData = data.data?.resumeData || data.resumeData
        
        // Ensure we have proper data before proceeding
        if (!resumeData || !resumeData.name) {
          console.warn('⚠️ Resume data incomplete:', resumeData)
          console.warn('⚠️ Raw response data:', data)
          // Try to extract from different response structures
          const fallbackData = data.resumeData || data.data || data
          if (fallbackData && fallbackData.name) {
            console.log('✅ Using fallback data extraction')
            setResumeAnalysisData(fallbackData)
            setResumeAnalysisStatus('completed')
            return
          }
          throw new Error('Incomplete resume analysis data received')
        }
        
        // Track successful resume analysis
        track('Resume Analysis Completed', {
          name: resumeData?.name || 'Unknown',
          experienceYears: resumeData?.experienceYears || 0,
          contentLength: text.length,
          timestamp: new Date().toISOString()
        }, { 
          flags: [
            FEATURE_FLAGS.ADVANCED_RESUME_PARSING,
            FEATURE_FLAGS.AI_MODEL_VERSION
          ]
        })
        
        setResumeAnalysisData(resumeData)
        setResumeAnalysisStatus('completed')
      } catch (error) {
        console.error('❌ Resume analysis failed:', error)
        track('Resume Analysis Error', {
          error: error instanceof Error ? error.message : 'Unknown error',
          contentLength: text.length,
          timestamp: new Date().toISOString()
        }, { 
          flags: [
            FEATURE_FLAGS.ADVANCED_RESUME_PARSING,
            FEATURE_FLAGS.AI_MODEL_VERSION
          ]
        })
        setResumeAnalysisStatus('error')
      }
    }
  }

  // Handle job data and immediately start job analysis
  const handleJobData = async (data: any) => {
    // Track job analysis initiation
    track('Job Analysis Started', {
      hasUrl: !!data.url,
      hasDescription: !!data.description,
      source: data.url ? 'url' : 'manual_input',
      contentLength: data.description?.length || 0,
      timestamp: new Date().toISOString()
    }, { 
      flags: [
        FEATURE_FLAGS.CUSTOM_COMPANY_RESEARCH,
        FEATURE_FLAGS.AI_MODEL_VERSION
      ]
    })
    
    setJobData(data)
    
    // Start job analysis immediately if we have meaningful job data
    if (data && (data.description || data.content || data.url)) {
      setJobAnalysisStatus('processing')
      
      try {
        console.log('🚀 Starting immediate job analysis...')
        const response = await fetch('/api/analyze-job', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ jobData: data })
        })

        if (!response.ok) {
          // Track failed job analysis
          track('Job Analysis Failed', {
            error: response.statusText,
            source: data.url ? 'url' : 'manual_input',
            timestamp: new Date().toISOString()
          }, { 
            flags: [
              FEATURE_FLAGS.CUSTOM_COMPANY_RESEARCH,
              FEATURE_FLAGS.AI_MODEL_VERSION
            ]
          })
          throw new Error(`Job analysis failed: ${response.statusText}`)
        }

        const analysisData = await response.json()
        console.log('✅ Job analysis completed:', analysisData)
        
        // Track successful job analysis
        track('Job Analysis Completed', {
          title: analysisData.jobAnalysis?.title || 'Unknown',
          company: analysisData.jobAnalysis?.company || 'Unknown',
          source: data.url ? 'url' : 'manual_input',
          timestamp: new Date().toISOString()
        }, { 
          flags: [
            FEATURE_FLAGS.CUSTOM_COMPANY_RESEARCH,
            FEATURE_FLAGS.AI_MODEL_VERSION
          ]
        })
        
        setJobAnalysisData(analysisData.jobAnalysis)
        setJobAnalysisStatus('completed')
      } catch (error) {
        console.error('❌ Job analysis failed:', error)
        track('Job Analysis Error', {
          error: error instanceof Error ? error.message : 'Unknown error',
          source: data.url ? 'url' : 'manual_input',
          timestamp: new Date().toISOString()
        }, { 
          flags: [
            FEATURE_FLAGS.CUSTOM_COMPANY_RESEARCH,
            FEATURE_FLAGS.AI_MODEL_VERSION
          ]
        })
        setJobAnalysisStatus('error')
      }
    }
  }

  const handleStartAnalysis = () => {
    if (!resumeText.trim() || !jobData) return
    
    // Track interview guide generation
    track('Interview Guide Generation Started', {
      hasPrecomputedResults: comprehensiveAnalysisReady && !!comprehensiveAnalysisData,
      resumeLength: resumeText.length,
      jobTitle: jobData.title || 'Unknown',
      timestamp: new Date().toISOString()
    }, { 
      flags: [
        FEATURE_FLAGS.PREMIUM_FEATURES_ENABLED,
        FEATURE_FLAGS.QUESTION_GENERATION_V2,
        FEATURE_FLAGS.AI_MODEL_VERSION
      ]
    })
    
    // If comprehensive analysis is already complete, show results immediately
    if (comprehensiveAnalysisReady && comprehensiveAnalysisData) {
      console.log('🚀 Using pre-computed comprehensive analysis results!')
      track('Interview Guide Displayed', {
        source: 'precomputed',
        jobTitle: jobData.title || 'Unknown',
        timestamp: new Date().toISOString()
      }, { 
        flags: [
          FEATURE_FLAGS.PREMIUM_FEATURES_ENABLED,
          FEATURE_FLAGS.QUESTION_GENERATION_V2,
          FEATURE_FLAGS.AI_MODEL_VERSION
        ]
      })
      setShowAnalysis(true)
      setAnalysisComplete(true)
    } else {
      // Start fresh analysis or wait for background analysis
      setShowAnalysis(true)
      setAnalysisComplete(false)
    }
  }

  // Start comprehensive analysis in background
  const startComprehensiveAnalysis = async () => {
    if (comprehensiveAnalysisStatus === 'processing') return // Already processing
    
    setComprehensiveAnalysisStatus('processing')
    
    try {
      console.log('🚀 Starting background comprehensive analysis...')
      const response = await fetch('/api/analyze-complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resumeText,
          jobDescription: jobData.description || JSON.stringify(jobData),
          jobData,
          resumeAnalysisData,
          jobAnalysisData
        })
      })

      if (!response.ok) {
        throw new Error(`Comprehensive analysis failed: ${response.statusText}`)
      }

      const data = await response.json()
      console.log('✅ Background comprehensive analysis completed:', data)
      
      setComprehensiveAnalysisData(data.results)
      setComprehensiveAnalysisStatus('completed')
    } catch (error) {
      console.error('❌ Background comprehensive analysis failed:', error)
      setComprehensiveAnalysisStatus('error')
    }
  }

  const handleAnalysisComplete = (result: any) => {
    setAnalysisComplete(true)
    console.log('Analysis completed:', result)
  }

  const canAnalyze = resumeText.trim() && jobData
  const bothAnalysesReady = resumeAnalysisStatus === 'completed' && jobAnalysisStatus === 'completed'
  const comprehensiveAnalysisReady = comprehensiveAnalysisStatus === 'completed'

  // Auto-start comprehensive analysis when both individual analyses are complete
  React.useEffect(() => {
    if (bothAnalysesReady && comprehensiveAnalysisStatus === 'idle' && resumeAnalysisData && jobAnalysisData) {
      console.log('🚀 Auto-starting comprehensive analysis in background...')
      startComprehensiveAnalysis()
    }
  }, [bothAnalysesReady, resumeAnalysisData, jobAnalysisData, comprehensiveAnalysisStatus, startComprehensiveAnalysis])

  return (
    <div className="gradient-bg min-h-screen">
      {/* Header Controls - Top Right - Single instance for both views */}
      <div className="absolute top-4 right-4 z-50">
        <HeaderControls />
      </div>

      {showAnalysis ? (
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <div className="text-center mb-8">
            <Button
              variant="outline"
              onClick={() => setShowAnalysis(false)}
              className="mb-4 glass-effect"
            >
              ← Start New Analysis
            </Button>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-50 mb-2">
              <span className="text-slate-800 dark:text-slate-200">IQ</span>
              <span className="text-blue-600 dark:text-blue-400">Killer</span> Analysis
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-300">
              Real-time AI-powered interview preparation
            </p>
          </div>

          {/* Enhanced Streaming Analysis with pre-processed data */}
          <div className="glass-effect rounded-xl p-6 shadow-lg">
            <StreamingAnalysis
              resumeText={resumeText}
              jobDescription={jobData.description || JSON.stringify(jobData)}
              jobData={jobData}
              resumeAnalysisData={resumeAnalysisData}
              jobAnalysisData={jobAnalysisData}
              preComputedResults={comprehensiveAnalysisData}
              onComplete={handleAnalysisComplete}
            />
          </div>
        </div>
      ) : (
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-4 py-2 glass-effect rounded-full text-sm font-medium mb-6">
              <Sparkles className="w-4 h-4" />
              AI-Powered Interview Preparation
            </div>
            <h1 className="text-6xl font-bold text-gray-900 dark:text-gray-50 mb-6">
              <span className="text-slate-800 dark:text-slate-200">IQ</span>
              <span className="text-blue-600 dark:text-blue-400">Killer</span>
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto mb-8 leading-relaxed">
              Upload your resume, analyze job postings, and get personalized interview questions, salary negotiation strategies, and real-time preparation insights powered by AI.
            </p>
            
            {/* Feature highlights */}
            <div className="flex items-center justify-center gap-8 text-gray-500 dark:text-gray-400 mb-12">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                <span className="text-sm">Resume Analysis</span>
              </div>
              <div className="flex items-center gap-2">
                <Globe className="w-5 h-5" />
                <span className="text-sm">Job Scraping</span>
              </div>
              <div className="flex items-center gap-2">
                <Brain className="w-5 h-5" />
                <span className="text-sm">Open Source</span>
              </div>
              <div className="flex items-center gap-2">
                <Target className="w-5 h-5" />
                <span className="text-sm">Strategy</span>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="max-w-6xl mx-auto">
            <div className="grid lg:grid-cols-2 gap-8 mb-12">
              {/* Resume Upload with Real-time Analysis */}
              <div className="card-gradient relative overflow-hidden border-0 shadow-lg rounded-xl bg-card text-card-foreground">
                <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-100/50 to-transparent rounded-full -mr-16 -mt-16"></div>
                <div className="flex flex-col space-y-1.5 p-6 relative">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
                      <Upload className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div className="flex-1">
                      <div className="font-semibold tracking-tight text-xl">Upload Your Resume</div>
                      <div className="text-sm text-muted-foreground">Resume analysis with AI-powered skills extraction</div>
                    </div>
                    {/* Resume Analysis Status */}
                    <div className="flex items-center gap-2">
                      {resumeAnalysisStatus === 'idle' && <Clock className="w-5 h-5 text-gray-400" />}
                      {resumeAnalysisStatus === 'processing' && <Loader className="w-5 h-5 text-blue-500 animate-spin" />}
                      {resumeAnalysisStatus === 'completed' && <CheckCircle className="w-5 h-5 text-green-500" />}
                      {resumeAnalysisStatus === 'error' && <div className="w-5 h-5 rounded-full bg-red-500" />}
                    </div>
                  </div>
                </div>
                <div className="p-6 pt-0 relative">
                  <div className="space-y-4">
                    <FileUpload onFileUpload={handleResumeUpload} />
                    {resumeAnalysisStatus === 'processing' && (
                      <div className="text-sm text-blue-600 font-medium">
                        🧠 Analyzing resume with AI...
                      </div>
                    )}
                    {resumeAnalysisStatus === 'completed' && (
                      <div className="text-sm text-green-600 font-medium">
                        ✅ Resume analysis completed: {resumeAnalysisData?.name} ({resumeAnalysisData?.experienceYears || 'N/A'} years)
                      </div>
                    )}
                    {resumeAnalysisStatus === 'error' && (
                      <div className="text-sm text-red-600 font-medium">
                        ❌ Resume analysis failed. Please try again.
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Job Analysis with Real-time Processing */}
              <div className="card-gradient relative overflow-hidden border-0 shadow-lg rounded-xl bg-card text-card-foreground">
                <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-purple-100/50 to-transparent rounded-full -mr-16 -mt-16"></div>
                <div className="flex flex-col space-y-1.5 p-6 relative">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
                      <Globe className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                    </div>
                    <div className="flex-1">
                      <div className="font-semibold tracking-tight text-xl">Job Analysis</div>
                      <div className="text-sm text-muted-foreground">Paste URL or job description for analysis</div>
                    </div>
                    {/* Job Analysis Status */}
                    <div className="flex items-center gap-2">
                      {jobAnalysisStatus === 'idle' && <Clock className="w-5 h-5 text-gray-400" />}
                      {jobAnalysisStatus === 'processing' && <Loader className="w-5 h-5 text-purple-500 animate-spin" />}
                      {jobAnalysisStatus === 'completed' && <CheckCircle className="w-5 h-5 text-green-500" />}
                      {jobAnalysisStatus === 'error' && <div className="w-5 h-5 rounded-full bg-red-500" />}
                    </div>
                  </div>
                </div>
                <div className="p-6 pt-0 relative">
                  <JobAnalysis onJobData={handleJobData} />
                  {jobAnalysisStatus === 'processing' && (
                    <div className="text-sm text-purple-600 font-medium mt-4">
                      🔍 Analyzing job posting...
                    </div>
                  )}
                  {jobAnalysisStatus === 'completed' && (
                    <div className="text-sm text-green-600 font-medium mt-4">
                      ✅ Job analysis completed: {jobAnalysisData?.title} at {jobAnalysisData?.company}
                    </div>
                  )}
                  {jobAnalysisStatus === 'error' && (
                    <div className="text-sm text-red-600 font-medium mt-4">
                      ❌ Job analysis failed. Please try again.
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Analysis Button */}
            {canAnalyze && (
              <div className="text-center mb-12">
                <Button
                  onClick={handleStartAnalysis}
                  disabled={!bothAnalysesReady}
                  className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white text-lg px-8 py-4 h-auto shadow-lg transition-all duration-200 disabled:opacity-50"
                >
                  {comprehensiveAnalysisReady ? (
                    <>
                      <Trophy className="w-5 h-5 mr-2" />
                      View Your Interview Guide (Ready!)
                    </>
                  ) : comprehensiveAnalysisStatus === 'processing' ? (
                    <>
                      <Loader className="w-5 h-5 mr-2 animate-spin" />
                      Generating Interview Guide...
                    </>
                  ) : bothAnalysesReady ? (
                    <>
                      <Sparkles className="w-5 h-5 mr-2" />
                      Generate Interview Guide
                    </>
                  ) : (
                    <>
                      <Clock className="w-5 h-5 mr-2" />
                      Waiting for analyses to complete...
                    </>
                  )}
                </Button>
                
                {/* Status Messages */}
                {comprehensiveAnalysisReady && (
                  <p className="text-sm text-green-600 mt-2 font-medium">
                    🎉 Your personalized interview guide is ready! Click to view.
                  </p>
                )}
                {comprehensiveAnalysisStatus === 'processing' && (
                  <p className="text-sm text-blue-600 mt-2">
                    🚀 Generating your comprehensive interview guide in the background...
                  </p>
                )}
                {bothAnalysesReady && comprehensiveAnalysisStatus === 'idle' && (
                  <p className="text-sm text-green-600 mt-2">
                    ✅ Both analyses complete - ready to generate your personalized interview guide!
                  </p>
                )}
              </div>
            )}

            {/* Feature Cards */}
            <div className="grid md:grid-cols-3 gap-6 mt-16">
              <div className="card-gradient text-center p-6 border-0 shadow-lg rounded-xl bg-card text-card-foreground relative overflow-hidden group h-72 flex flex-col"
                   onMouseEnter={() => setCard1Hovered(true)}
                   onMouseLeave={() => setCard1Hovered(false)}>
                {/* Premium gradient overlay */}
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-transparent to-purple-500/10 pointer-events-none"></div>
                {/* Coming Soon Badge */}
                <div className="absolute top-3 right-3 px-2 py-1 bg-gradient-to-r from-amber-400 to-orange-500 text-white text-xs font-semibold rounded-full shadow-lg">
                  Coming Soon
                </div>
                <div className="relative flex-1 flex flex-col">
                  <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <Brain className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-blue-600 dark:text-blue-400 mb-2">Smart Question Generation</h3>
                  <div className="flex-1 mb-4">
                    <p className="text-gray-600 dark:text-gray-300 text-sm group-hover:hidden">
                      AI-generated interview questions tailored to your resume and the specific job requirements.
                    </p>
                    <p className="text-blue-600 dark:text-blue-400 text-sm font-medium hidden group-hover:block cursor-pointer" onClick={() => window.open('https://www.linkedin.com/in/avikalp/', '_blank')}>
                      <span className="flex items-center justify-center">
                        <Zap className="w-4 h-4 mr-2" />
                        Wanna speed it up? Come build with us!
                      </span>
                    </p>
                  </div>
                  {/* Premium feature indicator */}
                  <CountdownTimer targetDate={new Date('2025-07-26')} title="July 26th" isHovered={card1Hovered} />
                </div>
              </div>
              
              <div className="card-gradient text-center p-6 border-0 shadow-lg rounded-xl bg-card text-card-foreground relative overflow-hidden group h-72 flex flex-col"
                   onMouseEnter={() => setCard2Hovered(true)}
                   onMouseLeave={() => setCard2Hovered(false)}>
                {/* Premium gradient overlay */}
                <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 via-transparent to-pink-500/10 pointer-events-none"></div>
                {/* Coming Soon Badge */}
                <div className="absolute top-3 right-3 px-2 py-1 bg-gradient-to-r from-amber-400 to-orange-500 text-white text-xs font-semibold rounded-full shadow-lg">
                  Coming Soon
                </div>
                <div className="relative flex-1 flex flex-col">
                  <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <Target className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-purple-600 dark:text-purple-400 mb-2">Skills Gap Analysis</h3>
                  <div className="flex-1 mb-4">
                    <p className="text-gray-600 dark:text-gray-300 text-sm group-hover:hidden">
                      Identify gaps between your skills and job requirements, with personalized learning recommendations.
                    </p>
                    <p className="text-purple-600 dark:text-purple-400 text-sm font-medium hidden group-hover:block cursor-pointer" onClick={() => window.open('https://www.linkedin.com/in/avikalp/', '_blank')}>
                      <span className="flex items-center justify-center">
                        <Zap className="w-4 h-4 mr-2" />
                        Wanna speed it up? Come build with us!
                      </span>
                    </p>
                  </div>
                  {/* Premium feature indicator */}
                  <CountdownTimer targetDate={new Date('2025-08-09')} title="August 9th" isHovered={card2Hovered} />
                </div>
              </div>
              
              <div className="card-gradient text-center p-6 border-0 shadow-lg rounded-xl bg-card text-card-foreground relative overflow-hidden group h-72 flex flex-col"
                   onMouseEnter={() => setCard3Hovered(true)}
                   onMouseLeave={() => setCard3Hovered(false)}>
                {/* Premium gradient overlay */}
                <div className="absolute inset-0 bg-gradient-to-br from-green-500/10 via-transparent to-emerald-500/10 pointer-events-none"></div>
                {/* Coming Soon Badge */}
                <div className="absolute top-3 right-3 px-2 py-1 bg-gradient-to-r from-amber-400 to-orange-500 text-white text-xs font-semibold rounded-full shadow-lg">
                  Coming Soon
                </div>
                <div className="relative flex-1 flex flex-col">
                  <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <Trophy className="w-6 h-6 text-green-600 dark:text-green-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-green-600 dark:text-green-400 mb-2">Salary Negotiation</h3>
                  <div className="flex-1 mb-4">
                    <p className="text-gray-600 dark:text-gray-300 text-sm group-hover:hidden">
                      AI-powered salary insights and negotiation strategies based on market data and your profile.
                    </p>
                    <p className="text-green-600 dark:text-green-400 text-sm font-medium hidden group-hover:block cursor-pointer" onClick={() => window.open('https://www.linkedin.com/in/avikalp/', '_blank')}>
                      <span className="flex items-center justify-center">
                        <Zap className="w-4 h-4 mr-2" />
                        Wanna speed it up? Come build with us!
                      </span>
                    </p>
                  </div>
                  {/* Premium feature indicator */}
                  <CountdownTimer targetDate={new Date('2025-08-23')} title="August 23rd" isHovered={card3Hovered} />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
} 
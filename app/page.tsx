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

  // Handle resume upload and immediately start analysis
  const handleResumeUpload = async (text: string) => {
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
          throw new Error(`Resume analysis failed: ${response.statusText}`)
        }

        const data = await response.json()
        console.log('✅ Resume analysis completed:', data)
        
        setResumeAnalysisData(data.resumeData)
        setResumeAnalysisStatus('completed')
      } catch (error) {
        console.error('❌ Resume analysis failed:', error)
        setResumeAnalysisStatus('error')
      }
    }
  }

  // Handle job data and immediately start job analysis
  const handleJobData = async (data: any) => {
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
          throw new Error(`Job analysis failed: ${response.statusText}`)
        }

        const analysisData = await response.json()
        console.log('✅ Job analysis completed:', analysisData)
        
        setJobAnalysisData(analysisData.jobAnalysis)
        setJobAnalysisStatus('completed')
      } catch (error) {
        console.error('❌ Job analysis failed:', error)
        setJobAnalysisStatus('error')
      }
    }
  }

  const handleStartAnalysis = () => {
    if (!resumeText.trim() || !jobData) return
    
    // If comprehensive analysis is already complete, show results immediately
    if (comprehensiveAnalysisReady && comprehensiveAnalysisData) {
      console.log('🚀 Using pre-computed comprehensive analysis results!')
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



  if (showAnalysis) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-slate-900 dark:via-slate-800 dark:to-indigo-900">
        {/* Enhanced animated background */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-blue-400/20 to-purple-600/20 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-br from-purple-400/20 to-pink-600/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-br from-indigo-400/10 to-cyan-600/10 rounded-full blur-3xl animate-pulse delay-2000"></div>
        </div>
        
        {/* Header Controls - Top Right */}
        <div className="absolute top-6 right-6 z-50">
          <HeaderControls />
        </div>
        
        <div className="relative z-10 container mx-auto px-4 py-8">
          {/* Enhanced Header */}
          <div className="text-center mb-12">
            <Button
              variant="outline"
              onClick={() => setShowAnalysis(false)}
              className="mb-6 backdrop-blur-sm bg-white/80 dark:bg-slate-800/80 border-white/20 dark:border-slate-700/30 hover:bg-white/90 dark:hover:bg-slate-700/90 transition-all duration-300 hover:scale-105 hover:shadow-lg"
            >
              ← Start New Analysis
            </Button>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-slate-800 via-blue-600 to-indigo-600 dark:from-slate-200 dark:via-blue-400 dark:to-indigo-400 bg-clip-text text-transparent mb-4">
              IQKiller Analysis
            </h1>
            <p className="text-xl text-slate-600 dark:text-slate-300 font-medium">
              Real-time AI-powered interview preparation
            </p>
          </div>

          {/* Enhanced Streaming Analysis */}
          <div className="backdrop-blur-sm bg-white/80 dark:bg-slate-800/80 rounded-2xl p-8 shadow-2xl border border-white/20 dark:border-slate-700/30 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 to-purple-50/50 dark:from-slate-800/50 dark:to-indigo-900/50 pointer-events-none"></div>
            <div className="relative z-10">
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
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-slate-900 dark:via-slate-800 dark:to-indigo-900 relative overflow-hidden">
      {/* Enhanced animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-blue-400/20 to-purple-600/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-br from-purple-400/20 to-pink-600/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-br from-indigo-400/10 to-cyan-600/10 rounded-full blur-3xl animate-pulse delay-2000"></div>
        
        {/* Floating particles */}
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-blue-400/40 rounded-full animate-bounce delay-300"></div>
        <div className="absolute top-3/4 right-1/4 w-3 h-3 bg-purple-400/40 rounded-full animate-bounce delay-700"></div>
        <div className="absolute bottom-1/4 left-1/3 w-2 h-2 bg-indigo-400/40 rounded-full animate-bounce delay-1100"></div>
      </div>
      
      {/* Header Controls - Top Right */}
      <div className="absolute top-6 right-6 z-50">
        <HeaderControls />
      </div>
      
      <div className="relative z-10 container mx-auto px-4 py-8">
        {/* Enhanced Header */}
        <div className="text-center mb-20">
          <div className="inline-flex items-center gap-2 px-6 py-3 backdrop-blur-sm bg-white/80 dark:bg-slate-800/80 border border-white/20 dark:border-slate-700/30 rounded-full text-sm font-semibold mb-8 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
            <Sparkles className="w-4 h-4 text-blue-500" />
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              AI-Powered Interview Preparation
            </span>
          </div>
          
          <h1 className="text-7xl font-bold bg-gradient-to-r from-slate-800 via-blue-600 to-indigo-600 dark:from-slate-200 dark:via-blue-400 dark:to-indigo-400 bg-clip-text text-transparent mb-8 tracking-tight">
            IQKiller
          </h1>
          
          <p className="text-xl text-slate-600 dark:text-slate-300 max-w-4xl mx-auto mb-10 leading-relaxed font-medium">
            Upload your resume, analyze job postings, and get personalized interview questions, salary negotiation strategies, and real-time preparation insights powered by AI.
          </p>
          
          {/* Enhanced feature highlights */}
          <div className="flex items-center justify-center gap-10 text-slate-500 dark:text-slate-400 mb-16">
            <div className="flex items-center gap-3 group cursor-pointer">
              <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg group-hover:bg-blue-200 dark:group-hover:bg-blue-800/50 transition-all duration-300">
                <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
              <span className="text-sm font-medium group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors duration-300">Resume Analysis</span>
            </div>
            <div className="flex items-center gap-3 group cursor-pointer">
              <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg group-hover:bg-purple-200 dark:group-hover:bg-purple-800/50 transition-all duration-300">
                <Globe className="w-5 h-5 text-purple-600 dark:text-purple-400" />
              </div>
              <span className="text-sm font-medium group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors duration-300">Job Scraping</span>
            </div>
            <div className="flex items-center gap-3 group cursor-pointer">
              <div className="p-2 bg-emerald-100 dark:bg-emerald-900/30 rounded-lg group-hover:bg-emerald-200 dark:group-hover:bg-emerald-800/50 transition-all duration-300">
                <Brain className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
              </div>
              <span className="text-sm font-medium group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors duration-300">Open Source</span>
            </div>
            <div className="flex items-center gap-3 group cursor-pointer">
              <div className="p-2 bg-amber-100 dark:bg-amber-900/30 rounded-lg group-hover:bg-amber-200 dark:group-hover:bg-amber-800/50 transition-all duration-300">
                <Target className="w-5 h-5 text-amber-600 dark:text-amber-400" />
              </div>
              <span className="text-sm font-medium group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors duration-300">Strategy</span>
            </div>
          </div>
        </div>

        {/* Enhanced Main Content */}
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-8 mb-16">
            {/* Enhanced Resume Upload Card */}
            <div className="group relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-purple-600/10 rounded-2xl blur-xl group-hover:blur-2xl transition-all duration-500"></div>
              <div className="relative backdrop-blur-sm bg-white/80 dark:bg-slate-800/80 border border-white/20 dark:border-slate-700/30 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-500 hover:scale-[1.02] overflow-hidden">
                <div className="absolute top-0 right-0 w-40 h-40 bg-gradient-to-br from-blue-100/50 to-purple-100/50 dark:from-blue-900/30 dark:to-purple-900/30 rounded-full -mr-20 -mt-20 group-hover:scale-110 transition-transform duration-500"></div>
                
                <div className="relative p-8">
                  <div className="flex items-center gap-4 mb-6">
                    <div className="p-3 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg group-hover:shadow-xl transition-all duration-300">
                      <Upload className="w-7 h-7 text-white" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-2xl font-bold text-slate-800 dark:text-slate-200 mb-1">Upload Your Resume</h3>
                      <p className="text-slate-600 dark:text-slate-400 font-medium">Resume analysis with AI-powered skills extraction</p>
                    </div>
                    {/* Enhanced Status Indicator */}
                    <div className="flex items-center gap-2">
                      {resumeAnalysisStatus === 'idle' && (
                        <div className="p-2 bg-slate-100 dark:bg-slate-700 rounded-full">
                          <Clock className="w-5 h-5 text-slate-400" />
                        </div>
                      )}
                      {resumeAnalysisStatus === 'processing' && (
                        <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-full">
                          <Loader className="w-5 h-5 text-blue-500 animate-spin" />
                        </div>
                      )}
                      {resumeAnalysisStatus === 'completed' && (
                        <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-full shadow-lg">
                          <CheckCircle className="w-5 h-5 text-green-500" />
                        </div>
                      )}
                      {resumeAnalysisStatus === 'error' && (
                        <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-full">
                          <div className="w-5 h-5 rounded-full bg-red-500" />
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <FileUpload onFileUpload={handleResumeUpload} />
                    {resumeAnalysisStatus === 'processing' && (
                      <div className="flex items-center gap-3 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-200 dark:border-blue-800">
                        <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent"></div>
                        <span className="text-sm text-blue-700 dark:text-blue-300 font-medium">
                          Analyzing resume with AI...
                        </span>
                      </div>
                    )}
                    {resumeAnalysisStatus === 'completed' && (
                      <div className="flex items-center gap-3 p-4 bg-green-50 dark:bg-green-900/20 rounded-xl border border-green-200 dark:border-green-800">
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        <span className="text-sm text-green-700 dark:text-green-300 font-medium">
                          Resume analysis completed: {resumeAnalysisData?.name} ({resumeAnalysisData?.experienceYears} years)
                        </span>
                      </div>
                    )}
                    {resumeAnalysisStatus === 'error' && (
                      <div className="flex items-center gap-3 p-4 bg-red-50 dark:bg-red-900/20 rounded-xl border border-red-200 dark:border-red-800">
                        <div className="w-4 h-4 rounded-full bg-red-500" />
                        <span className="text-sm text-red-700 dark:text-red-300 font-medium">
                          Resume analysis failed. Please try again.
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Enhanced Job Analysis Card */}
            <div className="group relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-pink-600/10 rounded-2xl blur-xl group-hover:blur-2xl transition-all duration-500"></div>
              <div className="relative backdrop-blur-sm bg-white/80 dark:bg-slate-800/80 border border-white/20 dark:border-slate-700/30 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-500 hover:scale-[1.02] overflow-hidden">
                <div className="absolute top-0 right-0 w-40 h-40 bg-gradient-to-br from-purple-100/50 to-pink-100/50 dark:from-purple-900/30 dark:to-pink-900/30 rounded-full -mr-20 -mt-20 group-hover:scale-110 transition-transform duration-500"></div>
                
                <div className="relative p-8">
                  <div className="flex items-center gap-4 mb-6">
                    <div className="p-3 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg group-hover:shadow-xl transition-all duration-300">
                      <Globe className="w-7 h-7 text-white" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-2xl font-bold text-slate-800 dark:text-slate-200 mb-1">Job Analysis</h3>
                      <p className="text-slate-600 dark:text-slate-400 font-medium">Paste URL or job description for analysis</p>
                    </div>
                    {/* Enhanced Status Indicator */}
                    <div className="flex items-center gap-2">
                      {jobAnalysisStatus === 'idle' && (
                        <div className="p-2 bg-slate-100 dark:bg-slate-700 rounded-full">
                          <Clock className="w-5 h-5 text-slate-400" />
                        </div>
                      )}
                      {jobAnalysisStatus === 'processing' && (
                        <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-full">
                          <Loader className="w-5 h-5 text-purple-500 animate-spin" />
                        </div>
                      )}
                      {jobAnalysisStatus === 'completed' && (
                        <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-full shadow-lg">
                          <CheckCircle className="w-5 h-5 text-green-500" />
                        </div>
                      )}
                      {jobAnalysisStatus === 'error' && (
                        <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-full">
                          <div className="w-5 h-5 rounded-full bg-red-500" />
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <JobAnalysis onJobData={handleJobData} />
                    {jobAnalysisStatus === 'processing' && (
                      <div className="flex items-center gap-3 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-xl border border-purple-200 dark:border-purple-800">
                        <div className="animate-spin rounded-full h-4 w-4 border-2 border-purple-500 border-t-transparent"></div>
                        <span className="text-sm text-purple-700 dark:text-purple-300 font-medium">
                          Analyzing job posting...
                        </span>
                      </div>
                    )}
                    {jobAnalysisStatus === 'completed' && (
                      <div className="flex items-center gap-3 p-4 bg-green-50 dark:bg-green-900/20 rounded-xl border border-green-200 dark:border-green-800">
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        <span className="text-sm text-green-700 dark:text-green-300 font-medium">
                          Job analysis completed: {jobAnalysisData?.title} at {jobAnalysisData?.company}
                        </span>
                      </div>
                    )}
                    {jobAnalysisStatus === 'error' && (
                      <div className="flex items-center gap-3 p-4 bg-red-50 dark:bg-red-900/20 rounded-xl border border-red-200 dark:border-red-800">
                        <div className="w-4 h-4 rounded-full bg-red-500" />
                        <span className="text-sm text-red-700 dark:text-red-300 font-medium">
                          Job analysis failed. Please try again.
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Enhanced Analysis Button */}
          {canAnalyze && (
            <div className="text-center mb-16">
              <div className="relative inline-block">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl blur-xl opacity-75 animate-pulse"></div>
                <Button
                  onClick={handleStartAnalysis}
                  disabled={!bothAnalysesReady}
                  className="relative bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white text-lg font-semibold px-12 py-6 h-auto shadow-2xl transition-all duration-300 disabled:opacity-50 hover:scale-105 rounded-2xl border-0"
                >
                  {comprehensiveAnalysisReady ? (
                    <>
                      <Zap className="w-5 h-5 mr-2" />
                      Launch Instant Analysis
                    </>
                  ) : bothAnalysesReady ? (
                    <>
                      <Brain className="w-5 h-5 mr-2" />
                      Generate Interview Guide
                    </>
                  ) : (
                    <>
                      <Loader className="w-5 h-5 mr-2 animate-spin" />
                      Preparing Analysis...
                    </>
                  )}
                </Button>
              </div>
              
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

          {/* Enhanced Feature Cards */}
          <div className="grid md:grid-cols-3 gap-8 mt-20">
            {/* Smart Question Generation Card */}
            <div className="group relative overflow-hidden h-80"
                 onMouseEnter={() => setCard1Hovered(true)}
                 onMouseLeave={() => setCard1Hovered(false)}>
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-indigo-600/10 rounded-2xl blur-xl group-hover:blur-2xl transition-all duration-500"></div>
              <div className="relative backdrop-blur-sm bg-white/80 dark:bg-slate-800/80 border border-white/20 dark:border-slate-700/30 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-500 hover:scale-[1.02] h-full flex flex-col overflow-hidden">
                <div className="absolute top-0 right-0 w-40 h-40 bg-gradient-to-br from-blue-100/50 to-indigo-100/50 dark:from-blue-900/30 dark:to-indigo-900/30 rounded-full -mr-20 -mt-20 group-hover:scale-110 transition-transform duration-500"></div>
                
                {/* Enhanced Coming Soon Badge */}
                <div className="absolute top-4 right-4 px-3 py-1.5 bg-gradient-to-r from-amber-400 via-orange-500 to-red-500 text-white text-xs font-bold rounded-full shadow-lg animate-pulse">
                  Coming Soon
                </div>
                
                <div className="relative p-8 flex-1 flex flex-col text-center">
                  <div className="p-4 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl shadow-lg group-hover:shadow-xl transition-all duration-300 mx-auto mb-6">
                    <Brain className="w-8 h-8 text-white" />
                  </div>
                  
                  <h3 className="text-2xl font-bold text-slate-800 dark:text-slate-200 mb-3">Smart Question Generation</h3>
                  
                  <div className="flex-1 mb-6">
                    <p className="text-slate-600 dark:text-slate-300 text-sm leading-relaxed group-hover:hidden">
                      AI-generated interview questions tailored to your resume and the specific job requirements.
                    </p>
                    <div className="hidden group-hover:block">
                      <p className="text-blue-600 dark:text-blue-400 text-sm font-semibold mb-3 cursor-pointer" onClick={() => window.open('https://www.linkedin.com/in/avikalp/', '_blank')}>
                        <span className="flex items-center justify-center gap-2 p-3 bg-blue-50 dark:bg-blue-900/30 rounded-xl border border-blue-200 dark:border-blue-800">
                          <Zap className="w-4 h-4" />
                          Wanna speed it up? Come build with us!
                        </span>
                      </p>
                    </div>
                  </div>
                  
                  <CountdownTimer targetDate={new Date('2025-07-26')} title="July 26th" isHovered={card1Hovered} />
                </div>
              </div>
            </div>
            
            {/* Skills Gap Analysis Card */}
            <div className="group relative overflow-hidden h-80"
                 onMouseEnter={() => setCard2Hovered(true)}
                 onMouseLeave={() => setCard2Hovered(false)}>
              <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-pink-600/10 rounded-2xl blur-xl group-hover:blur-2xl transition-all duration-500"></div>
              <div className="relative backdrop-blur-sm bg-white/80 dark:bg-slate-800/80 border border-white/20 dark:border-slate-700/30 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-500 hover:scale-[1.02] h-full flex flex-col overflow-hidden">
                <div className="absolute top-0 right-0 w-40 h-40 bg-gradient-to-br from-purple-100/50 to-pink-100/50 dark:from-purple-900/30 dark:to-pink-900/30 rounded-full -mr-20 -mt-20 group-hover:scale-110 transition-transform duration-500"></div>
                
                {/* Enhanced Coming Soon Badge */}
                <div className="absolute top-4 right-4 px-3 py-1.5 bg-gradient-to-r from-amber-400 via-orange-500 to-red-500 text-white text-xs font-bold rounded-full shadow-lg animate-pulse">
                  Coming Soon
                </div>
                
                <div className="relative p-8 flex-1 flex flex-col text-center">
                  <div className="p-4 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl shadow-lg group-hover:shadow-xl transition-all duration-300 mx-auto mb-6">
                    <Target className="w-8 h-8 text-white" />
                  </div>
                  
                  <h3 className="text-2xl font-bold text-slate-800 dark:text-slate-200 mb-3">Skills Gap Analysis</h3>
                  
                  <div className="flex-1 mb-6">
                    <p className="text-slate-600 dark:text-slate-300 text-sm leading-relaxed group-hover:hidden">
                      Identify gaps between your skills and job requirements, with personalized learning recommendations.
                    </p>
                    <div className="hidden group-hover:block">
                      <p className="text-purple-600 dark:text-purple-400 text-sm font-semibold mb-3 cursor-pointer" onClick={() => window.open('https://www.linkedin.com/in/avikalp/', '_blank')}>
                        <span className="flex items-center justify-center gap-2 p-3 bg-purple-50 dark:bg-purple-900/30 rounded-xl border border-purple-200 dark:border-purple-800">
                          <Zap className="w-4 h-4" />
                          Wanna speed it up? Come build with us!
                        </span>
                      </p>
                    </div>
                  </div>
                  
                  <CountdownTimer targetDate={new Date('2025-08-09')} title="August 9th" isHovered={card2Hovered} />
                </div>
              </div>
            </div>
            
            {/* Salary Negotiation Card */}
            <div className="group relative overflow-hidden h-80"
                 onMouseEnter={() => setCard3Hovered(true)}
                 onMouseLeave={() => setCard3Hovered(false)}>
              <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 to-teal-600/10 rounded-2xl blur-xl group-hover:blur-2xl transition-all duration-500"></div>
              <div className="relative backdrop-blur-sm bg-white/80 dark:bg-slate-800/80 border border-white/20 dark:border-slate-700/30 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-500 hover:scale-[1.02] h-full flex flex-col overflow-hidden">
                <div className="absolute top-0 right-0 w-40 h-40 bg-gradient-to-br from-emerald-100/50 to-teal-100/50 dark:from-emerald-900/30 dark:to-teal-900/30 rounded-full -mr-20 -mt-20 group-hover:scale-110 transition-transform duration-500"></div>
                
                {/* Enhanced Coming Soon Badge */}
                <div className="absolute top-4 right-4 px-3 py-1.5 bg-gradient-to-r from-amber-400 via-orange-500 to-red-500 text-white text-xs font-bold rounded-full shadow-lg animate-pulse">
                  Coming Soon
                </div>
                
                <div className="relative p-8 flex-1 flex flex-col text-center">
                  <div className="p-4 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl shadow-lg group-hover:shadow-xl transition-all duration-300 mx-auto mb-6">
                    <Trophy className="w-8 h-8 text-white" />
                  </div>
                  
                  <h3 className="text-2xl font-bold text-slate-800 dark:text-slate-200 mb-3">Salary Negotiation</h3>
                  
                  <div className="flex-1 mb-6">
                    <p className="text-slate-600 dark:text-slate-300 text-sm leading-relaxed group-hover:hidden">
                      AI-powered salary insights and negotiation strategies based on market data and your profile.
                    </p>
                    <div className="hidden group-hover:block">
                      <p className="text-emerald-600 dark:text-emerald-400 text-sm font-semibold mb-3 cursor-pointer" onClick={() => window.open('https://www.linkedin.com/in/avikalp/', '_blank')}>
                        <span className="flex items-center justify-center gap-2 p-3 bg-emerald-50 dark:bg-emerald-900/30 rounded-xl border border-emerald-200 dark:border-emerald-800">
                          <Zap className="w-4 h-4" />
                          Wanna speed it up? Come build with us!
                        </span>
                      </p>
                    </div>
                  </div>
                  
                  <CountdownTimer targetDate={new Date('2025-08-23')} title="August 23rd" isHovered={card3Hovered} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 
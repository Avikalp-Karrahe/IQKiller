'use client'

import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Loader2, CheckCircle, AlertCircle, Brain, Target, HelpCircle, Trophy, DollarSign, FileText, Users, Zap, Star, BookOpen, ExternalLink, Github, Linkedin, Mail, MessageSquare, Heart, Trophy as TrophyIcon, Code, Building } from 'lucide-react'
import { ComprehensiveGuideDisplay } from './comprehensive-guide-display'

interface AnalysisStep {
  step: string
  status: 'processing' | 'completed' | 'error'
  message: string
  progress: number
  data?: any
  error?: string
}

interface StreamingAnalysisProps {
  resumeText: string
  jobDescription: string
  jobData?: any
  resumeAnalysisData?: any
  jobAnalysisData?: any
  preComputedResults?: any
  onComplete?: (result: any) => void
}

export default function StreamingAnalysis({ resumeText, jobDescription, jobData, resumeAnalysisData, jobAnalysisData, preComputedResults, onComplete }: StreamingAnalysisProps) {
  const [steps, setSteps] = useState<AnalysisStep[]>([])
  const [currentStep, setCurrentStep] = useState(0)
  const [overallProgress, setOverallProgress] = useState(0)
  const [isComplete, setIsComplete] = useState(false)
  const [finalResults, setFinalResults] = useState<any>(null)
  const [comprehensiveGuide, setComprehensiveGuide] = useState<any>(null)
  const [showGuideView, setShowGuideView] = useState(false)
  
  // Granular progress tracking for questions
  const [questionProgress, setQuestionProgress] = useState({
    total: 15, // Expected total questions
    completed: 0,
    technical: { completed: 0, total: 5 },
    behavioral: { completed: 0, total: 5 },
    systemDesign: { completed: 0, total: 5 }
  })

  // Scroll to top when guide view is shown
  useEffect(() => {
    if (showGuideView) {
      // Use setTimeout to ensure the component has rendered
      setTimeout(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }, 100)
    }
  }, [showGuideView])

  const analysisSteps = [
    { key: 'resume_analysis', label: 'Resume Analysis', icon: FileText, color: 'blue' },
    { key: 'job_matching', label: 'Job Matching', icon: Target, color: 'purple' },
    { key: 'question_generation', label: 'Interview Questions', icon: HelpCircle, color: 'green' },
    { key: 'question_generated', label: 'Questions Ready', icon: HelpCircle, color: 'green' },
    { key: 'final_analysis', label: 'Final Analysis', icon: Brain, color: 'indigo' },
    { key: 'comprehensive_guide', label: 'Professional Guide', icon: BookOpen, color: 'orange' },
    { key: 'completed', label: 'Complete', icon: Trophy, color: 'pink' }
  ]

  useEffect(() => {
    startAnalysis()
  }, [])

  useEffect(() => {
    // Check if all steps are completed and force completion state
    const allStepsComplete = analysisSteps.every(step => {
      const stepStatus = getStepStatus(step.key)
      return stepStatus === 'completed'
    })
    
    if (allStepsComplete && steps.length >= analysisSteps.length && !isComplete) {
      console.log('All steps completed, forcing completion state')
      setIsComplete(true)
      setOverallProgress(100)
      setCurrentStep(analysisSteps.length - 1)
    }

    // Recovery mechanism: if resume analysis is in error state but we have valid data, recover
    const resumeStatus = getStepStatus('resume_analysis')
    if (resumeStatus === 'error' && resumeAnalysisData && !isComplete) {
      console.log('🔄 Recovering resume analysis from error state - we have valid data')
      updateStep('resume_analysis', 'completed', '✅ Resume analysis recovered', 100, resumeAnalysisData)
    }
  }, [steps, isComplete, resumeAnalysisData])

  const startAnalysis = async () => {
    try {
      // If we have pre-computed comprehensive results, show them immediately
      if (preComputedResults) {
        console.log('🚀 Using pre-computed comprehensive analysis results!')
        
        // Mark all steps as completed immediately
        const steps = [
          { key: 'resume_analysis', message: '✅ Resume analysis (pre-computed)', data: preComputedResults.resumeData },
          { key: 'job_matching', message: '✅ Job matching (pre-computed)', data: preComputedResults.matchData },
          { key: 'question_generation', message: '✅ Questions generated (pre-computed)', data: preComputedResults.questions },
          { key: 'question_generated', message: '✅ Questions ready (pre-computed)', data: preComputedResults.questions },
          { key: 'final_analysis', message: '✅ Final analysis (pre-computed)', data: preComputedResults.finalAnalysis },
          { key: 'comprehensive_guide', message: '✅ Professional guide (pre-computed)', data: preComputedResults.comprehensiveGuide },
          { key: 'completed', message: '🎉 Analysis complete! (pre-computed)', data: preComputedResults }
        ]

        // Complete all steps rapidly with animation
        for (let i = 0; i < steps.length; i++) {
          const step = steps[i]
          updateStep(step.key, 'completed', step.message, 100, step.data)
          setCurrentStep(i)
          setOverallProgress(((i + 1) / steps.length) * 100)
          
          // Update question progress for pre-computed questions
          if (step.key === 'question_generation' && step.data) {
            const questions = step.data
            const questionCount = questions.length || 15
            
            // Count questions by type
            const technicalCount = questions.filter((q: any) => q.type === 'technical').length
            const behavioralCount = questions.filter((q: any) => q.type === 'behavioral').length  
            const systemDesignCount = questions.filter((q: any) => q.type === 'system-design').length
            
            console.log('📊 Updating question progress with pre-computed data:', {
              total: questionCount, 
              technical: technicalCount,
              behavioral: behavioralCount, 
              systemDesign: systemDesignCount
            })
            
            // Update question progress with real counts
            setQuestionProgress({
              total: questionCount,
              completed: questionCount,
              technical: { completed: technicalCount, total: technicalCount },
              behavioral: { completed: behavioralCount, total: behavioralCount },
              systemDesign: { completed: systemDesignCount, total: systemDesignCount }
            })
          }
          
          // Small delay for UI effect
          if (i < steps.length - 1) {
            await new Promise(resolve => setTimeout(resolve, 100))
          }
        }

        // Set final results immediately
        setFinalResults(preComputedResults)
        setComprehensiveGuide(preComputedResults.comprehensiveGuide)
        setIsComplete(true)
        setOverallProgress(100)
        onComplete?.(preComputedResults)
        return
      }

      // Initialize steps - be more conservative with status updates
      if (resumeAnalysisData) {
        updateStep('resume_analysis', 'completed', '✅ Resume analysis already completed', 100, resumeAnalysisData)
        setCurrentStep(1)
      } else {
        updateStep('resume_analysis', 'processing', 'Starting resume analysis...', 10)
        setCurrentStep(0)
      }

      if (jobAnalysisData) {
        updateStep('job_matching', 'completed', '✅ Job analysis already completed', 100, jobAnalysisData)
        if (!resumeAnalysisData) setCurrentStep(1)
        else setCurrentStep(2)
      } else {
        updateStep('job_matching', 'processing', 'Starting job analysis...', 10)
      }
      
      // Simulate progress for better UX - but be more conservative
      const progressInterval = setInterval(() => {
        setOverallProgress(prev => Math.min(prev + 5, 70)) // More conservative progress
      }, 500) // Slower updates
      
      console.log('🚀 Starting enhanced analysis with pre-processed data:', {
        hasResumeData: !!resumeAnalysisData,
        hasJobData: !!jobAnalysisData
      })
      
      // Add timeout and retry logic for better resilience
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 30000) // 30 second timeout
      
      try {
        const response = await fetch('/api/analyze-complete', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            resumeText, 
            jobDescription,
            jobData,
            resumeAnalysisData, // Pass pre-processed data
            jobAnalysisData    // Pass pre-processed data
          }),
          signal: controller.signal
        })

        clearTimeout(timeoutId)
        clearInterval(progressInterval)

        if (!response.ok) {
          // Don't immediately mark as error - try to get more info
          const errorText = await response.text()
          console.error('Response not OK:', response.status, errorText)
          throw new Error(`Analysis failed: ${response.status} - ${errorText}`)
        }

        const data = await response.json()
        console.log('Enhanced analysis result:', data)

        if (data.success && data.data) {
          // Map the API response structure to match expected format
          const apiData = data.data
          const mappedResults = {
            resumeData: apiData.resumeAnalysis,
            matchData: apiData.jobAnalysis,
            questions: apiData.enhancedQuestions,
            finalAnalysis: apiData.matchAnalysis,
            comprehensiveGuide: apiData.comprehensiveGuide,
            premiumContent: apiData.premiumContent,
            premiumCoaching: apiData.premiumCoaching
          }
          
          console.log('📊 Mapped API data structure:', {
            questionsCount: mappedResults.questions?.length,
            hasResumeData: !!mappedResults.resumeData,
            hasMatchData: !!mappedResults.matchData
          })
          
          // Simulate step completion for UI
          const steps = [
            { key: 'resume_analysis', message: 'Resume analysis completed', data: mappedResults.resumeData },
            { key: 'job_matching', message: 'Job matching completed', data: mappedResults.matchData },
            { key: 'question_generation', message: 'Questions generated', data: mappedResults.questions },
            { key: 'question_generated', message: 'Questions ready', data: mappedResults.questions },
            { key: 'final_analysis', message: 'Final analysis completed', data: mappedResults.finalAnalysis },
            { key: 'comprehensive_guide', message: 'Professional guide created', data: mappedResults.comprehensiveGuide },
            { key: 'completed', message: 'Analysis complete!', data: mappedResults }
          ]

          // Complete all steps rapidly with question generation simulation
          for (let i = 0; i < steps.length; i++) {
            const step = steps[i]
            
            // If this is the question generation step, simulate progress
            if (step.key === 'question_generation') {
              updateStep(step.key, 'processing', 'Starting question generation...', 0, step.data)
              setCurrentStep(i)
              
              // Update question progress with real data from API
              if (step.data && step.data.length > 0) {
                const questions = step.data
                const questionCount = questions.length || 15
                
                // Count questions by type
                const technicalCount = questions.filter((q: any) => q.type === 'technical').length
                const behavioralCount = questions.filter((q: any) => q.type === 'behavioral').length  
                const systemDesignCount = questions.filter((q: any) => q.type === 'system-design').length
                
                console.log('📊 Updating question progress with real API data:', {
                  total: questionCount, 
                  technical: technicalCount,
                  behavioral: behavioralCount, 
                  systemDesign: systemDesignCount
                })
                
                // Update question progress with real counts
                setQuestionProgress({
                  total: questionCount,
                  completed: questionCount,
                  technical: { completed: technicalCount, total: technicalCount },
                  behavioral: { completed: behavioralCount, total: behavioralCount },
                  systemDesign: { completed: systemDesignCount, total: systemDesignCount }
                })
              }
              
              await simulateQuestionProgress()
            } else {
              updateStep(step.key, 'completed', step.message, 100, step.data)
              setCurrentStep(i)
              setOverallProgress(((i + 1) / steps.length) * 100)
            }
            
            // Small delay for UI effect
            if (i < steps.length - 1) {
              await new Promise(resolve => setTimeout(resolve, 200))
            }
          }

          // Set final results
          setFinalResults(mappedResults)
          setComprehensiveGuide(mappedResults.comprehensiveGuide)
          setIsComplete(true)
          setOverallProgress(100)
          onComplete?.(mappedResults)
          
        } else {
          throw new Error(data.error || 'Analysis failed - no results returned')
        }
      } catch (fetchError) {
        clearTimeout(timeoutId)
        clearInterval(progressInterval)
        
        // Handle different types of errors more gracefully
        const error = fetchError as Error
        if (error.name === 'AbortError') {
          console.error('Analysis timed out after 30 seconds')
          updateStep('resume_analysis', 'error', 'Analysis timed out. Please try again.', 0, undefined, 'Timeout after 30 seconds')
        } else if (error.message.includes('NetworkError') || error.message.includes('fetch')) {
          console.error('Network error during analysis:', error)
          updateStep('resume_analysis', 'error', 'Network error. Please check your connection and try again.', 0, undefined, error.message)
        } else {
          console.error('Analysis error:', error)
          updateStep('resume_analysis', 'error', 'Analysis failed. Please try again.', 0, undefined, error.message)
        }
        throw error // Re-throw so caller knows about the error
      }
      
    } catch (error) {
      console.error('Unexpected analysis error:', error)
      // Only update error state if we haven't already handled it above
      const currentResumeStatus = getStepStatus('resume_analysis')
      if (currentResumeStatus !== 'error') {
        updateStep('resume_analysis', 'error', 'Unexpected error. Please refresh and try again.', 0, undefined, error instanceof Error ? error.message : 'Unknown error')
      }
    }
  }

  const handleStreamData = (data: any) => {
    const { step, status, message, progress, results, error } = data
    console.log('📥 Handling stream data:', { step, status, message, progress, hasResults: !!results, hasError: !!error })
    
    // Validate the data before processing
    if (!step || !status) {
      console.warn('⚠️ Invalid stream data received:', data)
      return
    }
    
    // Don't mark resume_analysis as error if we have valid data already
    if (step === 'resume_analysis' && status === 'error' && resumeAnalysisData) {
      console.log('🛡️ Preventing resume analysis error - we have valid data')
      return
    }
        
    // Update the current step's progress
    updateStep(step, status, message, progress || 0, results, error)

    // Handle question generation completion - update real progress
    if (step === 'question_generation' && status === 'completed' && results?.questions) {
      const questions = results.questions
      const questionCount = questions.length || 15
      
      // Count questions by type
      const technicalCount = questions.filter((q: any) => q.type === 'technical').length
      const behavioralCount = questions.filter((q: any) => q.type === 'behavioral').length  
      const systemDesignCount = questions.filter((q: any) => q.type === 'system-design').length
      
      // Update question progress with real counts
      setQuestionProgress({
        total: questionCount,
        completed: questionCount,
        technical: { completed: technicalCount, total: technicalCount },
        behavioral: { completed: behavioralCount, total: behavioralCount },
        systemDesign: { completed: systemDesignCount, total: systemDesignCount }
      })
      
      console.log('✅ Updated question progress with real data:', {
        total: questionCount, 
        technical: technicalCount,
        behavioral: behavioralCount, 
        systemDesign: systemDesignCount
      })
    }

    if (status === 'completed') {
      const stepIndex = analysisSteps.findIndex(s => s.key === step)
      
      // Update overall progress
      const newProgress = ((stepIndex + 1) / analysisSteps.length) * 100
      setOverallProgress(Math.min(95, newProgress))
      
      // Move to next step if not the last step
      if (stepIndex < analysisSteps.length - 1) {
        setCurrentStep(stepIndex + 1)
        // Initialize next step
        const nextStep = analysisSteps[stepIndex + 1]
        updateStep(nextStep.key, 'processing', `Starting ${nextStep.label.toLowerCase()}...`, 0)
      }
      
      // Handle final results
      if (results) {
        if (step === 'comprehensive_guide') {
          setComprehensiveGuide(results)
        }
      if (step === 'completed') {
          setFinalResults(results)
        setIsComplete(true)
        setOverallProgress(100)
          onComplete?.(results)
        }
      }
    }
  }

  const updateStep = (step: string, status: AnalysisStep['status'], message: string, progress: number, data?: any, error?: string) => {
    setSteps(prevSteps => {
      const existingStepIndex = prevSteps.findIndex(s => s.step === step)
      const newStep: AnalysisStep = { step, status, message, progress, data, error }
      
      // Don't allow backward state transitions unless it's a real error
      if (existingStepIndex >= 0) {
        const existingStep = prevSteps[existingStepIndex]
        
        // If existing step is completed and we're trying to set it to processing/error,
        // only allow if this is a genuine error (has error message)
        if (existingStep.status === 'completed' && status !== 'completed') {
          if (status === 'error' && error) {
            // Allow error state if there's a real error message
            console.log(`⚠️ Overriding completed step ${step} with error: ${error}`)
          } else {
            // Ignore the update - don't go backwards
            console.log(`🚫 Ignoring backward transition for ${step}: ${existingStep.status} -> ${status}`)
            return prevSteps
          }
        }
        
        // Update existing step
        const updatedSteps = [...prevSteps]
        updatedSteps[existingStepIndex] = newStep
        return updatedSteps
      } else {
        // Add new step
        return [...prevSteps, newStep]
      }
    })
  }

  const getStepStatus = (stepKey: string) => {
    const step = steps.find(s => s.step === stepKey)
    if (!step) return 'pending'
    return step.status
  }

  const getStepData = (stepKey: string) => {
    const step = steps.find(s => s.step === stepKey)
    return step?.data
  }

  // Function to simulate question generation progress
  const simulateQuestionProgress = async () => {
    // Reset progress
    setQuestionProgress({
      total: 15,
      completed: 0,
      technical: { completed: 0, total: 5 },
      behavioral: { completed: 0, total: 5 },
      systemDesign: { completed: 0, total: 5 }
    })

    // Simulate generating questions one by one
    const categories = ['technical', 'behavioral', 'systemDesign'] as const
    
    for (let i = 0; i < 15; i++) {
      await new Promise(resolve => setTimeout(resolve, 200 + Math.random() * 300)) // Random delay
      
      const categoryIndex = Math.floor(i / 5)
      const category = categories[categoryIndex]
      
      setQuestionProgress(prev => ({
        ...prev,
        completed: i + 1,
        [category]: {
          ...prev[category],
          completed: prev[category].completed + 1
        }
      }))

      // Update the step progress
      const progressPercent = ((i + 1) / 15) * 100
      updateStep('question_generation', 'processing', `Generating question ${i + 1} of 15...`, progressPercent)
    }

    // Mark as completed
    updateStep('question_generation', 'completed', '✅ All questions generated', 100)
  }

  // Get step progress (including granular progress for questions)
  const getStepProgress = (stepKey: string) => {
    const step = steps.find(s => s.step === stepKey)
    if (!step) return 0
    
    if (stepKey === 'question_generation' && step.status === 'processing') {
      return (questionProgress.completed / questionProgress.total) * 100
    }
    
    return step.progress
  }

  // Show comprehensive guide if available and user wants to see it
  if (showGuideView && comprehensiveGuide) {
    return (
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <Button 
            variant="outline" 
            onClick={() => setShowGuideView(false)}
            className="mb-4"
          >
            ← Back to Analysis Summary
          </Button>
          <Badge variant="secondary" className="text-sm">
            Professional Interview Guide
          </Badge>
        </div>
        <ComprehensiveGuideDisplay 
          guide={{
            ...comprehensiveGuide,
            premiumContent: finalResults?.premiumContent,
            premiumCoaching: finalResults?.premiumCoaching
          }} 
          isGenerating={false}
        />
      </div>
    )
  }

  const renderResults = () => {
    if (!isComplete || !finalResults) return null

    return null // Content is now handled in the main section above
  }

    return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Marketing Content With Progress Bar or Completion Message */}
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Progress Bar OR Completion Message */}
        {isComplete ? (
          /* Analysis Complete Section - Replaces Progress Bar Only */
          <Card className="bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-950/20 dark:to-blue-950/20 border border-green-200 dark:border-green-800">
            <CardContent className="p-8 text-center">
              <div className="inline-flex items-center gap-2 px-6 py-3 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-full text-lg font-semibold mb-6">
            <CheckCircle className="w-6 h-6" />
            Analysis Complete!
              </div>
              
              <h3 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-4">Your Interview Preparation Report</h3>
              <p className="text-gray-600 dark:text-gray-300 mb-8 text-lg">Comprehensive analysis with personalized recommendations</p>
              
              {comprehensiveGuide && (
                <div className="space-y-4">
                  <Button 
                    onClick={() => setShowGuideView(true)}
                    size="lg"
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-4 text-lg"
                  >
                    <BookOpen className="w-5 h-5 mr-2" />
                    View Professional Interview Guide
                  </Button>
                  <p className="text-gray-500 dark:text-gray-400 text-sm">
                    Complete with personalized questions, company insights, and preparation roadmap
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        ) : (
          /* Progress Bar - While Loading */
      <Card>
        <CardContent className="pt-6">
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Analysis Progress</h3>
                  <span className="text-sm font-medium text-gray-600 dark:text-gray-300">{Math.round(overallProgress)}%</span>
            </div>
                <Progress value={overallProgress} className="h-3 progress-bar" />
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-7 gap-4">
            {analysisSteps.map((step, idx) => {
              const status = getStepStatus(step.key)
              const isActive = idx === currentStep
              const isCompleted = status === 'completed'
              const hasError = status === 'error'
                  const stepProgress = getStepProgress(step.key)
              
              return (
                <div
                  key={step.key}
                      className={`flex flex-col items-center p-3 rounded-lg transition-all duration-200 relative overflow-hidden ${
                    isActive ? 'bg-blue-50 dark:bg-blue-950/30 border-2 border-blue-200 dark:border-blue-700' :
                    isCompleted ? 'bg-green-50 dark:bg-green-950/30 border-2 border-green-200 dark:border-green-700' :
                    hasError ? 'bg-red-50 dark:bg-red-950/30 border-2 border-red-200 dark:border-red-700' :
                    'bg-gray-50 dark:bg-gray-800/50 border-2 border-gray-200 dark:border-gray-700'
                  }`}
                >
                      {/* Progress fill background */}
                      {(isActive || isCompleted) && (
                        <div 
                          className={`absolute inset-0 transition-all duration-300 ${
                            isCompleted ? 'bg-green-100 dark:bg-green-900/40' : 'bg-blue-100 dark:bg-blue-900/40'
                          }`}
                          style={{ 
                            width: `${isCompleted ? 100 : stepProgress}%`,
                            background: isCompleted 
                              ? 'linear-gradient(90deg, rgba(34, 197, 94, 0.1) 0%, rgba(34, 197, 94, 0.2) 100%)'
                              : 'linear-gradient(90deg, rgba(59, 130, 246, 0.1) 0%, rgba(59, 130, 246, 0.2) 100%)'
                          }}
                        />
                      )}
                      
                      {/* Content */}
                      <div className="relative z-10 flex flex-col items-center">
                  <div className={`p-2 rounded-lg mb-2 ${
                    isActive ? 'bg-blue-100 dark:bg-blue-900' :
                    isCompleted ? 'bg-green-100 dark:bg-green-900' :
                    hasError ? 'bg-red-100 dark:bg-red-900' :
                    'bg-gray-100 dark:bg-gray-700'
                  }`}>
                    {isCompleted ? (
                      <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
                    ) : hasError ? (
                      <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400" />
                    ) : isActive ? (
                      <Loader2 className="w-5 h-5 text-blue-600 dark:text-blue-400 animate-spin" />
                    ) : (
                      <step.icon className="w-5 h-5 text-gray-400 dark:text-gray-500" />
                    )}
                  </div>
                  <span className={`text-xs font-medium text-center ${
                    isActive ? 'text-blue-700 dark:text-blue-300' :
                    isCompleted ? 'text-green-700 dark:text-green-300' :
                    hasError ? 'text-red-700 dark:text-red-300' :
                    'text-gray-500 dark:text-gray-400'
                  }`}>
                    {step.label}
                  </span>
                        
                        {/* Progress indicator for question generation */}
                        {step.key === 'question_generation' && (isActive || isCompleted) && (
                          <div className="mt-1 text-xs text-blue-600 dark:text-blue-400 font-medium">
                            {questionProgress.completed}/{questionProgress.total}
                          </div>
                        )}
                      </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>
        )}

          {/* Hero Section */}
          <div className="text-center space-y-6">
            <div className="flex justify-center">
              <Badge variant="secondary" className="px-4 py-2 text-sm font-medium bg-blue-50 text-blue-700 border border-blue-200">
                Free AI Interview Prep in 5 Seconds
              </Badge>
                  </div>
            
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-gray-100 leading-tight">
              Stop guessing what they'll ask.<br />
              <span className="text-blue-600 dark:text-blue-400">Know what to say</span> with <span className="text-slate-800 dark:text-slate-200">IQ</span><span className="text-blue-600 dark:text-blue-400">Killer</span>.
            </h1>
            
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Built by an AI Engineer who&apos;s been on both sides of interviews. Get personalized questions, 
              insights, and prep strategies for any role in seconds.
            </p>
          </div>

          {/* Value Propositions */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="text-center p-6 border-2 border-transparent hover:border-blue-200 dark:hover:border-blue-700 transition-all">
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <Target className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">Actually Personalized</h3>
              <p className="text-sm text-gray-600 dark:text-gray-300">No generic templates. Every question and tip is tailored to your specific experience and the role you want.</p>
            </Card>

            <Card className="text-center p-6 border-2 border-transparent hover:border-blue-200 dark:hover:border-blue-700 transition-all">
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <Code className="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">Built by a Builder</h3>
              <p className="text-sm text-gray-600 dark:text-gray-300">Created by someone who ships real AI products, not just presentations. I understand what actually matters in interviews.</p>
            </Card>

            <Card className="text-center p-6 border-2 border-transparent hover:border-blue-200 dark:hover:border-blue-700 transition-all">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <Heart className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">Truly Free</h3>
              <p className="text-sm text-gray-600 dark:text-gray-300">No signup required. No paywalls. No upsells. Just instant, high-quality interview prep because I believe good tools should be accessible.</p>
            </Card>

            <Card className="text-center p-6 border-2 border-transparent hover:border-blue-200 dark:hover:border-blue-700 transition-all">
              <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <Github className="w-6 h-6 text-orange-600 dark:text-orange-400" />
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">Open Source</h3>
              <p className="text-sm text-gray-600 dark:text-gray-300">Transparent code, honest intent. See exactly how your data is processed and contribute to making it better for everyone.</p>
            </Card>
          </div>

          {/* Social Proof */}
          <Card className="bg-gradient-to-r from-gray-50 to-blue-50 dark:from-gray-800/50 dark:to-blue-900/20 border border-blue-100 dark:border-blue-800">
            <CardContent className="p-8">
              <h3 className="text-2xl font-bold text-center text-gray-900 dark:text-gray-100 mb-8">
                Why Job Seekers Choose This
              </h3>
              
              <div className="grid md:grid-cols-3 gap-8">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600 dark:text-blue-400 mb-2">5 seconds</div>
                  <p className="text-gray-600 dark:text-gray-300">vs weeks of prep time</p>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600 dark:text-green-400 mb-2">$0</div>
                  <p className="text-gray-600 dark:text-gray-300">vs expensive coaching sessions</p>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-600 dark:text-purple-400 mb-2">Just launched</div>
                  <p className="text-gray-600 dark:text-gray-300">Already used by engineers prepping for FAANG and early-stage startups</p>
                </div>
                      </div>
              
              <div className="mt-8 text-center">
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-sm cursor-pointer relative overflow-hidden group">
                  {/* Star - clickable to GitHub with hover effects */}
                  <div 
                    className="relative z-10 p-1 rounded-full transition-all duration-300 group-hover:bg-yellow-200 hover:!bg-yellow-300 hover:scale-110 hover:animate-pulse"
                    onClick={(e) => {
                      e.stopPropagation()
                      window.open('https://github.com/avikalp-karrahe/iqkiller', '_blank')
                    }}
                  >
                    {/* Star icon (default state) */}
                    <Star 
                      className="w-4 h-4 transition-all duration-300 group-hover:opacity-0 group-hover:scale-0" 
                    />
                    {/* GitHub icon (hover state) */}
                    <Github 
                      className="w-4 h-4 absolute inset-0 m-1 transition-all duration-300 opacity-0 scale-0 group-hover:opacity-100 group-hover:scale-100 group-hover:text-yellow-600 hover:!text-yellow-500 hover:drop-shadow-[0_0_6px_rgba(234,179,8,0.6)]" 
                    />
                  </div>
                  
                  {/* Rest of button - clickable to feedback form */}
                  <span 
                    className="flex-1 cursor-pointer transition-all duration-300 hover:text-blue-600 hover:drop-shadow-[0_0_6px_rgba(59,130,246,0.6)]"
                    onClick={() => {
                      window.open('https://discord.gg/sEAEu6abdn', '_blank')
                    }}
                  >
                    Join our Discord! Share feedback & shape the next version.
                  </span>
                </div>
            </div>
          </CardContent>
        </Card>

        </div>

      {/* Results */}
      {renderResults()}
    </div>
  )
} 
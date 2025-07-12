'use client'

import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Link as LinkIcon, FileText, Loader2, CheckCircle, AlertCircle, Globe, Building2, MapPin, Clock, Sparkles, ExternalLink } from 'lucide-react'

interface JobAnalysisProps {
  onJobData: (data: any) => void
}

export function JobAnalysis({ onJobData }: JobAnalysisProps) {
  const [jobUrl, setJobUrl] = useState('')
  const [jobText, setJobText] = useState('')
  const [mode, setMode] = useState<'url' | 'text'>('url')
  const [isLoading, setIsLoading] = useState(false)
  const [scrapingStatus, setScrapingStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [scrapedData, setScrapedData] = useState<any>(null)
  const [isAnalysisComplete, setIsAnalysisComplete] = useState(false)
  const [completedJob, setCompletedJob] = useState<any>(null)

  const isValidUrl = (url: string) => {
    try {
      new URL(url)
      return true
    } catch {
      return false
    }
  }

  const handleUrlScraping = async (url: string) => {
    if (!isValidUrl(url)) {
      // Invalid URL, use as description (current behavior)
      const jobData = {
        description: url,
        source: 'url_saved',
        title: 'Job Position',
        company: 'Company'
      }
      onJobData(jobData)
      setCompletedJob(jobData)
      setIsAnalysisComplete(true)
      return
    }

    setIsLoading(true)
    setScrapingStatus('loading')

    try {
      console.log('🕷️ Attempting to scrape URL:', url)
      
      const response = await fetch('/api/test-firecrawl', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      })

      if (!response.ok) {
        throw new Error(`Scraping failed: ${response.statusText}`)
      }

      const result = await response.json()
      
      if (result.success && result.scrapedData) {
        console.log('✅ Scraping successful:', result.scrapedData)
        setScrapingStatus('success')
        setScrapedData(result.scrapedData)
        
        // Pass enhanced job data to parent
        const jobData = {
          description: result.scrapedData.content || url,
          source: 'url_scraped',
          title: result.scrapedData.title || 'Job Position',
          company: result.scrapedData.company || 'Company',
          location: result.scrapedData.location || '',
          url: url,
          scrapedAt: new Date().toISOString(),
          rawContent: result.scrapedData.content,
          // Additional structured data if available
          ...(result.scrapedData.structuredData || {})
        }
        onJobData(jobData)
        setCompletedJob(jobData)
        setIsAnalysisComplete(true)
      } else {
        throw new Error('No scraped data received')
      }
    } catch (error) {
      console.error('❌ Scraping failed:', error)
      setScrapingStatus('error')
      
      // Fallback to current behavior - use URL as description
      console.log('📄 Falling back to URL-as-description')
      const jobData = {
        description: url,
        source: 'url_fallback',
        title: 'Job Position',
        company: 'Company',
        fallbackReason: (error as Error).message
      }
      onJobData(jobData)
      setCompletedJob(jobData)
      setIsAnalysisComplete(true)
    } finally {
      setIsLoading(false)
    }
  }

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const url = e.target.value
    setJobUrl(url)
    setScrapingStatus('idle')
    setScrapedData(null)
    setIsAnalysisComplete(false)
    setCompletedJob(null)
    
    // Debounce the scraping attempt
    if (url.trim()) {
      setTimeout(() => {
        handleUrlScraping(url.trim())
      }, 1000) // Wait 1 second after user stops typing
    }
  }

  const handleTextSubmit = () => {
    if (!jobText.trim()) return
    
    const jobData = {
      description: jobText,
      source: 'manual_text',
      title: 'Custom Job Description',
      company: 'Company'
    }
    onJobData(jobData)
    setCompletedJob(jobData)
    setIsAnalysisComplete(true)
  }

  const handleNewAnalysis = () => {
    setJobUrl('')
    setJobText('')
    setScrapingStatus('idle')
    setScrapedData(null)
    setIsAnalysisComplete(false)
    setCompletedJob(null)
    setIsLoading(false)
  }

  // If analysis is complete, show success state
  if (isAnalysisComplete && completedJob) {
    return (
      <Card className="border-emerald-200 bg-gradient-to-br from-emerald-50 to-green-50 dark:from-emerald-950/20 dark:to-green-950/20">
        <CardHeader className="pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-100 dark:bg-emerald-900/50 rounded-lg">
              <Sparkles className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            </div>
            <div className="flex-1">
              <CardTitle className="text-emerald-900 dark:text-emerald-100 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-emerald-600" />
                Job Analysis Complete
              </CardTitle>
              <CardDescription className="text-emerald-700 dark:text-emerald-300">
                Successfully analyzed job posting
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Job Details Display */}
          <div className="bg-white dark:bg-gray-900/50 rounded-lg p-4 border border-emerald-200 dark:border-emerald-800">
            <div className="space-y-3">
              {completedJob.title && (
                <div className="flex items-start gap-2">
                  <Building2 className="w-4 h-4 text-emerald-600 mt-0.5" />
                  <div>
                    <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {completedJob.title}
                    </div>
                    {completedJob.company && (
                      <div className="text-xs text-gray-600 dark:text-gray-400">
                        at {completedJob.company}
                      </div>
                    )}
                  </div>
                </div>
              )}
              
              {completedJob.location && (
                <div className="flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-emerald-600" />
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    {completedJob.location}
                  </span>
                </div>
              )}
              
              {completedJob.url && (
                <div className="flex items-center gap-2">
                  <ExternalLink className="w-4 h-4 text-emerald-600" />
                  <a 
                    href={completedJob.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-sm text-emerald-600 hover:text-emerald-700 dark:text-emerald-400 dark:hover:text-emerald-300 underline"
                  >
                    View Original Posting
                  </a>
                </div>
              )}
              
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-emerald-600" />
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  Analyzed just now
                </span>
                <Badge variant="secondary" className="text-xs">
                  {completedJob.source === 'url_scraped' ? 'Auto-extracted' : 
                   completedJob.source === 'manual_text' ? 'Manual Input' : 'URL Fallback'}
                </Badge>
              </div>
            </div>
          </div>

          {/* Success Message */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-emerald-700 dark:text-emerald-300">
              <CheckCircle className="w-4 h-4" />
              <span className="font-medium">Ready for interview preparation</span>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleNewAnalysis}
              className="text-emerald-700 border-emerald-300 hover:bg-emerald-100 dark:text-emerald-300 dark:border-emerald-700 dark:hover:bg-emerald-900/20"
            >
              Analyze New Job
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border border-purple-200 bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-950/20 dark:to-blue-950/20">
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-100 dark:bg-purple-900/50 rounded-lg">
            <Globe className="w-5 h-5 text-purple-600 dark:text-purple-400" />
          </div>
          <div>
            <CardTitle className="text-purple-900 dark:text-purple-100">Job Analysis</CardTitle>
            <CardDescription className="text-purple-700 dark:text-purple-300">
              Paste URL or job description for analysis
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Mode Toggle */}
        <div className="flex space-x-1 p-1 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
          <Button
            variant={mode === 'url' ? 'default' : 'ghost'}
            onClick={() => setMode('url')}
            className={`flex-1 ${mode === 'url' 
              ? 'bg-white shadow-sm text-purple-700 dark:bg-gray-800 dark:text-purple-300' 
              : 'text-purple-600 hover:text-purple-700 dark:text-purple-400'
            }`}
          >
            <LinkIcon className="w-4 h-4 mr-2" />
            URL
          </Button>
          <Button
            variant={mode === 'text' ? 'default' : 'ghost'}
            onClick={() => setMode('text')}
            className={`flex-1 ${mode === 'text' 
              ? 'bg-white shadow-sm text-purple-700 dark:bg-gray-800 dark:text-purple-300' 
              : 'text-purple-600 hover:text-purple-700 dark:text-purple-400'
            }`}
          >
            <FileText className="w-4 h-4 mr-2" />
            Text
          </Button>
        </div>

        {mode === 'url' ? (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="job-url" className="text-sm font-medium text-purple-900 dark:text-purple-100">
                Job Posting URL
              </Label>
              <div className="relative">
                <Input
                  id="job-url"
                  type="url"
                  placeholder="https://company.com/careers/job-123456"
                  value={jobUrl}
                  onChange={handleUrlChange}
                  disabled={isLoading}
                  className="pr-10 border-purple-200 focus:border-purple-400 focus:ring-purple-400"
                />
                {scrapingStatus === 'loading' && (
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                    <Loader2 className="w-4 h-4 animate-spin text-purple-600" />
                  </div>
                )}
                {scrapingStatus === 'success' && (
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                    <CheckCircle className="w-4 h-4 text-emerald-600" />
                  </div>
                )}
                {scrapingStatus === 'error' && (
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                    <AlertCircle className="w-4 h-4 text-amber-600" />
                  </div>
                )}
              </div>
            </div>
            
            {/* Status Messages */}
            {scrapingStatus === 'loading' && (
              <div className="flex items-center gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg dark:bg-blue-950/20 dark:border-blue-800">
                <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                <div>
                  <div className="text-sm font-medium text-blue-800 dark:text-blue-200">
                    Extracting job details...
                  </div>
                  <div className="text-xs text-blue-600 dark:text-blue-400">
                    Analyzing the job posting content
                  </div>
                </div>
              </div>
            )}
            
            {scrapingStatus === 'success' && scrapedData && (
              <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-lg dark:bg-emerald-950/20 dark:border-emerald-800">
                <div className="flex items-center gap-2 text-sm font-medium text-emerald-800 dark:text-emerald-200 mb-3">
                  <CheckCircle className="w-4 h-4" />
                  Successfully extracted job details
                </div>
                <div className="space-y-2 text-sm">
                  {scrapedData.title && (
                    <div className="flex items-center gap-2">
                      <Building2 className="w-3 h-3 text-emerald-600" />
                      <span className="text-emerald-700 dark:text-emerald-300">
                        <strong>Role:</strong> {scrapedData.title}
                      </span>
                    </div>
                  )}
                  {scrapedData.company && (
                    <div className="flex items-center gap-2">
                      <Building2 className="w-3 h-3 text-emerald-600" />
                      <span className="text-emerald-700 dark:text-emerald-300">
                        <strong>Company:</strong> {scrapedData.company}
                      </span>
                    </div>
                  )}
                  {scrapedData.location && (
                    <div className="flex items-center gap-2">
                      <MapPin className="w-3 h-3 text-emerald-600" />
                      <span className="text-emerald-700 dark:text-emerald-300">
                        <strong>Location:</strong> {scrapedData.location}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}
            
            {scrapingStatus === 'error' && (
              <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg dark:bg-amber-950/20 dark:border-amber-800">
                <div className="flex items-center gap-2 text-sm font-medium text-amber-800 dark:text-amber-200 mb-2">
                  <AlertCircle className="w-4 h-4" />
                  Automatic extraction unavailable
                </div>
                <div className="text-xs text-amber-700 dark:text-amber-300">
                  Using URL content as job description. The analysis will still work perfectly!
                </div>
              </div>
            )}

            {/* Compatibility Note */}
            <div className="text-xs text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-950/20 p-3 rounded-lg border border-purple-200 dark:border-purple-800">
              <div className="flex items-center gap-2 font-medium mb-1">
                <Globe className="w-3 h-3" />
                Compatibility Note
              </div>
              <div>
                Some job sites with private access (like LinkedIn) may require manual text input due to login requirements.
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="job-text" className="text-sm font-medium text-purple-900 dark:text-purple-100">
                Job Description
              </Label>
              <textarea
                id="job-text"
                className="w-full min-h-[200px] p-3 border border-purple-200 rounded-lg resize-y focus:border-purple-400 focus:ring-purple-400 dark:bg-gray-900/50"
                placeholder="Paste the complete job description here..."
                value={jobText}
                onChange={(e) => setJobText(e.target.value)}
              />
            </div>
            <Button 
              onClick={handleTextSubmit} 
              disabled={!jobText.trim()}
              className="w-full bg-purple-600 hover:bg-purple-700 text-white"
            >
              <FileText className="w-4 h-4 mr-2" />
              Analyze Job Description
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
} 
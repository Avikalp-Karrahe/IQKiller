'use client'

import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Link as LinkIcon, FileText, Loader2, CheckCircle, AlertCircle, Globe } from 'lucide-react'

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
      onJobData({
        description: url,
        source: 'url_saved',
        title: 'Job Position',
        company: 'Company'
      })
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
        onJobData({
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
        })
      } else {
        throw new Error('No scraped data received')
      }
    } catch (error) {
      console.error('❌ Scraping failed:', error)
      setScrapingStatus('error')
      
      // Fallback to current behavior - use URL as description
      console.log('📄 Falling back to URL-as-description')
      onJobData({
        description: url,
        source: 'url_fallback',
        title: 'Job Position',
        company: 'Company',
        fallbackReason: (error as Error).message
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const url = e.target.value
    setJobUrl(url)
    setScrapingStatus('idle')
    setScrapedData(null)
    
    // Debounce the scraping attempt
    if (url.trim()) {
      setTimeout(() => {
        handleUrlScraping(url.trim())
      }, 1000) // Wait 1 second after user stops typing
    }
  }

  const handleTextSubmit = () => {
    if (!jobText.trim()) return
    
    onJobData({
      description: jobText,
      source: 'manual_text'
    })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Job Information</CardTitle>
        <CardDescription>
          Add job posting via URL or paste the description directly
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex space-x-2">
          <Button
            variant={mode === 'url' ? 'default' : 'outline'}
            onClick={() => setMode('url')}
            className="flex-1"
          >
            <LinkIcon className="w-4 h-4 mr-2" />
            URL
          </Button>
          <Button
            variant={mode === 'text' ? 'default' : 'outline'}
            onClick={() => setMode('text')}
            className="flex-1"
          >
            <FileText className="w-4 h-4 mr-2" />
            Text
          </Button>
        </div>

        {mode === 'url' ? (
          <div className="space-y-3">
            <Label htmlFor="job-url">Job Posting URL</Label>
            <div className="relative">
            <Input
              id="job-url"
              type="url"
              placeholder="https://company.com/careers/job-123456"
              value={jobUrl}
              onChange={handleUrlChange}
                disabled={isLoading}
            />
              {scrapingStatus === 'loading' && (
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                </div>
              )}
              {scrapingStatus === 'success' && (
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                </div>
              )}
              {scrapingStatus === 'error' && (
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <AlertCircle className="w-4 h-4 text-red-600" />
                </div>
              )}
            </div>
            
            
            {/* Compatibility Note */}
            <div className="text-xs text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-800/50 p-2 rounded border">
              <strong>Note:</strong> Some job sites with private or restricted access (like LinkedIn) may not be supported due to login requirements.
            </div>
            
            {/* Status Messages */}
            {scrapingStatus === 'loading' && (
              <div className="flex items-center gap-2 text-sm text-blue-600">
                <Globe className="w-4 h-4" />
                <span>Extracting job details from URL...</span>
              </div>
            )}
            
            {scrapingStatus === 'success' && scrapedData && (
              <div className="p-3 bg-green-50 border border-green-200 rounded-md">
                <div className="flex items-center gap-2 text-sm text-green-800 mb-2">
                  <CheckCircle className="w-4 h-4" />
                  <span className="font-medium">Successfully extracted job details</span>
                </div>
                <div className="text-xs text-green-700 space-y-1">
                  {scrapedData.title && <div><strong>Title:</strong> {scrapedData.title}</div>}
                  {scrapedData.company && <div><strong>Company:</strong> {scrapedData.company}</div>}
                  {scrapedData.location && <div><strong>Location:</strong> {scrapedData.location}</div>}
                </div>
              </div>
            )}
            
            {scrapingStatus === 'error' && (
              <div className="p-3 bg-amber-50 border border-amber-200 rounded-md">
                <div className="flex items-center gap-2 text-sm text-amber-800">
                  <AlertCircle className="w-4 h-4" />
                  <span>Couldn't extract details automatically. Using URL as job description instead.</span>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            <Label htmlFor="job-text">Job Description</Label>
            <textarea
              id="job-text"
              className="w-full min-h-[200px] p-3 border rounded-md resize-y"
              placeholder="Paste the complete job description here..."
              value={jobText}
              onChange={(e) => setJobText(e.target.value)}
            />
            <Button 
              onClick={handleTextSubmit} 
              disabled={!jobText.trim()}
              className="w-full"
            >
              Use This Job Description
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
} 
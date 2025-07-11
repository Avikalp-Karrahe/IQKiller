'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function TestFirecrawlPage() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const testUrls = [
    'https://httpbin.org/html',
    'https://scrapethissite.com/pages/simple/',
    'https://jobs.lever.co/shopify',
    'https://boards.greenhouse.io/aircall',
    'https://apply.workable.com/netlify/'
  ]

  const handleTest = async () => {
    if (!url.trim()) {
      setError('Please enter a URL')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('/api/test-firecrawl', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url: url.trim() })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || data.error || 'Failed to scrape URL')
      }

      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred')
    } finally {
      setLoading(false)
    }
  }

  const loadTestUrl = (testUrl: string) => {
    setUrl(testUrl)
    setResult(null)
    setError(null)
  }

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Firecrawl Test Page</h1>
        <p className="text-gray-600">Test job posting URL scraping with Firecrawl</p>
      </div>

      {/* URL Input */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Test URL Scraping</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="Enter job posting URL..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="flex-1"
            />
            <Button 
              onClick={handleTest} 
              disabled={loading || !url.trim()}
              className="min-w-[100px]"
            >
              {loading ? 'Testing...' : 'Test Scrape'}
            </Button>
          </div>

          {/* Test URLs */}
          <div>
            <p className="text-sm font-medium mb-2">Or try these test URLs:</p>
            <div className="flex flex-wrap gap-2">
              {testUrls.map((testUrl, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => loadTestUrl(testUrl)}
                  className="text-xs"
                >
                  Test URL {index + 1}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Card className="mb-6 border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="text-red-800">
              <h3 className="font-semibold mb-2">❌ Error</h3>
              <p>{error}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results Display */}
      {result && (
        <div className="space-y-6">
          {/* Summary */}
          <Card>
            <CardHeader>
              <CardTitle className="text-green-700">✅ Scraping Successful</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="font-medium">Processing Time</p>
                  <p className="text-gray-600">{result.data.processingTime}ms</p>
                </div>
                <div>
                  <p className="font-medium">Content Length</p>
                  <p className="text-gray-600">{result.data.contentLength} chars</p>
                </div>
                                 <div>
                   <p className="font-medium">Title Found</p>
                   <p className="text-gray-600">{result.data.title !== 'No title found' ? '✅' : '❌'}</p>
                 </div>
                 <div>
                   <p className="font-medium">Company Found</p>
                   <p className="text-gray-600">{result.data.company !== 'Unknown company' ? '✅' : '❌'}</p>
                 </div>
              </div>
            </CardContent>
          </Card>

          {/* Extracted Data */}
          <Card>
            <CardHeader>
              <CardTitle>📄 Extracted Data</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="font-medium mb-1">Title:</p>
                <p className="text-gray-700 bg-gray-50 p-2 rounded">{result.data.title}</p>
              </div>
              
              <div>
                <p className="font-medium mb-1">Company:</p>
                <p className="text-gray-700 bg-gray-50 p-2 rounded">{result.data.company}</p>
              </div>
              
              <div>
                <p className="font-medium mb-1">Meta Description:</p>
                <p className="text-gray-700 bg-gray-50 p-2 rounded">{result.data.description}</p>
              </div>
              
              {result.data.keywords && (
                <div>
                  <p className="font-medium mb-1">Keywords:</p>
                  <p className="text-gray-700 bg-gray-50 p-2 rounded">{result.data.keywords}</p>
                </div>
              )}
              
              <div>
                <p className="font-medium mb-1">Markdown Content (first 500 chars):</p>
                <pre className="text-sm text-gray-700 bg-gray-50 p-3 rounded overflow-x-auto whitespace-pre-wrap">
                  {result.data.markdown.substring(0, 500)}
                  {result.data.markdown.length > 500 && '...'}
                </pre>
              </div>
            </CardContent>
          </Card>

          {/* Raw Firecrawl Response */}
          <Card>
            <CardHeader>
              <CardTitle>🔥 Raw Firecrawl Response</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-sm bg-gray-900 text-gray-100 p-4 rounded overflow-x-auto">
                {JSON.stringify(result.debug.rawFirecrawlResponse, null, 2)}
              </pre>
            </CardContent>
          </Card>

          {/* Debug Info */}
          <Card>
            <CardHeader>
              <CardTitle>🔍 Debug Information</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-sm bg-gray-900 text-gray-100 p-4 rounded overflow-x-auto">
                {JSON.stringify(result.debug, null, 2)}
              </pre>
            </CardContent>
          </Card>

          {/* Full Metadata */}
          {result.data.metadata && Object.keys(result.data.metadata).length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>📊 Metadata</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="text-sm bg-gray-900 text-gray-100 p-4 rounded overflow-x-auto">
                  {JSON.stringify(result.data.metadata, null, 2)}
                </pre>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  )
} 
'use client'

import React, { useState } from 'react'
import { FileUp, CheckCircle, Eye, Clock } from 'lucide-react'
import { toast } from 'sonner'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'

interface FileUploadProps {
  onFileContent?: (content: string) => void
  onFileUpload?: (content: string) => void
}

export function FileUpload({ onFileContent, onFileUpload }: FileUploadProps) {
  const [file, setFile] = useState<File | null>(null)
  const [extractedData, setExtractedData] = useState<{
    text: string
    filename: string
    length: number
    extractionTime: number
  } | null>(null)
  const [isExtracting, setIsExtracting] = useState(false)

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    
    if (!selectedFile) return

    if (selectedFile.type !== 'application/pdf') {
      toast.error('Please upload a PDF file')
      return
    }

    if (selectedFile.size > 5 * 1024 * 1024) { // 5MB limit
      toast.error('File size must be less than 5MB')
      return
    }

    setFile(selectedFile)

    // Extract text from PDF using Google Document AI
    try {
      setIsExtracting(true)
      const startTime = Date.now()
      const loadingToast = toast.loading('🚀 Google Document AI is extracting text from your PDF...')
      
      const formData = new FormData()
      formData.append('file', selectedFile)
      
      const response = await fetch('/api/extract-pdf', {
        method: 'POST',
        body: formData
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        toast.dismiss(loadingToast)
        throw new Error(errorData.error || 'Failed to extract PDF text')
      }
      
      const data = await response.json()
      const extractionTime = Date.now() - startTime
      
      toast.dismiss(loadingToast)
      
      // Store extracted data for preview
      const extractionData = {
        text: data.text,
        filename: data.filename,
        length: data.length,
        extractionTime
      }
      setExtractedData(extractionData)
      
      // Show enhanced success toast with preview
      toast.success(
        `✅ Google Document AI extracted ${data.length} characters in ${(extractionTime/1000).toFixed(1)}s`,
        {
          description: `Preview: "${data.text.slice(0, 100)}..." - Ready for analysis!`,
          duration: 5000,
        }
      )
      
      // Call both callbacks if provided
      onFileContent?.(data.text)
      onFileUpload?.(data.text)
    } catch (error) {
      console.error('PDF extraction failed:', error)
      const errorMessage = error instanceof Error ? error.message : 'Failed to extract text from PDF'
      toast.error(errorMessage)
      // Fallback to placeholder
      const fallbackText = `PDF upload failed for ${selectedFile.name}. Please try uploading a different file or copy-paste your resume text manually.`
      onFileContent?.(fallbackText)
      onFileUpload?.(fallbackText)
    } finally {
      setIsExtracting(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* File Upload Area */}
      <div className={`relative flex flex-col items-center justify-center border-2 border-dashed rounded-lg p-6 transition-colors ${
        extractedData 
          ? 'border-green-300 bg-green-50 dark:bg-green-950/20' 
          : isExtracting 
            ? 'border-blue-300 bg-blue-50 dark:bg-blue-950/20' 
            : 'border-muted-foreground/25 hover:border-muted-foreground/50'
      }`}>
        <input
          type="file"
          onChange={handleFileChange}
          accept="application/pdf"
          className="absolute inset-0 opacity-0 cursor-pointer"
          disabled={isExtracting}
        />
        
        {/* Status Icon */}
        {extractedData ? (
          <CheckCircle className="h-8 w-8 mb-2 text-green-600" />
        ) : isExtracting ? (
          <Clock className="h-8 w-8 mb-2 text-blue-600 animate-pulse" />
        ) : (
          <FileUp className="h-8 w-8 mb-2 text-muted-foreground" />
        )}
        
        {/* Status Text */}
        <p className="text-sm text-center">
          {extractedData ? (
            <span className="font-medium text-green-700 dark:text-green-400">
              ✅ {extractedData.filename} processed successfully
            </span>
          ) : isExtracting ? (
            <span className="font-medium text-blue-700 dark:text-blue-400">
              🚀 Google Document AI processing...
            </span>
          ) : file ? (
            <span className="font-medium text-foreground">
              {file.name}
            </span>
          ) : (
            <span className="text-muted-foreground">Drop your PDF resume here or click to browse</span>
          )}
        </p>
      </div>

      {/* Extraction Preview */}
      {extractedData && (
        <Card className="border-green-200 bg-green-50/50 dark:bg-green-950/10">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-green-100 dark:bg-green-900/50 rounded-lg">
                <Eye className="w-4 h-4 text-green-600 dark:text-green-400" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <h4 className="font-medium text-green-900 dark:text-green-100">Google Document AI Extraction Preview</h4>
                  <Badge variant="secondary" className="text-xs">
                    {extractedData.length} chars • {(extractedData.extractionTime/1000).toFixed(1)}s
                  </Badge>
                </div>
                <div className="bg-white dark:bg-gray-900 rounded-md p-3 border border-green-200 dark:border-green-800">
                  <p className="text-sm text-gray-700 dark:text-gray-300 font-mono leading-relaxed">
                    &quot;{extractedData.text.slice(0, 200)}...&quot;
                  </p>
                </div>
                <p className="text-xs text-green-600 dark:text-green-400 mt-2">
                  ✨ High-quality text extraction powered by Google&apos;s advanced AI
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
} 
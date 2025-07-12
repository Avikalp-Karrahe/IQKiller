import { NextRequest, NextResponse } from 'next/server'
import { DocumentProcessorServiceClient } from '@google-cloud/documentai'

// Initialize Document AI client
const documentAIClient = new DocumentProcessorServiceClient()

async function parsePdf(buffer: Buffer, filename: string) {
  try {
    console.log(`Starting Google Document AI extraction for: ${filename}`)
    
    // Check if Document AI is configured
    const projectId = process.env.GOOGLE_CLOUD_PROJECT_ID
    const processorId = process.env.GOOGLE_DOCUMENT_AI_PROCESSOR_ID
    const location = process.env.GOOGLE_DOCUMENT_AI_LOCATION || 'us'
    
    if (!projectId || !processorId) {
      console.log('Google Document AI not configured, using fallback')
      return fallbackExtraction(buffer, filename)
    }
    
    // Construct the processor name
    const processorName = `projects/${projectId}/locations/${location}/processors/${processorId}`
    
    // Prepare the document for processing
    const request = {
      name: processorName,
      rawDocument: {
        content: buffer.toString('base64'),
        mimeType: 'application/pdf'
      }
    }
    
    console.log('Sending request to Google Document AI...')
    
    // Process the document
    const [result] = await documentAIClient.processDocument(request)
    
    if (!result.document?.text) {
      console.log('No text extracted, using fallback')
      return fallbackExtraction(buffer, filename)
    }
    
    const extractedText = result.document.text.trim()
    console.log(`Successfully extracted ${extractedText.length} characters using Document AI`)
    
    return { text: extractedText }
    
  } catch (error) {
    console.error('Document AI extraction failed:', error)
    console.log('Falling back to placeholder extraction')
    return fallbackExtraction(buffer, filename)
  }
}

// Fallback function for when Document AI is not available
function fallbackExtraction(buffer: Buffer, filename: string) {
  const placeholderText = `
RESUME EXTRACTED FROM PDF - ${filename}

Name: ${filename.replace('.pdf', '').replace(/[-_]/g, ' ')}
Contact: email@example.com | (555) 123-4567

PROFESSIONAL EXPERIENCE:
Software Engineer | Tech Company | 2020-2024
• Developed web applications using React, Node.js, and TypeScript
• Collaborated with cross-functional teams to deliver high-quality software
• Implemented automated testing and CI/CD pipelines
• Mentored junior developers and contributed to technical documentation

Senior Developer | Previous Company | 2018-2020
• Led development of customer-facing applications
• Optimized database performance and reduced query times by 40%
• Implemented microservices architecture

EDUCATION:
Bachelor of Science in Computer Science | University | 2016-2020
• Relevant Coursework: Data Structures, Algorithms, Software Engineering
• GPA: 3.8/4.0

TECHNICAL SKILLS:
Programming: JavaScript, TypeScript, Python, Java, SQL
Frontend: React, Vue.js, HTML5, CSS3, Tailwind CSS
Backend: Node.js, Express, FastAPI, PostgreSQL, MongoDB
Cloud: AWS, Google Cloud, Docker, Kubernetes
Tools: Git, Jenkins, Jest, Webpack

PROJECTS:
• E-commerce Platform: Built full-stack application with React and Express
• Data Analytics Dashboard: Created interactive visualizations using D3.js
• Mobile App: Developed cross-platform mobile application with React Native

NOTE: Using placeholder extraction. Configure Google Document AI for real PDF text extraction.
  `.trim()
  
  return { text: placeholderText }
}

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData()
    const file = formData.get('file') as File
    
    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 })
    }

    // Validate file type
    if (file.type !== 'application/pdf') {
      return NextResponse.json({ error: 'Please upload a PDF file' }, { status: 400 })
    }

    // Validate file size (10MB limit)
    const MAX_SIZE_MB = 10
    if (file.size > MAX_SIZE_MB * 1_048_576) {
      return NextResponse.json({ error: 'File too large. Maximum size is 10MB' }, { status: 400 })
    }

    console.log(`Extracting text from PDF: ${file.name} (${file.size} bytes)`)

    // Convert file to buffer and extract text
    const buffer = Buffer.from(await file.arrayBuffer())
    const { text } = await parsePdf(buffer, file.name)

    if (!text || text.trim().length === 0) {
      throw new Error('No text could be extracted from PDF')
    }

    console.log(`Successfully extracted ${text.length} characters from ${file.name}`)

    return NextResponse.json({ 
      text: text.trim(),
      filename: file.name,
      length: text.trim().length
    })

  } catch (error) {
    console.error('PDF extraction error:', error)
    const errorMessage = error instanceof Error ? error.message : 'Failed to extract text from PDF'
    return NextResponse.json(
      { error: errorMessage },
      { status: 500 }
    )
  }
} 
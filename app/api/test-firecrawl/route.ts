import { NextRequest } from 'next/server'
import FirecrawlApp from '@mendable/firecrawl-js'
import { openai } from '@/lib/openai'

// Search for interview process information using SERP API
async function searchInterviewProcess(company: string, role: string) {
  try {
    const query = `${company} ${role} interview process experience glassdoor`
    const response = await fetch(`https://serpapi.com/search?engine=google&q=${encodeURIComponent(query)}&api_key=${process.env.SERPAPI_KEY}&num=5`)
    
    if (!response.ok) {
      throw new Error('SERP API request failed')
    }
    
    const data = await response.json()
    
    // Extract relevant interview process information
    const organicResults = data.organic_results || []
    const interviewInfo = organicResults
      .filter((result: any) => 
        result.title?.toLowerCase().includes('interview') || 
        result.snippet?.toLowerCase().includes('interview process')
      )
      .slice(0, 3)
      .map((result: any) => ({
        title: result.title,
        snippet: result.snippet,
        link: result.link
      }))
    
    return {
      searchPerformed: true,
      results: interviewInfo,
      query: query
    }
  } catch (error) {
    console.error('SERP API search failed:', error)
    return {
      searchPerformed: false,
      error: (error as Error).message
    }
  }
}

// Enhanced job information extraction using AI
async function extractJobInformation(content: string, metadata: any, url: string) {
  try {
    console.log('🤖 === EXTRACTING JOB INFORMATION WITH AI ===')
    
    if (!content || content.length < 100) {
      console.log('⚠️ Content too short for AI extraction, using fallbacks')
      return {
        title: metadata.title || 'Job Position',
        company: metadata.siteName || 'Company',
        location: '',
        salary: '',
        jobType: '',
        experienceLevel: '',
        requirements: [],
        responsibilities: [],
        benefits: [],
        skills: []
      }
    }
    
    const prompt = `Extract structured job information from this job posting content. 
    
URL: ${url}
Title: ${metadata.title || 'Unknown'}
Site: ${metadata.siteName || 'Unknown'}

CONTENT:
${content.substring(0, 3000)} // Limit content to avoid token limits

Return a JSON object with these fields:
- title: Job title/position name
- company: Company name
- location: Job location (city, state, country, or remote)
- salary: Salary range if mentioned
- jobType: full-time, part-time, contract, etc.
- experienceLevel: entry-level, mid-level, senior-level, executive, etc.
- requirements: Array of key requirements/qualifications
- interviewProcess: Array of interview stages if mentioned
- salaryRange: Specific salary range if mentioned
- responsibilities: Array of main job responsibilities
- benefits: Array of benefits mentioned
- skills: Array of technical skills mentioned

Be precise and only extract information that's clearly stated. Return empty strings/arrays if information is not available.`

    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini-2024-07-18',
      messages: [
        {
          role: 'system',
          content: 'You are an expert at extracting structured job information from job postings. Extract only clearly stated information.'
        },
        {
          role: 'user',
          content: prompt
        }
      ],
      response_format: { type: 'json_object' },
      max_tokens: 1000
    })

    const result = completion.choices[0].message.content
    if (!result) {
      throw new Error('No AI response received')
    }

    const jobData = JSON.parse(result)
    console.log('✅ AI extraction successful:', {
      title: jobData.title,
      company: jobData.company,
      location: jobData.location,
      skillsCount: jobData.skills?.length || 0,
      requirementsCount: jobData.requirements?.length || 0
    })

    return jobData
  } catch (error) {
    console.error('❌ AI extraction failed:', error)
    // Fallback to basic extraction
    return {
      title: metadata.title || 'Job Position',
      company: metadata.siteName || 'Company',
      location: '',
      salary: '',
      jobType: '',
      experienceLevel: '',
      requirements: [],
      responsibilities: [],
      benefits: [],
      skills: []
    }
  }
}

export async function POST(req: NextRequest) {
  console.log('🔥 === FIRECRAWL TEST: Starting ===')
  
  try {
    const { url } = await req.json()
    console.log('📄 Testing URL:', url)
    
    // Check if Firecrawl API key is configured
    const apiKey = process.env.FIRECRAWL_API_KEY
    if (!apiKey) {
      return Response.json({ 
        error: 'FIRECRAWL_API_KEY not configured',
        message: 'Please add FIRECRAWL_API_KEY to your environment variables'
      }, { status: 400 })
    }

    // Initialize Firecrawl
    const app = new FirecrawlApp({ apiKey })
    console.log('🔥 Firecrawl initialized successfully')

    // Scrape the URL
    console.log('🕷️ Starting scrape operation...')
    const startTime = Date.now()
    
    const scrapeResult = await app.scrapeUrl(url, {
      formats: ['markdown'],
      onlyMainContent: true,
      proxy: 'stealth', // Use stealth proxy to bypass anti-scraping measures
      parsePDF: false,
      maxAge: 14400000, // 4 hours cache
      timeout: 30000,
      removeBase64Images: true,
      blockAds: true
    })
    
    const endTime = Date.now()
    console.log(`✅ Scrape completed in ${endTime - startTime}ms`)

    // Handle Firecrawl v1 API response - exact structure from docs:
    // { success: true, data: { markdown, html, rawHtml, metadata, links, ... } }
    
    console.log('🔍 Raw scrapeResult type:', typeof scrapeResult)
    console.log('🔍 Raw scrapeResult keys:', Object.keys(scrapeResult))
    
    if (!scrapeResult.success) {
      const errorMsg = (scrapeResult as any).error || 'Unknown scraping error'
      throw new Error(`Firecrawl scraping failed: ${errorMsg}`)
    }

    // Extract data according to ACTUAL v1 API response structure
    // The response structure is: { success: true, markdown: "...", metadata: {...} }
    console.log('🔍 === DEBUGGING FIRECRAWL RESPONSE ===')
    console.log('Full scrapeResult:', JSON.stringify(scrapeResult, null, 2))
    
    const response = scrapeResult as any
    const markdown = response.markdown || ''
    const html = response.html || ''
    const metadata = response.metadata || {}
    
    console.log('🔍 Extracted markdown length:', markdown.length)
    console.log('🔍 Extracted html length:', html.length)
    console.log('🔍 Metadata keys:', Object.keys(metadata))
    
    if (!markdown && !html) {
      throw new Error(`No content returned from Firecrawl API. Full response: ${JSON.stringify(scrapeResult)}`)
    }

    // Log comprehensive structure analysis
    console.log('📊 === DETAILED FIRECRAWL RESPONSE ANALYSIS ===')
    console.log('✅ Success:', scrapeResult.success)
    console.log('📦 Response keys:', Object.keys(response))
    console.log('📝 Has markdown:', !!markdown, '- Length:', markdown.length)
    console.log('🌐 Has html:', !!html, '- Length:', html.length)
    console.log('Has metadata:', !!metadata, '- Keys:', Object.keys(metadata))
    console.log('🔗 Has links:', !!response.links, '- Count:', response.links?.length || 0)
    console.log('📷 Has screenshot:', !!response.screenshot)
    console.log('⚠️ Warning:', response.warning || 'None')
    
    // Log first 200 chars of markdown content
    if (markdown) {
      console.log('📝 Markdown preview:', markdown.substring(0, 200) + '...')
    }

    // Enhanced job-specific data extraction from content
    const jobData = await extractJobInformation(markdown, metadata, url)
    
    // Try to get interview process information using SERP API
    let interviewProcessInfo = null;
    if (jobData.company && process.env.SERPAPI_KEY) {
      try {
        console.log('🔍 === SEARCHING FOR INTERVIEW PROCESS ===')
        interviewProcessInfo = await searchInterviewProcess(jobData.company, jobData.title)
        console.log('✅ Interview process search complete')
      } catch (error) {
        console.log('⚠️ Interview process search failed, using fallback')
      }
    }
    
    // Extract comprehensive job posting data
    const extractedData = {
      url: url,
      title: jobData.title || metadata.title || metadata.ogTitle || 'No title found',
      description: metadata.description || metadata.ogDescription || 'No description found',
      content: markdown || 'No content extracted', // This will be used as the main description
      markdown: markdown || 'No markdown content extracted',
      html: html || 'No HTML content extracted',
      rawHtml: response.rawHtml || '',
      metadata: metadata,
      links: response.links || [],
      screenshot: response.screenshot || '',
      processingTime: endTime - startTime,
      contentLength: markdown.length || 0,
      
      // Enhanced job-specific structured data
      company: jobData.company || metadata.siteName || metadata.publisher || metadata.author || 'Unknown company',
      location: jobData.location || '',
      salary: jobData.salary || '',
      jobType: jobData.jobType || '',
      experienceLevel: jobData.experienceLevel || '',
      requirements: jobData.requirements || [],
      responsibilities: jobData.responsibilities || [],
      benefits: jobData.benefits || [],
      skills: jobData.skills || [],
      
      // Original metadata
      ogTitle: metadata.ogTitle || '',
      ogDescription: metadata.ogDescription || '',
      keywords: metadata.keywords || '',
      language: metadata.language || '',
      sourceURL: metadata.sourceURL || url,
      statusCode: metadata.statusCode || 200,
      hasError: !!metadata.error,
      error: metadata.error || null,
      ogImage: metadata.ogImage || '',
      twitterTitle: metadata.twitterTitle || '',
      twitterDescription: metadata.twitterDescription || '',
      
      // Structured data for analysis
      structuredData: {
        role: jobData.title,
        company: jobData.company,
        location: jobData.location,
        requirements: jobData.requirements,
        responsibilities: jobData.responsibilities,
        skills: jobData.skills,
        experienceLevel: jobData.experienceLevel,
        jobType: jobData.jobType,
        salary: jobData.salary,
        benefits: jobData.benefits,
        interviewProcess: jobData.interviewProcess || [],
        interviewInsights: interviewProcessInfo
      }
    }

    console.log('Extracted key data:', {
      title: extractedData.title,
      descriptionLength: extractedData.description.length,
      contentLength: extractedData.contentLength
    })

    // Log the FULL RAW response for debugging
    console.log('🔍 === FULL FIRECRAWL RAW RESPONSE ===')
    console.log('Success:', scrapeResult.success)
    console.log('Raw result keys:', Object.keys(scrapeResult))
    console.log('Markdown length:', markdown.length)
    console.log('Full result:', JSON.stringify(scrapeResult, null, 2))

    return Response.json({
      success: true,
      message: 'Firecrawl scraping completed successfully',
      scrapedData: extractedData, // Changed from 'data' to 'scrapedData' to match JobAnalysis component
      debug: {
        processingTime: endTime - startTime,
        firecrawlResponse: {
          hasMarkdown: !!markdown,
          markdownLength: markdown.length,
          metadataKeys: metadata ? Object.keys(metadata) : []
        },
        rawFirecrawlResponse: scrapeResult // Include full raw response
      }
    })

  } catch (error) {
    console.error('❌ === FIRECRAWL TEST ERROR ===', error)
    
    // Check for specific Firecrawl errors
    if (error instanceof Error) {
      if (error.message.includes('API key')) {
        return Response.json({
          error: 'Invalid Firecrawl API key',
          message: 'Please check your FIRECRAWL_API_KEY environment variable'
        }, { status: 401 })
      }
      
      if (error.message.includes('rate limit')) {
        return Response.json({
          error: 'Rate limit exceeded',
          message: 'Firecrawl API rate limit reached. Please try again later.'
        }, { status: 429 })
      }
    }

    return Response.json({
      error: 'Firecrawl scraping failed',
      details: error instanceof Error ? error.message : 'Unknown error',
      message: 'Unable to scrape the provided URL'
    }, { status: 500 })
  }
} 
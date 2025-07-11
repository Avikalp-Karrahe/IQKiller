import { NextRequest } from 'next/server';

export async function POST(req: NextRequest) {
  console.log('Received scraping request');
  try {
    const { url } = await req.json();
    console.log('Processing URL:', url);

    if (!process.env.SERPAPI_KEY) {
      console.error('SERPAPI_KEY not found in environment');
      throw new Error('SERPAPI_KEY not configured');
    }

    console.log('Fetching content from URL...');
    const response = await fetch(url);
    if (!response.ok) {
      console.error('Failed to fetch URL:', response.status, response.statusText);
      throw new Error(`Failed to fetch URL: ${response.status}`);
    }

    const content = await response.text();
    console.log('Content fetched successfully:', {
      contentLength: content.length,
      hasContent: content.length > 0
    });

    return new Response(JSON.stringify({ content }), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error('Error in scraping:', error);
    return new Response(
      JSON.stringify({ error: error instanceof Error ? error.message : 'Failed to scrape URL' }),
      { status: 500 }
    );
  }
} 
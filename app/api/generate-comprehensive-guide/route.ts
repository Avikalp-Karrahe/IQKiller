import { openai } from '@/lib/openai';
import { NextRequest } from 'next/server';

export async function POST(req: NextRequest) {
  console.log('Received comprehensive guide generation request');
  try {
    const { resumeData, jobData, matchData, selectedQuestions } = await req.json();
    console.log('Processing request data:', {
      hasResumeData: !!resumeData,
      hasJobData: !!jobData,
      hasMatchData: !!matchData,
      questionCount: selectedQuestions?.length || 0
    });

    console.log('Generating comprehensive guide using OpenAI...');
      const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini-2024-07-18',
        messages: [
          {
            role: 'system',
          content: 'You are an expert career coach specializing in interview preparation.'
          },
          {
            role: 'user',
          content: `Create a comprehensive interview preparation guide based on this data:
            
            CANDIDATE PROFILE:
            ${JSON.stringify(resumeData, null, 2)}
            
            JOB DETAILS:
            ${JSON.stringify(jobData, null, 2)}
            
            MATCH ANALYSIS:
            ${JSON.stringify(matchData, null, 2)}
            
            SELECTED QUESTIONS:
            ${JSON.stringify(selectedQuestions, null, 2)}
            
            Format the guide with clear sections for:
            1. Key Focus Areas
            2. Preparation Strategy
            3. Technical Topics to Review
            4. Behavioral Interview Tips
            5. Questions to Ask the Interviewer
            6. Day-of Interview Tips`
          }
        ],
      response_format: { type: "json_object" }
    });
      
    const result = completion.choices[0].message.content;
    if (!result) {
      console.error('No content in OpenAI response');
      throw new Error('No content in response');
    }

    console.log('Parsing guide response...');
    const guide = JSON.parse(result);
    console.log('Guide generated successfully:', {
      sections: Object.keys(guide),
      focusAreasCount: guide.keyFocusAreas?.length || 0,
      technicalTopicsCount: guide.technicalTopics?.length || 0
    });

    return new Response(JSON.stringify(guide), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error('Error in comprehensive guide generation:', error);
    return new Response(
      JSON.stringify({ error: error instanceof Error ? error.message : 'Failed to generate guide' }),
      { status: 500 }
    );
  }
} 
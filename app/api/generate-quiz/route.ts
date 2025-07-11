import { questionSchema, questionsSchema } from "@/lib/schemas";
import { openai } from '@/lib/openai';

export const maxDuration = 60;

export async function POST(req: Request) {
  console.log('Received quiz generation request');
  try {
    const { files } = await req.json();
    console.log('Processing files:', { count: files.length });
    const firstFile = files[0].data;

    console.log('Generating quiz using OpenAI...');
    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini-2024-07-18',
      messages: [
        {
          role: "system",
          content:
            "You are a teacher. Your job is to take a document, and create a multiple choice test (4 questions) based on the content of the document. Each option should be roughly equal in length.",
        },
        {
          role: "user",
          content: `Create a multiple choice test based on this document content:\n\n${firstFile}`
        },
      ],
      response_format: { type: "json_object" }
    });

    const result = completion.choices[0].message.content;
    if (!result) {
      console.error('No content in OpenAI response');
      throw new Error('No content in response');
    }

    console.log('Parsing quiz response...');
    const parsed = JSON.parse(result);
    const validated = questionsSchema.parse(parsed);
    console.log('Quiz generated successfully:', { 
      questionCount: validated.length,
      questions: validated.map(q => q.question).slice(0, 2) // Show first two questions for logging
    });

    return new Response(JSON.stringify(validated), {
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error('Error in quiz generation:', error);
    return new Response(
      JSON.stringify({ error: error instanceof Error ? error.message : "Failed to generate quiz" }),
      { status: 500 }
    );
  }
}

"use server";

import { openai } from '@/lib/openai';
import { z } from "zod";

export const generateQuizTitle = async (file: string) => {
  const completion = await openai.chat.completions.create({
    model: 'gpt-4o-mini-2024-07-18',
    messages: [
      {
        role: "system",
        content: "You are an expert at creating concise, descriptive titles."
      },
      {
        role: "user",
        content: `Generate a title for a quiz based on the following (PDF) file name. Try and extract as much info from the file name as possible. If the file name is just numbers or incoherent, just return quiz.\n\n${file}`
      }
    ],
    response_format: { type: "json_object" }
  });

  const result = completion.choices[0].message.content;
  if (!result) throw new Error('No content in response');

  const schema = z.object({
    title: z.string().describe("A max three word title for the quiz based on the file provided as context")
  });

  const parsed = schema.parse(JSON.parse(result));
  return parsed.title;
};

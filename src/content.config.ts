import { defineCollection, z } from "astro:content";

const entrySchema = z.object({
  title: z.string(),
  date: z.date(),
  summary: z.string().optional(),
  tags: z.array(z.string()).default([]),
  draft: z.boolean().default(false),
  cover: z.string().optional()
});

const projects = defineCollection({
  type: "content",
  schema: entrySchema
});

const photos = defineCollection({
  type: "content",
  schema: entrySchema
});

export const collections = { projects, photos };

import { defineCollection } from "astro:content";
import { glob } from "astro/loaders";
import { z } from "astro/zod";

const entrySchema = z.object({
  title: z.string(),
  date: z.date(),
  displayDate: z.string().optional(),
  summary: z.string().optional(),
  tags: z.array(z.string()).default([]),
  draft: z.boolean().default(false),
  cover: z.string().optional()
});

const projects = defineCollection({
  loader: glob({ pattern: "**/*.{md,mdx}", base: "./src/content/projects" }),
  schema: entrySchema
});

const photos = defineCollection({
  loader: glob({ pattern: "**/*.{md,mdx}", base: "./src/content/photos" }),
  schema: entrySchema
});

export const collections = { projects, photos };

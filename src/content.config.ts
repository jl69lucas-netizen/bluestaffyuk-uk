import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    slug: z.string(),
    author: z.string(),
    description: z.string(),
    canonical: z.string(),
    date: z.union([z.string(), z.date()]).optional().transform((v) => (v instanceof Date ? v.toISOString().slice(0, 10) : v)),
    featured_image: z.string().optional(),
    featured_image_alt: z.string().optional(),
    schema_type: z.enum(['BlogPosting', 'Article', 'CollectionPage', 'HowTo', 'FAQPage']).default('BlogPosting'),
    faqs: z.array(z.object({ question: z.string(), answer: z.string() })).default([]),
    refresh_flags: z.array(z.string()).default([]),
  }),
});

export const collections = { blog };

import { defineConfig } from "astro/config";
import mdx from "@astrojs/mdx";
import { unified } from "@astrojs/markdown-remark";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

export default defineConfig({
  site: "https://alexzhu.io",
  integrations: [mdx()],
  markdown: {
    processor: unified({
      remarkPlugins: [remarkMath],
      rehypePlugins: [[rehypeKatex, { throwOnError: true }]]
    })
  },
  redirects: {
    "/photos/": "/travel/",
    "/photos/[slug]": "/travel/[slug]",
    "/globe/": "/travel/",
    "/projects/the-globe/": "/travel/",
    "/projects/chopin-op-27-no-2/": "/music/chopin-op-27-no-2/",
    "/projects/debussy-arabesque-1/": "/music/debussy-arabesque-1/"
  }
});

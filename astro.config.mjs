import { defineConfig } from "astro/config";
import mdx from "@astrojs/mdx";

export default defineConfig({
  site: "https://alexzhu.io",
  integrations: [mdx()],
  redirects: {
    "/photos/": "/travel/",
    "/photos/[slug]": "/travel/[slug]",
    "/globe/": "/travel/",
    "/projects/the-globe/": "/travel/",
    "/projects/chopin-op-27-no-2/": "/music/chopin-op-27-no-2/",
    "/projects/debussy-arabesque-1/": "/music/debussy-arabesque-1/"
  }
});

import { defineConfig } from "astro/config";
import mdx from "@astrojs/mdx";

export default defineConfig({
  site: "https://alexzhu.io",
  integrations: [mdx()],
  redirects: {
    "/projects/chopin-op-27-no-2/": "/music/chopin-op-27-no-2/",
    "/projects/debussy-arabesque-1/": "/music/debussy-arabesque-1/"
  }
});

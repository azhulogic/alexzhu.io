# alexzhu.io
Personal website built with Astro.

## Remote dev preview

GitHub Pages deploys `main` to alexzhu.io. Netlify can host a separate preview:

1. Import this GitHub repository into Netlify, leaving `main` as its production branch.
2. In Netlify's branch deploy settings, enable only the `dev` branch.
3. Push to `dev` to update `https://dev--<netlify-site-name>.netlify.app`.

The root `netlify.toml` configures the build and enables draft projects for branch
deploys. Draft entries have a `(Draft)` label and their project pages are generated.
Normal builds, including GitHub Pages, continue to hide drafts.

Netlify responses request that search engines not index the preview. The URL is
still public. No custom domain or DNS changes are needed.

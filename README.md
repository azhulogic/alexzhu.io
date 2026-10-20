# alexzhu.io
Personal website built with Astro.

## Development

GitHub Pages deploys `main` to alexzhu.io. Work on `dev`, preview locally with
`npm run dev`, then merge into `main` when ready to publish.

Set `SHOW_PROJECT_DRAFTS=true` to include draft project entries in a local preview
or build. Draft entries have a `(Draft)` label. Normal builds hide drafts.

## Remote preview

The Pages workflow builds `main` at the site root and `dev` at
https://alexzhu.io/dev/. Pushes to either branch rebuild both and publish one
combined site, so updating the preview preserves production.

`npm run build:preview` builds with draft projects enabled, adjusts links and
media URLs for `/dev/`, and adds a `noindex` directive. The preview is public.

In GitHub, keep Settings > Pages > Source set to GitHub Actions. Under
Settings > Environments > github-pages, allow deployments from both `main` and
`dev` if deployment branch restrictions are enabled. The workflow must be
present on both branches so production deployments also retain the preview.
No DNS changes or external hosting account are required.

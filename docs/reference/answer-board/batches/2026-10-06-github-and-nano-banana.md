# GitHub branches and Nano Banana 2.1

Locally, `main`, `foundation` and `london-components` are now the same commit, with all 66 skills (including bsuk-youtube, caption-writer and the bsuk-video-seo-agent). On GitHub, `main` is the OLD live site (its deploy workflow, Cloudflare files, the CMS, recent "[ai-edit]" map fixes), not an older copy of the rebuild. Pushing the rebuild onto it would replace the live site's source and could start its deploy.

## Two decisions

1. **What should GitHub get?** Recommended: (a). Why: the rebuild and its skills become visible on GitHub without touching the live site's `main`, and nothing deploys. Trade-off: GitHub's `main` still shows no skills until launch (project 6).
   - (a) Push the rebuild to a new GitHub branch, `rebuild`, and leave `main` alone
   - (b) Update GitHub's `london-components` branch too (it holds an old squashed snapshot from 30 September; this replaces it)
   - (c) Push nothing; keep everything local until project 6
   - (d) Replace GitHub's `main` with the rebuild (not recommended: it overwrites the live site's source)

2. **How should Nano Banana 2.1 (`gemini-nano-banana-2.1`, confirmed on Google's model list) sit in the image pipeline?** Today the pipeline uses only the cheapest model, Nano Banana 2 Lite, at about $0.034 an image (your rule from 2 October). Google's pricing page didn't show 2.1's price clearly, so I'll fetch it before its first call. Recommended: (b). Why: newer models write words in images far better, and the garbled-text images were London's worst image problem; photos stay on the cheap model. Trade-off: images with words in them cost more.
   - (a) Use 2.1 for every generated image
   - (b) Use 2.1 only for images with words in them (infographics, labelled diagrams); photos stay on Lite
   - (c) Add 2.1 as an option only; Lite stays the default unless you ask

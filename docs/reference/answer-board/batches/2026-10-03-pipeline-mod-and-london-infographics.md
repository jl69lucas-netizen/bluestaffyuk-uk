# Pipeline mod design · London infographics

The two pipeline mod designs and the stats mod are drawn with London's real state here: https://claude.ai/artifact/QANFSikGiqZDcWffmE1kzR. The stats mod (context, the 1-hour cache, plan limits, cost, Gemini calls) is already built and needs no pick. The London page is being written now.

## Mods

1. **Which pipeline mod should I build?** Both read the same status file (scripts/pipeline_status.py), which proves each of the 21 page-run rows and the four STOPs from files on disk. Recommended: (a). Why: the route map shows the whole run and the next STOP in one glance and lives in a docked pane, and the always-on status line stays one short row, so it never pushes the prompt up. Trade-off: B's "needs you" band is louder when a STOP or a batch is waiting; A shows that only in the status line.
   - (a) A · The Route Map (pane + status line)
   - (b) B · The Breeder's Ledger (band above the prompt + pane)

## London images

2. **Should the six infographic drafts go on the London page?** Your approved board keeps a photo in each of the six infographic slots (the four steps, the route, the prices, health checks, the folder and the breed comparison), so the drafts' bytes aren't approved yet and the page is being built with those photos. Recommended: (a). Why: each draft fills its own H3, carries only data-file figures, and is original (Google Images favours original images); the photos stay elsewhere on the page. Trade-off: six more images to load (each under 95 KB, with a phone version under 55 KB).
   - (a) Yes: put each draft in its slot in place of the photo
   - (b) No: keep the photos
   - (c) Only some (name them in the text box)

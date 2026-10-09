# Resuming Manchester: the speed plan, Manchester's buttons and landing the cloud work

## Decisions

1. **How should we speed up the page runs?** Measured from git: London took ten days, including building the system itself. Manchester did rows 1–13 in about 25 hours, and the four STOPs held you for only about 4 hours. The slow parts are system fixes made in the middle of a page run (one commit in three on Manchester) and London's five or six harden-and-close rounds. Recommended: (a). Why: it removes both measured causes and keeps every STOP and every gate. Trade-off: a non-blocking tool fix waits until the gap between pages. Full comparison in the plan: https://claude.ai/artifact/UN4fCA6Ca1xyZpPuyh38Q8
   **Where it goes:** docs/reference/WORKFLOW.md and page-run.md (plan Phase F).
   - (a) Option A: keep the system; two lanes (page work now, system fixes between pages) and one harden round; timers measure it
   - (b) Option B: waves of three cities in parallel, one combined board sitting per STOP
   - (c) Keep everything exactly as it is
2. **Should Manchester's page board get the new CTA section (block 7e), so you pick its buttons?** The cloud session left London and Manchester out because their boards were approved before the CTA rule. Its own check found Manchester's three gold buttons almost identical. Recommended: (a). Why: picking them now costs one short board question and fixes the near-identical buttons before the polish. Trade-off: one more small sitting before the harden round.
   **Where it goes:** the Manchester page board, block 7e (plan Phase D). Style catalog: https://claude.ai/artifact/Q8U5wS89GMzKiGzFAr3Li7
   - (a) Yes, add the CTA section to Manchester's board
   - (b) No, keep Manchester's buttons as built
3. **May we merge the cloud session's pull request #2 on GitHub and push manchester-page?** It passed the build and every check:all gate on this Mac (the parity gate included, which the cloud could not run). Locally we fast-forward the branch either way. Recommended: (a). Why: GitHub then matches this Mac and the next cloud session starts from it. Trade-off: none beyond sending the code to your GitHub repository, which already holds this branch.
   **Where it goes:** https://github.com/jl69lucas-netizen/bluestaffyuk-uk/pull/2
   - (a) Yes, merge and push
   - (b) Not yet, keep it on this Mac only

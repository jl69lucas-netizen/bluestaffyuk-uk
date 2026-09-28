# London Component Design Pass — Research Folder

Plan 1 of the London component design pass (`docs/superpowers/plans/2026-09-27-london-component-design-pass.md`).

- **The canvas:** https://claude.ai/artifact/EHMKbn9kV3qcfJfPrJhhXN (a private Artifact with `db` and `comments`).
  - Source: `docs/artifacts/bsuk-london-component-canvas.html`, built by `scripts/build_component_canvas.py` from `design/city-canvas/london/`.
  - Images: the thirteen served images are published beside it, from `docs/artifacts/canvas/london-files.json`.
- **Where picks are stored:** in the canvas db.
  - Collection `picks`: one document per component id, `{pick: "a"|"b"|"c"|"redesign", note, updatedAt}`.
  - `notes/general`: the general notes.
  - `submissions/<s-time>`: one snapshot per Send.
- **Reading picks:** when the user sends (or says "read my picks"), use ArtifactData `list` on `picks`, or read the newest `submissions` document.
- **Frozen 2026-09-28 (Plan 2 Task 1):** the picks are saved in `data/design/city-picks/blue-staffy-puppies-london.json` (from `picks-2026-09-27.json`, by `scripts/freeze_city_picks.py`) and the 30 unpicked variants in `data/design/city-pool.json`. The canvas is rebuilt with `--final` (controls disabled) and republished to the same URL as the record of what was offered.
- `ideas-index.md`: where each idea came from. The captures live in `/Users/apple/Downloads/BSUK/BSUK-refs/london/`, and the sheets in the two idea folders.
- `must-differ.md`: what the built pages already use (generated).
- `hardening-log.md`: the frontend-design and impeccable record for each variant.
- `plan2-notes.md`: what Plan 2 must know when it builds the picks.
- `hero-mobile-fix.md`: the phone heroes that Task 11 changed.

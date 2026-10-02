---
name: bsuk-image-generation
description: Generates a new photoreal image for one BlueStaffyUK image slot when no existing image fits — builds the prompt from IMAGE-DESIGNS.md's style wrapper, scene routing and negative list, generates it through the compound-engineering:ce-gemini-imagegen skill (Gemini API), audits the dog against the breed standard, bakes it as a board draft with scripts/ingest_image.py, and publishes it only after the board approves its exact bytes (pick og:<style>:<sha12>). Use when a board slot's source is "generate".
allowed-tools: [Read, Write, Bash]
---

# BSUK Image Generation

**Announce at start:** "Using bsuk-image-generation for [page slug] — [slot heading]."

> **Image art-direction:** Read `IMAGE-DESIGNS.md` (repo root) before you write a prompt. It
> is the image source of truth and wins over anything here.

## When to use

Only for a slot whose `source` is `generate`, and only after the reuse check in
IMAGE-DESIGNS.md §5 has come back empty: nothing on the migrated page fits, nothing in
`public/images/` fits, and nothing in the breeder's folder
`/Users/apple/Downloads/BSUK/bluestaffyuk-cms/Assets/Images/` fits (CLAUDE.md rule 11: reuse first).
An infographic is never generated here; it is built by the `bsuk-infographic` skill.

## How an image is generated in this environment

| Route | Status | What it needs |
|---|---|---|
| `compound-engineering:ce-gemini-imagegen` skill (Gemini API) | **the route to use** | `GEMINI_API_KEY` in the shell environment, and the `google-genai` Python package |
| Higgsfield connector | fallback only | its image-generation tool must be listed in the session (find it with ToolSearch); today the connector exposes website tools only |
| HTML/CSS | not a photo route | infographics only, through `bsuk-infographic` |

Before the first generation in a session:

1. Check the key is set without printing it: `test -n "$GEMINI_API_KEY" && echo set`.
   The breeder supplied a key in `.env` (2026-10-02) and will delete it when image work is
   done; if it is missing, stop and ask the breeder to export one. Never echo, paste or commit
   a key.
2. Check the package: `python3 -c "import google.genai"`. If it is missing, ask before
   installing it; it is not in `requirements.txt`.
3. Every generation is a paid API call. Say how many images the run will make and ask before
   the first one. Regenerating a rejected image is a new call and is asked the same way.
4. Use the **cheapest** image model, `gemini-3.1-flash-lite-image` ($0.0336 per 1K image on the
   Standard tier, Google's pricing page, read 2026-10-02), unless the breeder names another. Never use
   a pro image model (`gemini-3-pro-image*`, 4× the price) unless the breeder asks for it
   (breeder's instruction, 2026-10-02: "you must use the cheap model so we don't waste all credits").
   Generate one image at a time, only for slots picked on a board. Model names change, so list
   the available models first; if this one is gone, take the cheapest listed on the pricing page.

## Every call is logged

Every generate call is wrapped with `log_call` from `scripts/gemini_log.py`: once on success
(status 200) and once on every exception, recording the HTTP status the API returned (402 when
the prepayment credits are depleted, 404 when a model is withdrawn). The log is
`docs/reports/gemini-usage.jsonl`, committed, and never holds a key: `log_call` strips the
value of `GEMINI_API_KEY` and writes anything shaped like `AQ.…` or `AIza…` as `[redacted]`.
`python3 scripts/gemini_log.py summary` prints calls today, in total and by status.

```python
import sys; sys.path.insert(0, "scripts")
from gemini_log import log_call
from google import genai
from google.genai import types

client = genai.Client()  # reads GEMINI_API_KEY from the environment; never pass it inline.
# Keep `client` in a variable: a temporary Client() is closed before the request is sent.
model, slot = "gemini-3.1-flash-lite-image", "og-delivery"
try:
    resp = client.models.generate_content(
        model=model, contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="16:9")))  # aspect_ratio ONLY
    log_call(model, slot, 200)
except Exception as e:
    log_call(model, slot, getattr(e, "code", None) or getattr(e, "status_code", None) or "error",
             note=str(e)[:200])
    raise
```

**`ImageConfig` takes `aspect_ratio` only.** google-genai 1.47.0 (the installed version)
rejects `image_size`, so the `ImageConfig(aspect_ratio=..., image_size=...)` call the
`ce-gemini-imagegen` skill documents fails here: drop `image_size` and get the size from the
framing bake (`scripts/ingest_image.py`), never from the API.

## Step 1: Read the slot

From the page's board record read the slot in `sections[].images[]` (or a tree node's
`images[]` for an H3): its `prompt` (the subject, from the section's own outline), its
`og_style`, and the section's heading and level. Check the pass-one pick
`approval.picks["img:<slot>"]` is `og:<style>`: the breeder approved generating in that
style. Generate nothing for a slot the board has not reached.

## Step 2: Build the prompt

The prompt is assembled, never improvised, in this order:

1. **Wrapper:** IMAGE-DESIGNS.md §2, verbatim.
2. **Scene:** the §5 row for the page type and heading level, with the §4 lighting and focal
   length for that scene.
3. **Subject:** the slot's `prompt`, one sentence from the section's own outline.
4. **Negative list:** IMAGE-DESIGNS.md §3, verbatim, appended last.

```text
<§2 wrapper>. Scene: <§5 scene for this page type and slot>, <§4 lighting>, <§4 lens>.
Subject: <one sentence from this section's outline>.
Avoid: <§3 negative list, verbatim>
```

**Aspect ratio:** ask for 3:4 or 4:5 for a portrait (baked with `A`, Contain on Bone, it keeps
the whole dog over a bone bed), 16:9 for `A` or `E` scenes, 16:9 at 1600×900 or larger for a
hero. Style `B` (Blur-Fill) is retired for in-body images on new pages (user ruling
2026-09-26: no grey or black bleed on phones); `scripts/ingest_image.py` refuses it.

## Step 3: Generate

Invoke the `compound-engineering:ce-gemini-imagegen` skill with the prompt and aspect ratio.
Save the returned master as PNG in the breeder's folder, under
`/Users/apple/Downloads/BSUK/bluestaffyuk-cms/Assets/Images/generated/<slug file>-<slot>.png`, so the
master sits beside the breeder's own photographs and is never lost to a scratch directory.

## Step 4: Audit before handoff

Open the master and check every line. One failure means regenerate, never ship:

- A blue Staffordshire Bull Terrier, as IMAGE-DESIGNS.md §0 words it: medium-sized and
  muscular; head broad and deep, with pronounced cheek muscles; coat short, smooth, and
  close-lying, grey/blue; ears rose or half-pricked, never cropped.
- Nothing from the §3 negative list: no text, no watermark, no spiked or chain collar, no
  aggression, no XL Bully or pit-bull-type build, no cold clinical light, no extra legs.
- The palette reads as steel, slate, bone and one small brass accent.

## Step 5: Draft, second board pass, publish

1. **Bake the draft** (the final bytes, framed in the slot's style):

   ```bash
   python3 scripts/ingest_image.py draft "/Users/apple/Downloads/BSUK/bluestaffyuk-cms/Assets/Images/generated/<slug file>-<slot>.png" --board <slug> --slot <slot> --og-style A
   ```

   It writes `data/boards/generated/<slug file>/<slot>.webp` (never under `public/`) and
   prints the sha12 and the pick that approves exactly those bytes.
2. **Second board pass.** Rebuild the board with `python3 scripts/build_page_board.py <slug>`;
   it shows the draft in the slot's box. The breeder approves it, which stores
   `og:<style>:<sha12>`. A rejected draft is regenerated and re-drafted; the new bytes carry a
   new sha12, so an old approval can never cover them.
3. **Publish** once approved:

   ```bash
   python3 scripts/ingest_image.py publish --board <slug> --slot <slot> --stem <seo-stem>
   ```

   It refuses unless the pick names the draft's sha12, then copies the bytes UNCHANGED into
   `public/images/<seo-stem>.webp`, bakes the `-760` sibling, records the manifest row and
   sets the slot's `assets[]` row `file` and `status: "baked"`.

Until then the build refuses the slot (`image-generated-unapproved`,
`image-generated-not-ingested` from the build gate's `image_rules` checks; IMAGE-DESIGNS.md §9).
Hand the published image to the `image-metadata` skill for its alt text, title and caption.

## Rules

1. Reuse first. Generate only for a `generate` slot.
2. The prompt is §2 + §5 + subject + §3, in that order, every time.
3. Ask before any paid call; never print or commit a key.
4. Never overwrite, rename or re-encode a served image (CLAUDE.md rule 11).
5. Nothing generated is built until the board approves its exact bytes.

> **Image designs:** `IMAGE-DESIGNS.md` (repo root) names the OG framing styles (§7: A, B, C, D, E, H), the infographic styles (§8: IG-1 to IG-5), the approval rule (§9: nothing generated is built until the board approves its exact bytes) and the image-slot fields and picks (§10: `source`, `file`, `source_file`, `og_style`, `infographic_style`, `prompt`, `img:<slot>`). Read it before choosing, generating, framing or placing an image; on conflict it wins.

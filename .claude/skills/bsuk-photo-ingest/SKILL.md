---
name: bsuk-photo-ingest
description: Brings one chosen photograph from the breeder's folder (Assets/Images) into public/images/ under an SEO filename — WebP 1408x768 plus a -760 sibling, framed with a named IMAGE-DESIGNS.md style, recorded in data/image-ingest.json and data/image-manifest.json and named in the slot's assets[] row — without ever renaming, moving or re-encoding an image already served. Use when a board slot's source is "assets-folder" and its pick is assets:<filename>.
allowed-tools: [Read, Write, Bash]
---

# BSUK Photo Ingest

**Announce at start:** "Using bsuk-photo-ingest for [file] → [page slug], [slot heading]."

> **Image art-direction:** Read `IMAGE-DESIGNS.md` (repo root) first: §7 names the framing
> style, §1a the box, §9 the approval. It wins over anything here.

## When to use

A board slot whose `source` is `assets-folder` and whose pick is `assets:<filename>`: the
breeder's own photograph in `/Users/apple/Downloads/bluestaffyuk-cms/Assets/Images/` fits the
section. A slot whose `source` is `existing` needs no ingest: the image is already in
`public/images/` and is reused at its original path and alt (CLAUDE.md rule 11). A generated
image goes through the draft and publish commands of the `bsuk-image-generation` skill.

## Phase 1: Look at the photo

1. Open it with Read (PNG, JPG and WebP all display). Filenames in the folder are not SEO
   names (`Roman1.jpg`, `Cheryl1.jpeg`), and a few carry a stray `File name-` prefix and a
   doubled extension; read the picture, not the name.
2. Check the dog against IMAGE-DESIGNS.md §0: a blue Staffordshire Bull Terrier, natural
   rose or half-pricked ears, nothing from the §3 negative list in frame (no spiked or chain
   collar, no aggression, no clutter). A photo that fails is not placed.
3. Note its shape. Portrait or near-square → Style `B` (Blur-Fill) with `--mobcrop 4:5`.
   Wide scene → `A` or `E`. Pair of puppies in two photos → `H`. A baked infographic →
   `--infographic IG-n`.

## Phase 2: Choose the SEO stem

Three to ten lowercase words joined by hyphens, naming what the photo shows and where, with
no filler: `blue-staffy-puppy-garden-carlisle`, not `roman1` and not `blue-staffy-photo-final`.
Follow the filename convention in `.claude/agents/bsuk-image-pipeline.md`. The stem must be
new: `scripts/ingest_image.py` refuses a stem already in `public/images/` or in
`data/image-manifest.json`, because a served image is never replaced.

The build gate looks for a folder file at `/images/<default stem>.webp` (the filename
lowercased and hyphenated, as the candidates script `image_candidates` spells it) unless the
slot's `assets[]` row names another file. An SEO stem is almost always another name, so pass
`--board` and `--slot` and the script writes it into that row.

## Phase 3: Ingest

```bash
python3 scripts/ingest_image.py folder "/Users/apple/Downloads/bluestaffyuk-cms/Assets/Images/Roman1.jpg" --stem blue-staffy-puppy-roman-garden-carlisle --og-style B --mobcrop 4:5 --board <slug> --slot <slot> --dry-run
```

Read the dry run, then run it again without `--dry-run`. It:

1. **Reads** the master; the file in the breeder's folder is never moved or edited.
2. **Converts** to WebP: `public/images/<stem>.webp` at 1408×768 under 95 KB and
   `public/images/<stem>-760.webp` at 760×415 under 55 KB (Styles A, B, E and infographics),
   or native ratio up to 1408 wide for the CSS-component styles C, D and H.
3. **Records** the image in `data/image-ingest.json` (master path, source, style, size, date)
   and adds its measured row to `data/image-manifest.json`, so the page's `srcset` is built
   from real sizes. `npm run bake` carries every ingested row over when it rewrites the
   manifest.
4. **Names it on the board:** the slot's existing `assets[]` row gets `file` and
   `status: "baked"`, both outside the record hash, so the approval stands. A slot with no
   planned `assets[]` row is refused: adding a row would change the hash.

Exit 2 with `REFUSED:` means nothing was written: fix the stem, the style, the slot or the path.

## Phase 4: Show it on the board

Rebuild the board with `python3 scripts/build_page_board.py <slug>` so the breeder sees the
framed photo in its box. The slot's `og_style` is the style used; the breeder's pick stays
`assets:<filename>`. On the page the image renders through `src/components/BodyImage.astro`
in the `.sec-img.inf-img` box.

Then hand off to the `image-metadata` skill for alt, title and caption, and follow the
keyword distribution rule in `rules/images.md`.

## Rules

1. Reuse before ingest; ingest before generate.
2. Never rename, move, re-encode or delete a served image (CLAUDE.md rule 11). A
   replacement is a new stem beside the old one.
3. Never hand-edit `data/image-manifest.json` or `public/images/`; `scripts/ingest_image.py`
   writes both.
4. The master stays in the breeder's folder.
5. A photo the breed check fails is never placed.

> **Image designs:** `IMAGE-DESIGNS.md` (repo root) names the OG framing styles (§7: A, B, C, D, E, H), the infographic styles (§8: IG-1 to IG-5), the approval rule (§9: nothing generated is built until the board approves its exact bytes) and the image-slot fields and picks (§10: `source`, `file`, `source_file`, `og_style`, `infographic_style`, `prompt`, `img:<slot>`). Read it before choosing, generating, framing or placing an image; on conflict it wins.

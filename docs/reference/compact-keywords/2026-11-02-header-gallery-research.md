# Header, gallery and littermate-strip research (2026-11-02, cloud session)

Sites: Pets4Homes (single blue Staffy litter ad), Champdogs (litter 80067), Battersea (dog
profile), Royal Kennel Club, Tails.com, Butternut Box, Allbirds (product page). Aesop was
blocked by Cloudflare. Playwright was refused by the proxy, so screenshots are Firecrawl at
1440 / 820 / 390; pixel figures are read off those screenshots. Not verified: sticky/shrink
behaviour (no scripted scroll), open-menu style, lazy-loaded gallery boxes on Pets4Homes and
Battersea (measured empty). No site puts a phone or WhatsApp in its header; none uses a
mobile bottom bar.

## Headers observed
- Pets4Homes: desktop 72px (burger, logo, 2 links, outline + filled pills 44px); mobile 56px.
- Battersea: desktop 92px with a solid DONATE block; mobile two rows, 121px total.
- Tails.com: desktop 90px + a 56px promo strip; tablet/mobile ~50px, Menu left, logo centred, CTA right.
- Butternut Box: 44px ticker + 72px bar with ghost + filled pills; mobile 36 + 56px.
- Royal Kennel Club: 40px utility row, logo as a hanging tab; mobile heavy (114 + 48px).
- Allbirds: 32px announcement + a floating white card header (inset 20px, 48px, radius ~10); tablet adds a 30px category row; mobile card 52px + 36px chip row.

## Galleries observed
- Pets4Homes: desktop 972×546 (~16:9) in-column, arrows, "1/10", thumbs 88×80; tablet edge to edge 820×460; mobile edge to edge 390×220, no thumbs.
- Battersea: desktop 744×435 (16:9), thumbs 144×81 with 3px active outline; mobile inset 342×192.
- Allbirds: desktop stacked grid (hero + 2-up) beside a 546px buy card; mobile square swipe with dots.
- Champdogs: 400×300 (4:3) slideshow, "1/5", 100×75 thumbs, facts beside.

## Cross-sell observed
- Pets4Homes litter strip: 4 columns (~222px) with Available/Reserved labels, name, sex, price; mobile 2×2.
- Battersea: horizontal slider with the next card peeking, arrows, "1/4".
- Allbirds: 3-up squares with captions.

## Note (2026-11-02, later): the breeder meant H2/H3 body headings, not the navbar
The header findings above are navbar research and are parked. The Art board
(https://claude.ai/artifact/J893onxJZi8idwKsxzu31S) row 1 now holds three H2/H3 heading styles
(HA Eyebrow and Question, HB Seam Rule and Answer Band, HC Margin Heading and Medal). Heading
treatments on other sites were not researched yet.

## Mapped to the first HTML board (superseded by the Art board)
H1 Trust Strip and Solid Bar (Tails, Pets4Homes) · H2 Floating Card with Quick Chips
(Allbirds) · H3 Two Rows and Phone Action Bar (Battersea, RKC; blocked on the phone number) ·
G1 Stage and Side Pair · G2 Three-Photo Spread · G3 Bleed Portrait and Contact Sheet ·
T1 Kennel Card · T2 Breeder's Note with Glance Card · T3 Question Rows and Ledger ·
X1 Swipe Rail · X2 Litter Line-Up Grid · X3 Compact List.
Excluded on purpose: the research's "Licensed breeder" trust-strip wording (licence claims are
LICENCE_CLAIM_PLACEHOLDER until confirmed).

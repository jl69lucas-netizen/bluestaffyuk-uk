import { register, type CheckResult, type CheckContext } from '../lib/registry.js';
import { settlePage } from '../lib/probes.js';
import { TIER, HEADING_CAPS } from '../lib/cityTiers.js';
import type { Page } from '@playwright/test';

register({
  id: 'layout-no-horizontal-overflow',
  family: 'LAYOUT',
  severity: 'blocking',
  describe: 'the document must not scroll sideways at any viewport',
  // This check judges exactly ONE unit: the document's own overflow measurement.
  // The per-element walk below runs only to NAME offenders, never to decide.
  // That keeps it free of false positives from intentionally-translated
  // decorative elements — but it also means the fixture pair is this check's
  // only real protection, so never weaken the fixtures.
  minExamined: 1,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    const r = await page.evaluate(() => {
      const de = document.documentElement;
      const limit = de.clientWidth;
      const overflow = de.scrollWidth - limit;
      const offenders: string[] = [];
      if (overflow > 1) {
        for (const el of Array.from(document.body.querySelectorAll<HTMLElement>('*'))) {
          if (getComputedStyle(el).position === 'fixed') continue;
          const box = el.getBoundingClientRect();
          if (box.width === 0 || box.height === 0) continue;
          if (box.right > limit + 1) {
            const cls =
              typeof el.className === 'string' && el.className.trim()
                ? '.' + el.className.trim().split(/\s+/).slice(0, 3).join('.')
                : '';
            offenders.push(`${el.tagName.toLowerCase()}${cls}@${Math.round(box.right)}px`);
          }
        }
      }
      return { overflow, offenders: offenders.slice(0, 8) };
    });

    return {
      examined: 1,
      defects:
        r.overflow > 1
          ? [
              {
                checkId: 'layout-no-horizontal-overflow',
                family: 'LAYOUT' as const,
                viewport,
                count: 1,
                message: `document overflows by ${r.overflow}px — offenders: ${
                  r.offenders.join(' | ') || 'none isolated'
                }`,
              },
            ]
          : [],
    };
  },
});

register({
  id: 'layout-min-font-size',
  family: 'LAYOUT',
  severity: 'blocking',
  describe: 'no visible text may render below 12.5px',
  // 12.5 was questioned on 2026-08-01: 88 declarations of `.78rem` compute to 12.48px
  // and fail by 0.02px, which reads like a rounding artifact, and the backlog advised
  // exempting them. It is not an artifact — `.78rem` is the single most-used small size
  // in this codebase (88 declarations across 17 files), so moving the threshold to 12.4
  // would retire the check's LARGEST cohort permanently and leave it unable to speak
  // about that band again. The threshold stayed; the codebase moved to `--fs-micro`
  // (0.79rem = 12.64px). Do not lower this number to make a sweep smaller.
  minExamined: 3,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    const r = await page.evaluate(() => {
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      let examined = 0;
      const bad: string[] = [];
      let node: Node | null;
      while ((node = walker.nextNode())) {
        const text = (node.textContent || '').trim();
        if (!text) continue;
        const el = node.parentElement;
        if (!el) continue;
        // getClientRects() is empty when ANY ancestor is display:none
        if (el.getClientRects().length === 0) continue;
        const cs = getComputedStyle(el);
        if (cs.visibility === 'hidden') continue;
        examined++;
        const size = parseFloat(cs.fontSize);
        if (size < 12.5) {
          bad.push(`${el.tagName.toLowerCase()} ${size}px "${text.slice(0, 30)}"`);
        }
      }
      return { examined, bad: bad.slice(0, 10), count: bad.length };
    });

    return {
      examined: r.examined,
      defects: r.count
        ? [
            {
              checkId: 'layout-min-font-size',
              family: 'LAYOUT' as const,
              viewport,
              count: r.count,
              message: `${r.count} text node(s) below 12.5px: ${r.bad.join(' | ')}`,
            },
          ]
        : [],
    };
  },
});

register({
  id: 'layout-tap-target-size',
  family: 'LAYOUT',
  severity: 'blocking',
  describe: 'every visible interactive control is at least 24x24px',
  minExamined: 2,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    const r = await page.evaluate(() => {
      const sel = 'a[href], button, input:not([type=hidden]), select, textarea, [role=button]';
      const nodes = Array.from(document.querySelectorAll<HTMLElement>(sel));
      let examined = 0;
      const bad: string[] = [];
      // WCAG 2.2 SC 2.5.8 exempts two things this check used to flag on every page.
      // In the 2026-08-01 baseline all 45 LAYOUT rows named the skip link, and inline
      // prose links supplied the bulk of every message — so the report's "worst
      // family / next action" line was pointing at the standard's own exemptions.

      // (1) Visually-hidden controls in the 1px-clip pattern. The WCAG-MANDATED skip
      //     link is the canonical case: it has client rects and is not
      //     visibility:hidden, so a naive size test counts it and reports an
      //     accessibility feature as an accessibility defect.
      const isVisuallyHidden = (el: HTMLElement, box: DOMRect, cs: CSSStyleDeclaration) =>
        box.width <= 4 ||
        box.height <= 4 ||
        cs.clipPath === 'inset(50%)' ||
        /rect\(0(px)?[,\s]/.test(cs.clip) ||
        /(^|\s)(sr-only|visually-hidden|skip-link)(\s|$)/.test(el.className || '');

      // (2) A link sitting INSIDE a sentence. SC 2.5.8: "the target is in a sentence
      //     or its size is otherwise constrained by the line-height". Enlarging these
      //     would break the line box, so the standard does not ask for it. Detected
      //     structurally — an inline <a> whose parent carries text beyond the link
      //     itself — which distinguishes prose links from nav pills, where the parent
      //     <li> contains nothing but the link.
      const isInlineProseLink = (el: HTMLElement, cs: CSSStyleDeclaration) => {
        // EXACTLY `inline`, never `startsWith('inline')`: inline-block and inline-flex
        // are how every button-shaped control on this site is laid out, and matching
        // the prefix exempted the known_broken fixture's own 44x44 control because
        // <body> happened to contain other text. Caught by the fixture, not by review.
        if (el.tagName !== 'A' || cs.display !== 'inline') return false;
        const parent = el.parentElement;
        if (!parent) return false;
        const own = (el.textContent || '').trim().length;
        const around = (parent.textContent || '').trim().length;
        return around > own + 1;
      };

      // (3) A form control whose LABEL is the real target. A 13x13 checkbox inside a
      //     341x62 <label class="inq-checkbox-item"> is activated by clicking anywhere
      //     in the label, so the effective target is the label — measuring the raw input
      //     reports a defect that no user can experience. Measured on
      //     the source project's care-guide and health-guarantee pages,
      //     where all 12 flagged controls were 13x13 radios and checkboxes wrapped in
      //     labels between 86x47 and 341x62. "Enlarge the checkbox" would have been a
      //     design change bought for zero accessibility gain.
      const effectiveBox = (el: HTMLElement): DOMRect => {
        if (!/^(INPUT|SELECT|TEXTAREA)$/.test(el.tagName)) return el.getBoundingClientRect();
        const wrapping = el.closest('label');
        const referencing = el.id
          ? document.querySelector<HTMLElement>(`label[for="${CSS.escape(el.id)}"]`)
          : null;
        const lab = wrapping || referencing;
        if (!lab || lab.getClientRects().length === 0) return el.getBoundingClientRect();
        const lb = lab.getBoundingClientRect();
        const own = el.getBoundingClientRect();
        return lb.width * lb.height > own.width * own.height ? lb : own;
      };

      const judged: { el: HTMLElement; box: DOMRect }[] = [];
      for (const el of nodes) {
        if (el.getClientRects().length === 0) continue;
        const cs = getComputedStyle(el);
        if (cs.visibility === 'hidden') continue;
        const box = effectiveBox(el);
        if (box.width === 0 || box.height === 0) continue;
        if (isVisuallyHidden(el, box, cs)) continue;
        if (isInlineProseLink(el, cs)) continue;
        examined++;
        judged.push({ el, box });
      }

      // (4) SC 2.5.8's SPACING exception, implemented rather than approximated. The
      //     standard does not require 24x24 outright: an undersized target passes if a
      //     24px-diameter circle centred on it intersects neither another target nor
      //     another undersized target's circle. A card-title link is small but sits
      //     alone in its card, and the standard says that is fine. Without this the
      //     check reports every isolated small control on the site as a defect — the
      //     third time this one check has flagged something WCAG itself exempts.
      const centre = (b: DOMRect) => ({ x: b.left + b.width / 2, y: b.top + b.height / 2 });
      const distToBox = (c: { x: number; y: number }, b: DOMRect) => {
        const dx = Math.max(b.left - c.x, 0, c.x - b.right);
        const dy = Math.max(b.top - c.y, 0, c.y - b.bottom);
        return Math.hypot(dx, dy);
      };
      const small = judged.filter((j) => j.box.width < 24 || j.box.height < 24);

      for (const t of small) {
        const c = centre(t.box);
        let intersects = false;
        for (const o of judged) {
          if (o.el === t.el) continue;
          if (o.el.contains(t.el) || t.el.contains(o.el)) continue; // nested control, one target
          const otherSmall = o.box.width < 24 || o.box.height < 24;
          if (otherSmall) {
            const oc = centre(o.box);
            if (Math.hypot(oc.x - c.x, oc.y - c.y) < 24) {
              intersects = true;
              break;
            }
          } else if (distToBox(c, o.box) < 12) {
            intersects = true;
            break;
          }
        }
        if (!intersects) continue; // isolated: SC 2.5.8 spacing exception
        const label = (t.el.textContent || t.el.getAttribute('aria-label') || '').trim().slice(0, 24);
        bad.push(
          `${t.el.tagName.toLowerCase()} ${Math.round(t.box.width)}x${Math.round(t.box.height)} "${label}"`,
        );
      }
      return { examined, bad: bad.slice(0, 10), count: bad.length };
    });

    return {
      examined: r.examined,
      defects: r.count
        ? [
            {
              checkId: 'layout-tap-target-size',
              family: 'LAYOUT' as const,
              viewport,
              count: r.count,
              message: `${r.count} control(s) under 24x24: ${r.bad.join(' | ')}`,
            },
          ]
        : [],
    };
  },
});

/**
 * Breeder rule, 2026-08-07 (rules/design.md `layout-hero-counter-separation`).
 *
 * A counter/stat strip flush against the hero on one continuous background reads as hero
 * furniture and the figures stop registering. The rule asks for a visible boundary:
 * a background-tone shift AND a rule (border or a seam/gradient bar).
 *
 * Judged unit: the ONE counter strip, against its own previous sibling. Not the cards
 * inside it — a page with eight stat cards would otherwise report examined=8 having
 * evaluated a single expression, which is the exact inflation the registry warns about.
 */
register({
  id: 'layout-hero-counter-separation',
  family: 'LAYOUT',
  severity: 'advisory',
  describe: 'a counter/stat strip must be visually separated from the hero above it',
  minExamined: 1,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    const r = await page.evaluate(() => {
      const strip = document.querySelector<HTMLElement>('.counter-wrap, .counter-strip, [data-counters]');
      if (!strip) return { examined: 0, hasTone: false, hasRule: false };
      const prev = strip.previousElementSibling as HTMLElement | null;
      const cs = getComputedStyle(strip);
      const before = getComputedStyle(strip, '::before');

      // Walk up for the hero's EFFECTIVE background: a transparent header inherits the
      // page surface, and comparing against rgba(0,0,0,0) would call every page separated.
      const opaque = (el: Element | null): string => {
        let n: Element | null = el;
        while (n && n !== document.documentElement) {
          const bg = getComputedStyle(n).backgroundColor;
          if (bg && !/rgba\(\s*0,\s*0,\s*0,\s*0\s*\)/.test(bg) && bg !== 'transparent') return bg;
          n = n.parentElement;
        }
        return getComputedStyle(document.documentElement).backgroundColor || 'rgb(255,255,255)';
      };

      const hasTone = opaque(strip) !== opaque(prev);
      const borderPx = parseFloat(cs.borderTopWidth) || 0;
      const barPx = parseFloat(before.height) || 0;
      const hasBar = before.content !== 'none' && barPx > 0;
      // Seam elements: MEASURED ABSENT from BSUK's dist/ on 2026-09-17 (no .bsuk-seam,
      // .seam-wrap or .seam anywhere in the build). Kept because this is a
      // separation-EXISTS check: the day a component ships a seam div instead of a border
      // or a ::before bar, this is what stops the check reporting a false defect. A
      // selector that names a class nobody has written yet is cheap; a check that fails on
      // the first correct implementation is not.
      const hasSeam = !!strip.querySelector(':scope > .bsuk-seam, :scope > .seam-wrap, :scope > .seam');
      return { examined: 1, hasTone, hasRule: borderPx > 0 || hasBar || hasSeam };
    });

    if (r.examined === 0) return { examined: 0, defects: [] };

    const missing: string[] = [];
    if (!r.hasTone) missing.push('background tone shift');
    if (!r.hasRule) missing.push('border/seam/gradient rule');

    return {
      examined: 1,
      defects: missing.length
        ? [
            {
              checkId: 'layout-hero-counter-separation',
              family: 'LAYOUT' as const,
              viewport,
              count: 1,
              message: `counter strip is flush against the hero — missing ${missing.join(' and ')}`,
            },
          ]
        : [],
    };
  },
});

/**
 * Breeder rule, 2026-08-07 (rules/design.md `layout-h3-image-first`).
 *
 * Under an H3, the sectional image comes before the prose. H2 blocks keep
 * lead-paragraph-first — this rule is H3-scoped, deliberately.
 *
 * Judged unit: H3 blocks that OWN a sectional image — `img.sec-img` (the kit specimen on
 * /kit-preview/) or `img.bl-img` (src/components/BodyImage.astro, the body photograph every
 * rebuilt page renders). Until 2026-09-26 only `.sec-img` counted, and no real page carries
 * one, so the check examined zero blocks on exactly the pages rule 17 puts an H3 image on.
 * An H3 with no image of its own is not a violation of an ordering rule, so counting it
 * would inflate `examined` with units the predicate never ran against. Seam emblems and
 * icons are excluded on purpose: they are decorative and would otherwise register as "the
 * image" and fail every clean page.
 */
register({
  id: 'layout-h3-image-first',
  family: 'LAYOUT',
  severity: 'advisory',
  describe: 'a sectional image under an H3 must precede that block’s prose',
  minExamined: 1,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    const r = await page.evaluate(() => {
      const scope = document.querySelector('main') ?? document.body;
      const heads = Array.from(scope.querySelectorAll<HTMLElement>('h3'));
      const offenders: string[] = [];
      let examined = 0;

      for (const h of heads) {
        let imgAt = -1;
        let proseAt = -1;
        let i = 0;
        // The block ends at the next heading of equal or higher rank.
        for (let n = h.nextElementSibling; n && !/^H[123]$/.test(n.tagName); n = n.nextElementSibling) {
          i++;
          const isImg = n.matches('img.sec-img, img.bl-img') || !!n.querySelector?.('img.sec-img, img.bl-img');
          if (isImg && imgAt === -1) imgAt = i;
          // Known limitations, both deliberate: prose is a direct <p> sibling of 40+ characters,
          // so text inside a wrapper (<div><p>, a list, a card) is not seen as prose and cannot
          // make the block an offender; and the image must carry `.sec-img` or `.bl-img` on the
          // <img> itself — a <picture> or figure whose class sits only on the wrapper, or an
          // image rendered by another component, is not counted as the block's image.
          const isProse = n.tagName === 'P' && (n.textContent ?? '').trim().length > 40;
          if (isProse && proseAt === -1) proseAt = i;
        }
        if (imgAt === -1) continue; // block owns no sectional image — nothing to order
        examined++;
        if (proseAt !== -1 && proseAt < imgAt) offenders.push((h.textContent ?? '').trim().slice(0, 50));
      }
      return { examined, offenders: offenders.slice(0, 6), total: offenders.length };
    });

    return {
      examined: r.examined,
      defects: r.total
        ? [
            {
              checkId: 'layout-h3-image-first',
              family: 'LAYOUT' as const,
              viewport,
              count: r.total,
              message: `${r.total} H3 block(s) put prose before their image: ${r.offenders.join(' | ')}`,
            },
          ]
        : [],
    };
  },
});

/**
 * 2026-09-13 — PSI measured CLS 0.266 on the source project's widest for-sale page while every
 * local Lighthouse run read 0. `.hero-field{margin-left:auto}` made a grid item shrink-wrap:
 * until the hero photo arrived its only max-content was the tile chips (228px at 412), so the
 * 2:1 photo box was 114px tall, then grew to 190 on load and pushed the hero copy down 76px.
 * Locally the preloaded photo lands before first paint, so the box never visibly grows —
 * the defect only exists on a slower load, which is exactly where PageSpeed measures.
 *
 * The probe reproduces the pre-load state without a slow network: each above-the-fold <img>
 * is REPLACED by a clone whose source never resolves. (Changing an existing element's src
 * would not work — the browser keeps painting the old image until the new one decodes.)
 * Layout is compared with the loaded state, then the originals are put back.
 *
 * Judged unit: each above-the-fold image. Elements that move are named, not counted as units.
 */
register({
  id: 'layout-image-box-reserved',
  family: 'LAYOUT',
  severity: 'advisory',
  describe: 'nothing in the first viewport may move or resize when above-the-fold images finish loading',
  minExamined: 0,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    await page.route('**/__bsuk_pending_image__/**', () => {
      /* never fulfilled: the clone stays in the pending state for the whole measurement */
    });
    try {
      const r = await page.evaluate(async () => {
        window.scrollTo(0, 0);
        const vh = window.innerHeight;
        const label = (el: Element) => {
          const c = typeof (el as HTMLElement).className === 'string' ? (el as HTMLElement).className.trim() : '';
          return el.tagName.toLowerCase() + (c ? '.' + c.split(/\s+/).slice(0, 2).join('.') : '');
        };
        const imgs = Array.from(document.images).filter((im) => {
          const b = im.getBoundingClientRect();
          return b.width > 0 && b.height > 0 && b.top < vh && im.currentSrc;
        });
        if (!imgs.length) return { examined: 0, movers: [] as string[] };
        const watched = Array.from(document.body.querySelectorAll<HTMLElement>('body *')).filter((el) => {
          if (el.tagName === 'IMG' || el.closest('svg')) return false;
          const b = el.getBoundingClientRect();
          return b.width > 0 && b.height > 0 && b.top < vh && getComputedStyle(el).position !== 'fixed';
        });
        const before = watched.map((el) => el.getBoundingClientRect());
        // Swap the image (or its <picture>) for a clone that cannot load.
        const swaps: [Element, Element][] = [];
        imgs.forEach((im, i) => {
          const host = im.parentElement && im.parentElement.tagName === 'PICTURE' ? im.parentElement : im;
          const clone = host.cloneNode(true) as HTMLElement;
          const cimg = (clone.tagName === 'IMG' ? clone : clone.querySelector('img')) as HTMLImageElement;
          clone.querySelectorAll('source').forEach((s) => s.remove());
          cimg.removeAttribute('srcset');
          cimg.removeAttribute('loading');
          cimg.src = `/__bsuk_pending_image__/${i}.webp`;
          host.replaceWith(clone);
          swaps.push([host, clone]);
        });
        document.body.offsetHeight;
        await new Promise((res) => requestAnimationFrame(() => requestAnimationFrame(res)));
        const movers: string[] = [];
        watched.forEach((el, i) => {
          if (!el.isConnected) return;
          const a = before[i];
          const b = el.getBoundingClientRect();
          const dy = Math.round(b.top - a.top);
          const dh = Math.round(b.height - a.height);
          if (Math.abs(dy) > 4 || Math.abs(dh) > 4) movers.push(`${label(el)} Δy${dy} Δh${dh}`);
        });
        swaps.forEach(([host, clone]) => clone.replaceWith(host));
        return { examined: imgs.length, movers };
      });
      return {
        examined: r.examined,
        defects: r.movers.length
          ? [
              {
                checkId: 'layout-image-box-reserved',
                family: 'LAYOUT' as const,
                viewport,
                count: r.movers.length,
                message: `layout in the first viewport changes when its images load (CLS): ${r.movers.slice(0, 5).join(' | ')}`,
              },
            ]
          : [],
      };
    } finally {
      await page.unroute('**/__bsuk_pending_image__/**');
    }
  },
});

/**
 * WORKING RULE 13, MEASURED. Any table a page carries stacks into labelled rows below
 * 640px: no horizontal scroll, no clipped columns, and every cell still saying which
 * column it came from. The kit's `DataTable` (component 17) writes `data-label` on every
 * `<td>` from its column list and carries `.stack-table`, whose rules live in
 * src/styles/global.css; the migrated bodies that already ship tables carry both too. This
 * check is what stops the next one from not.
 *
 * WHY IT IS NOT A vp375-ONLY CHECK. The meta gate runs every fixture pair at all three
 * viewports and requires the broken one to FIRE at each of them, so a check that only had
 * an opinion below 640px would examine its own fixture and pass it twice. The requirement
 * is therefore split honestly: the LABELLING is structural and judged at every width — a
 * `<td>` with no `data-label` is a cell that will be an unlabelled block the moment the
 * table stacks, and that is true at 1280 — while the GEOMETRY (rows laid out as blocks, no
 * sideways scroll) is judged where it exists, at 640px and below.
 *
 * THE UNIT IS ONE TABLE, so `examined` is the table count and a page with no table
 * contributes none. Guard 2 in build_scorecard.mjs fails a check that examined zero nodes
 * across EVERY page, which is the right bar here: /kit-preview/ mounts the component and
 * /uk-blue-staffy-puppy-buying-guide/ carries three migrated tables, so the check always
 * has subjects even before a rebuilt page boards one.
 */
register({
  id: 'layout-table-stacks-on-mobile',
  family: 'LAYOUT',
  severity: 'blocking',
  describe: 'every table stacks into labelled rows below 640px, with no sideways scroll',
  minExamined: 1,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    const r = await page.evaluate(() => {
      const tables = Array.from(document.querySelectorAll<HTMLTableElement>('main table'));
      // The geometry half applies where the stack does. Read off the document rather than
      // off the harness's viewport argument, so the two can never disagree about which
      // side of the breakpoint the page was actually rendered at.
      const stacked = document.documentElement.clientWidth <= 640;
      const bad: string[] = [];
      tables.forEach((t, i) => {
        const cap = (t.querySelector('caption')?.textContent || '').trim();
        const name = cap ? `"${cap.slice(0, 40)}"` : `table ${i + 1}`;
        const reasons: string[] = [];
        const cells = Array.from(t.querySelectorAll('tbody td'));
        if (!cells.length) {
          reasons.push('no <td> in a <tbody> — a table with no body rows is not a table');
        } else {
          const unlabelled = cells.filter(
            (c) => !(c.getAttribute('data-label') || '').trim(),
          ).length;
          if (unlabelled) {
            reasons.push(
              `${unlabelled} of ${cells.length} <td> carry no data-label, so they stack as unlabelled blocks`,
            );
          }
        }
        if (stacked) {
          const rows = Array.from(t.querySelectorAll('tbody tr'));
          const notBlock = rows.filter((row) => getComputedStyle(row).display !== 'block').length;
          if (notBlock) {
            reasons.push(
              `${notBlock} of ${rows.length} row(s) still lay out as table rows below 640px — .stack-table is missing`,
            );
          }
          const over = t.scrollWidth - t.clientWidth;
          if (over > 1) reasons.push(`scrolls sideways by ${over}px`);
        }
        if (reasons.length) bad.push(`${name}: ${reasons.join('; ')}`);
      });
      return { examined: tables.length, bad };
    });

    return {
      examined: r.examined,
      defects: r.bad.length
        ? [
            {
              checkId: 'layout-table-stacks-on-mobile',
              family: 'LAYOUT' as const,
              viewport,
              count: r.bad.length,
              message: `${r.bad.length} table(s) do not stack cleanly: ${r.bad.slice(0, 5).join(' | ')}`,
            },
          ]
        : [],
    };
  },
});

/**
 * THE HERO ASIDE IS THE ONE BLOCK IN THE BAND THAT CAN BE CUT WITHOUT SHOWING IT.
 *
 * Rule 10 holds the hero between 390 and 450px at desktop, and it holds it with a `max-height`
 * and a hidden overflow — which is the right way to keep a ceiling and the reason a ceiling
 * needs measuring rather than reading. A copy column pushes its own text past the fold and the
 * page looks wrong; the ASIDE is a bordered card in its own column, so when the band runs out
 * the card is simply guillotined along the ceiling and the missing row looks like a design
 * choice. It was found twice in two days on the two H-GD3 pages — 19px at 1024 and 30px at
 * 1280 on the breed guide's contents list, both invisible in a screenshot until the numbers
 * were taken.
 *
 * Two readings, because they are different failures. The aside OVERFLOWING ITSELF is content
 * the card cannot hold; the aside HANGING BELOW THE HERO is content the band cannot hold. One
 * pixel of tolerance on each, for sub-pixel layout.
 */
register({
  id: 'hero-aside-no-clip',
  family: 'LAYOUT',
  severity: 'blocking',
  describe: 'a hero aside is never cut off by its own box or by the hero\'s height ceiling',
  minExamined: 1,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    await settlePage(page);
    const r = await page.evaluate(() => {
      let examined = 0;
      const bad: string[] = [];
      for (const hero of Array.from(document.querySelectorAll('.kit-hero'))) {
        const aside = hero.querySelector('.hero-aside');
        if (!aside) continue;
        const box = aside.getBoundingClientRect();
        if (box.width < 1 || box.height < 1) continue;
        examined++;
        const own = aside.scrollHeight - aside.clientHeight;
        if (own > 1) bad.push(`the aside's own content is ${Math.round(own)}px taller than its box`);
        const below = box.bottom - hero.getBoundingClientRect().bottom;
        if (below > 1) {
          bad.push(`the aside runs ${Math.round(below)}px below the hero, which clips it`);
        }
      }
      return { examined, bad };
    });
    return {
      examined: r.examined,
      defects: r.bad.length
        ? [{
          checkId: 'hero-aside-no-clip',
          family: 'LAYOUT' as const,
          viewport,
          count: r.bad.length,
          message: r.bad.join(' | '),
        }]
        : [],
    };
  },
});

/**
 * THE HERO PHOTO COMES FIRST ON A PHONE (rules/design.md rule 10; the user's answer-board
 * ruling of 2026-09-27: "ALL HEROES images come first on MOBILE").
 *
 * Rule 10 already puts the photo first in SOURCE, and test_design_components.py proves it on
 * the built pages. What nothing measured was the PAINT: the split, bleed and mosaic layouts
 * gave `.pic` `order: 2` at every width, so below 900px — where every arrangement is one
 * column — the phone reader met the heading and the lede first and the photo underneath them.
 *
 * Two readings, split the way layout-table-stacks-on-mobile splits its own, because the meta
 * gate runs every fixture at all three widths and requires the broken one to fire at each:
 *   - SOURCE ORDER, judged at every width: the photo (`.pic`) precedes the heading (`.title`).
 *   - PAINT ORDER, judged where the hero is one column (the document is 900px wide or less):
 *     the photo's top is above the heading's top.
 * The paint half is proven on its own by the `hero-image-first-order-only` fixture in
 * meta.spec.ts, which has the source order right and the paint order wrong.
 *
 * THE UNIT IS ONE HERO with both a photo and a heading. A photoless hero (`media: 'none'`) is
 * not a violation and is not counted.
 */
register({
  id: 'layout-hero-image-first-mobile',
  family: 'LAYOUT',
  severity: 'blocking',
  describe: 'the hero photo precedes the heading in source and paints above it on one-column widths',
  minExamined: 1,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    await settlePage(page);
    const r = await page.evaluate(() => {
      const oneColumn = document.documentElement.clientWidth <= 900;
      let examined = 0;
      const bad: string[] = [];
      for (const hero of Array.from(document.querySelectorAll('.kit-hero'))) {
        const pic = hero.querySelector('.pic');
        const title = hero.querySelector('.title');
        if (!pic || !title) continue;
        const pb = pic.getBoundingClientRect();
        const tb = title.getBoundingClientRect();
        if (pb.width < 1 || pb.height < 1 || tb.width < 1 || tb.height < 1) continue;
        examined++;
        const layout = hero.getAttribute('data-hero-layout') || 'split';
        if (!(title.compareDocumentPosition(pic) & Node.DOCUMENT_POSITION_PRECEDING)) {
          bad.push(`${layout}: the heading precedes the photo in source`);
        } else if (oneColumn && pb.top >= tb.top) {
          bad.push(`${layout}: the photo paints ${Math.round(pb.top - tb.top)}px below the heading's top`);
        }
      }
      return { examined, bad };
    });
    return {
      examined: r.examined,
      defects: r.bad.length
        ? [{
          checkId: 'layout-hero-image-first-mobile',
          family: 'LAYOUT' as const,
          viewport,
          count: r.bad.length,
          message: r.bad.join(' | '),
        }]
        : [],
    };
  },
});

/**
 * A BODY HEADING PAINTS ABOVE THE BODY TEXT (Known Issue 97; the user's pick of the city
 * scale, option (a), 2026-09-29).
 *
 * On all twelve built pages 49 H2s and 217 H3s painted at 17px, the body size, at every width:
 * the only heading size a body section had was `.bl-box h2`, and every other H2/H3 inherited
 * the preflight's body size. No check was silent, because none covered it —
 * `layout-min-font-size` is a floor for ALL text, `sem-heading-order` reads levels, and
 * `city-type-fit` caps city headings from above and sets no floor.
 *
 * THE BODY SIZE is the computed font-size carrying the most reading text (visible `main p` and
 * `main li`, weighted by characters), counting only text within 0.85x-1.25x of `<main>`'s own
 * size, so a long 24px lede or a block of fine print cannot become the body (the Known Issue 97
 * review, item 8). A page with no such text falls back to `<main>`'s own size.
 *
 * THE UNIT is one visible H2 or H3 in `<main>` that is NOT inside a kit (`kit-*`) or city-kit
 * component (a class that STARTS with `kit-`, never one that merely contains it): those set
 * their own type, on their own scale, and are judged by their own checks (the city type-fit gate
 * among them). A heading fails when it paints at or below the body size (within 0.5px). A page
 * with no `<main>` is a defect. The examined count is the headings judged; zero across the run is
 * Guard 2's FAIL in build_scorecard.mjs, and the fixture floor is 2.
 */
/**
 * Headings that paint at or below the body size ON PURPOSE, pinned by page and exact text —
 * never by selector, so a new heading in the same block still fails. Each entry says why.
 */
const BODY_HEADING_PINNED: Record<string, { texts: string[]; why: string }> = {
  'kit-preview': {
    texts: ['01 · Health', '02 · Delivery', '03 · Deposit', '04 · Puppies', '05 · FAQ', '06 · Contact'],
    why: 'the specimen page\'s scroll-spy stub targets (.spy-targets h3, --text-sm, muted): demo anchors for the dial and the sheet, not reading copy',
  },
};

register({
  id: 'layout-body-heading-above-body',
  family: 'LAYOUT',
  severity: 'blocking',
  describe: 'a body H2 or H3 in <main> paints larger than the body text',
  minExamined: 2,
  async run(page: Page, viewport: number, ctx: CheckContext): Promise<CheckResult> {
    await page.evaluate(() => document.fonts.ready);
    const pinned = BODY_HEADING_PINNED[ctx?.slug ?? '']?.texts ?? [];
    const r = await page.evaluate((pinned) => {
      const main = document.querySelector('main');
      if (!main) return { noMain: true, examined: 0, body: 0, bad: [] as string[] };
      const visible = (el: Element) =>
        el.getClientRects().length > 0 && getComputedStyle(el).visibility !== 'hidden';
      // The body size: the font-size carrying the most `p` and `li` text, counting only text
      // within 0.85x-1.25x of the page's base size (`<main>`'s own), so a long lede or
      // pull-quote above it, or fine print below it, can never be taken for the body.
      const base = parseFloat(getComputedStyle(main).fontSize);
      const chars = new Map<number, number>();
      for (const el of Array.from(main.querySelectorAll('p, li'))) {
        if (!visible(el) || el.querySelector('p, li')) continue;
        const n = (el.textContent || '').trim().length;
        if (!n) continue;
        const fs = parseFloat(getComputedStyle(el).fontSize);
        if (fs < base * 0.85 || fs > base * 1.25) continue;
        chars.set(fs, (chars.get(fs) || 0) + n);
      }
      let body = base;
      let most = -1;
      for (const [fs, n] of chars) if (n > most) { most = n; body = fs; }
      let examined = 0;
      const bad: string[] = [];
      for (const h of Array.from(main.querySelectorAll('h2, h3'))) {
        if (!visible(h) || h.closest('[class^="kit-"], [class*=" kit-"], .city-kit')) continue;
        examined++;
        const fs = parseFloat(getComputedStyle(h).fontSize);
        const text = (h.textContent || '').trim().replace(/\s+/g, ' ');
        if (fs <= body + 0.5 && !pinned.includes(text)) {
          bad.push(`${h.tagName.toLowerCase()} ${fs}px "${text.slice(0, 50)}"`);
        }
      }
      return { noMain: false, examined, body, bad };
    }, pinned);
    if (r.noMain) {
      return { examined: 0, defects: [{ checkId: 'layout-body-heading-above-body', family: 'LAYOUT' as const, viewport, count: 1, message: 'the page has no <main>, so no heading could be judged' }] };
    }
    return {
      examined: r.examined,
      defects: r.bad.length
        ? [{
          checkId: 'layout-body-heading-above-body',
          family: 'LAYOUT' as const,
          viewport,
          count: r.bad.length,
          message: `${r.bad.length} of ${r.examined} body H2/H3 paint at or below the ${r.body}px body size: ${r.bad.slice(0, 6).join(' | ')}`,
        }]
        : [],
    };
  },
});

/**
 * EVERY TEXT BLOCK KEEPS A SIDE GUTTER (found with Known Issue 97, 2026-09-29).
 *
 * Below 1024px the kit shell adds no gutter of its own (PageShell: every kit section owns one),
 * and the migrated sections that are NOT a `.bl-box` — `.page-body > section` with no class —
 * owned none either, so on ten of the twelve built pages their headings and paragraphs ran
 * from x = 0 to the viewport's edge at 375 AND at 768. No check covered it:
 * `layout-no-horizontal-overflow` asks whether the document scrolls sideways, and text sitting
 * on the edge does not.
 *
 * THE UNIT is one visible text node in `<main>`, measured by the Range of its own glyphs (not
 * its element's box, which a padded block would pass). It fails when its painted text starts
 * less than 16px from the left edge or ends less than 16px from the right. Three things are not
 * judged, each because the reader never sees the text at the edge: text inside a horizontal
 * scroll container that actually scrolls (a rail's later cards), text whose every line box lies
 * wholly outside the viewport (a thead moved to left: -9999px for screen readers), and text
 * clipped to a box of 2px or less (a visually hidden label). Images are not text and are not
 * judged. The examined count is the text nodes judged; the fixture floor is 2.
 */
register({
  id: 'layout-text-has-side-gutter',
  family: 'LAYOUT',
  severity: 'blocking',
  describe: 'every visible text block in <main> sits at least 16px from both viewport edges',
  minExamined: 2,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    await page.evaluate(() => document.fonts.ready);
    const r = await page.evaluate(() => {
      const GUTTER = 16;
      const main = document.querySelector('main');
      if (!main) return { noMain: true, examined: 0, bad: [] as string[], count: 0 };
      const W = document.documentElement.clientWidth;
      const scrolls = (el: Element) => {
        const cs = getComputedStyle(el);
        return /(auto|scroll)/.test(cs.overflowX) && el.scrollWidth > el.clientWidth + 1;
      };
      const inScroller = (el: Element | null) => {
        for (let a = el; a && a !== main; a = a.parentElement) if (scrolls(a)) return true;
        return false;
      };
      const clipped = (el: Element | null) => {
        for (let a = el; a && a !== main; a = a.parentElement) {
          const b = a.getBoundingClientRect();
          const cs = getComputedStyle(a);
          if ((b.width <= 2 || b.height <= 2) && (cs.overflow !== 'visible' || cs.clip !== 'auto')) return true;
        }
        return false;
      };
      let examined = 0;
      const bad: string[] = [];
      const walker = document.createTreeWalker(main, NodeFilter.SHOW_TEXT);
      let node: Node | null;
      while ((node = walker.nextNode())) {
        const text = (node.textContent || '').trim();
        if (!text) continue;
        const el = node.parentElement;
        if (!el || el.getClientRects().length === 0) continue;
        if (getComputedStyle(el).visibility === 'hidden') continue;
        const range = document.createRange();
        range.selectNodeContents(node);
        const rects = Array.from(range.getClientRects()).filter((x) => x.width > 0 && x.height > 0);
        if (!rects.length) continue;
        if (rects.every((x) => x.right <= 0 || x.left >= W)) continue;
        if (inScroller(el) || clipped(el)) continue;
        examined++;
        const left = Math.min(...rects.map((x) => x.left));
        const right = W - Math.max(...rects.map((x) => x.right));
        if (left < GUTTER - 0.5 || right < GUTTER - 0.5) {
          const block = el.closest('p, li, h1, h2, h3, h4, h5, h6, dt, dd, th, td, figcaption, blockquote, summary') || el;
          bad.push(`${block.tagName.toLowerCase()} ${Math.round(left)}px|${Math.round(right)}px "${text.slice(0, 40)}"`);
        }
      }
      return { noMain: false, examined, bad: bad.slice(0, 8), count: bad.length };
    });
    if (r.noMain) {
      return { examined: 0, defects: [{ checkId: 'layout-text-has-side-gutter', family: 'LAYOUT' as const, viewport, count: 1, message: 'the page has no <main>, so no text could be judged' }] };
    }
    return {
      examined: r.examined,
      defects: r.count
        ? [{
          checkId: 'layout-text-has-side-gutter',
          family: 'LAYOUT' as const,
          viewport,
          count: r.count,
          message: `${r.count} of ${r.examined} text node(s) paint within 16px of a viewport edge (left|right gutter): ${r.bad.join(' | ')}`,
        }]
        : [],
    };
  },
});

/**
 * A BOXED H2 FITS THE CITY CAPS (found with Known Issue 97, 2026-09-29).
 *
 * `.bl-box h2` was --text-2xl (30px) at every width on the body's inherited 1.65 line-height:
 * the health page's first boxed H2 was four lines and 198px tall at 375, and the for-sale page
 * had two at six lines. Option (a) put the unboxed H2s on the city scale; a boxed H2 is held to
 * the same caps as the city type-fit gate, one table for both (HEADING_CAPS.H2 and TIER in
 * tests/render/lib/cityTiers.ts: 22px on a phone, 25px on a tablet, 28px on a desktop), and to at
 * most three lines. The tier is read off the viewport, as the stylesheet's media queries read it.
 *
 * THE UNIT is one visible H2 inside a `.bl-box` and outside any kit or city-kit component
 * (those set their own type). Lines are the painted height over the computed line-height. The
 * examined count is the headings judged; the fixture floor is 2.
 */
/**
 * Boxed H2s allowed past THREE LINES (never past the size cap), pinned by page and exact text.
 * Both are long migrated headings in their page's verbatim set (working rule 15): at 375 on
 * the 22px scale they take four lines (104px), down from six at 30px. Shortening them is a
 * content change with its own board record, out of this style change's scope (the heading-scale
 * preview, "What the run measured"). A new long heading still fails.
 */
const BOXED_H2_PINNED_LINES: Record<string, string[]> = {
  'buy-staffy-puppies-for-sale-uk': [
    'What Are the Key Takeaways When Choosing BlueStaffyUK for KC Registered Blue Staffy Puppies in the UK?',
    'Why Does BlueStaffyUK Health Test Puppies and What Does It Mean to Have Staffies From L-2-HGA Tested Parents?',
  ],
};

register({
  id: 'layout-boxed-h2-fits',
  family: 'LAYOUT',
  severity: 'blocking',
  describe: 'a boxed H2 is within its tier\'s size cap (22/25/28px) and three lines',
  minExamined: 2,
  async run(page: Page, viewport: number, ctx: CheckContext): Promise<CheckResult> {
    await page.evaluate(() => document.fonts.ready);
    const pinned = BOXED_H2_PINNED_LINES[ctx?.slug ?? ''] ?? [];
    const r = await page.evaluate(({ pinned, tier, caps }) => {
      const main = document.querySelector('main');
      if (!main) return { noMain: true, examined: 0, cap: 0, bad: [] as string[] };
      const w = document.documentElement.clientWidth;
      const cap = w < tier.tablet ? caps[0] : w < tier.desktop ? caps[1] : caps[2];
      let examined = 0;
      const bad: string[] = [];
      for (const h of Array.from(main.querySelectorAll('.bl-box h2'))) {
        if (h.getClientRects().length === 0 || getComputedStyle(h).visibility === 'hidden') continue;
        if (h.closest('[class^="kit-"], [class*=" kit-"], .city-kit')) continue;
        examined++;
        const cs = getComputedStyle(h);
        const fs = parseFloat(cs.fontSize);
        const lh = parseFloat(cs.lineHeight) || fs * 1.2;
        const height = h.getBoundingClientRect().height;
        const lines = Math.round(height / lh);
        const full = (h.textContent || '').trim().replace(/\s+/g, ' ');
        const why: string[] = [];
        if (fs > cap + 0.5) why.push(`${fs}px over the ${cap}px cap`);
        if (lines > 3 && !pinned.includes(full)) why.push(`${lines} lines, ${Math.round(height)}px tall`);
        if (why.length) bad.push(`"${full.slice(0, 50)}" ${why.join(', ')}`);
      }
      return { noMain: false, examined, cap, bad };
    }, { pinned, tier: TIER, caps: HEADING_CAPS.H2 });
    if (r.noMain) {
      return { examined: 0, defects: [{ checkId: 'layout-boxed-h2-fits', family: 'LAYOUT' as const, viewport, count: 1, message: 'the page has no <main>, so no boxed H2 could be judged' }] };
    }
    return {
      examined: r.examined,
      defects: r.bad.length
        ? [{
          checkId: 'layout-boxed-h2-fits',
          family: 'LAYOUT' as const,
          viewport,
          count: r.bad.length,
          message: `${r.bad.length} of ${r.examined} boxed H2(s) break the ${r.cap}px / three-line cap: ${r.bad.slice(0, 6).join(' | ')}`,
        }]
        : [],
    };
  },
});

/**
 * A KIT BAND SPANS ITS COLUMN (the Known Issue 97 review, item 1; generalised in the re-review,
 * minor 1). Renamed from `layout-kit-hero-full-bleed`.
 *
 * PageShell adds no width of its own: "every kit section ... already owns its gutter". A wrapper
 * between the column and a kit band must therefore never inset it. The side-gutter rule did: the
 * blog-post template mounts its hero in a class-less `<section>` under `.page-body`, the rule
 * padded that wrapper, and the band moved from x = 0 at the column's full width to x = 24, with
 * white strips at every width. Any kit section band (a CTA or steel band) in such a wrapper would
 * lose its bleed the same way.
 *
 * THE UNIT is one visible top-level kit section band: a `section` whose class starts with `kit-`,
 * not inside a `.bl-box` or another kit component, and whose wrappers up to its column (the
 * nearest `.page-body`, else `<main>`) are all class-less. A band placed in a classed wrapper
 * (the kit preview's `.container` specimen frames, a city preview) is laid out there by design
 * and is not judged. It fails when either edge sits more than 1px inside its column. A page with
 * no `<main>` is a defect.
 */
register({
  id: 'layout-kit-band-full-bleed',
  family: 'LAYOUT',
  severity: 'blocking',
  describe: 'a top-level kit section band spans its column edge to edge',
  minExamined: 1,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    const r = await page.evaluate(() => {
      const main = document.querySelector('main');
      if (!main) return { noMain: true, examined: 0, bad: [] as string[] };
      let examined = 0;
      const bad: string[] = [];
      for (const band of Array.from(main.querySelectorAll('section[class^="kit-"], section[class*=" kit-"]'))) {
        if (band.parentElement?.closest('.bl-box, [class^="kit-"], [class*=" kit-"]')) continue;
        const bb = band.getBoundingClientRect();
        if (bb.width < 1 || bb.height < 1) continue;
        const column = band.closest('.page-body') || main;
        let designed = false;
        for (let a = band.parentElement; a && a !== column; a = a.parentElement) {
          if (a.classList.length) { designed = true; break; }
        }
        if (designed) continue;
        const cb = column.getBoundingClientRect();
        examined++;
        const left = bb.left - cb.left;
        const right = cb.right - bb.right;
        if (left > 1 || right > 1) {
          const name = Array.from(band.classList).find((c) => c.startsWith('kit-')) || 'kit band';
          bad.push(`${name}${band.getAttribute('data-hero-layout') ? ' (' + band.getAttribute('data-hero-layout') + ')' : ''} inset ${Math.round(left)}px left, ${Math.round(right)}px right of its ${Math.round(cb.width)}px column`);
        }
      }
      return { noMain: false, examined, bad };
    });
    if (r.noMain) {
      return { examined: 0, defects: [{ checkId: 'layout-kit-band-full-bleed', family: 'LAYOUT' as const, viewport, count: 1, message: 'the page has no <main>, so no band could be judged' }] };
    }
    return {
      examined: r.examined,
      defects: r.bad.length
        ? [{
          checkId: 'layout-kit-band-full-bleed',
          family: 'LAYOUT' as const,
          viewport,
          count: r.bad.length,
          message: r.bad.join(' | '),
        }]
        : [],
    };
  },
});

/**
 * A HEADING NEVER PAINTS LARGER THAN THE ONE IT SITS UNDER (the Known Issue 97 review, item 2).
 *
 * `.bl-box h2` moved to the city scale (22 / 25 / 28px) while `.bl-stub h3` stayed at --text-xl,
 * 24px, so at 375 sixteen H3s on /buy-staffy-puppies-for-sale-uk/ and five on
 * /blue-staffy-pup-sale-uk/ painted larger than their box's H2. `sem-heading-order` reads levels,
 * never sizes, so nothing saw it.
 *
 * THE UNIT is one visible H3 or H4 in `<main>`, outside a kit or city-kit component (those set
 * their own type and are judged by their own checks), that has a parent heading: the nearest
 * earlier H2 for an H3, and the nearest earlier H3 under the same H2 for an H4, from the same
 * non-kit chain. It fails when it paints more than 0.5px larger than that parent. A page with
 * no `<main>` is a defect, never examined-zero.
 */
register({
  id: 'layout-heading-size-order',
  family: 'LAYOUT',
  severity: 'blocking',
  describe: 'an H3 paints no larger than its H2, and an H4 no larger than its H3',
  minExamined: 2,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    const r = await page.evaluate(() => {
      const main = document.querySelector('main');
      if (!main) return { noMain: true, examined: 0, bad: [] as string[] };
      let examined = 0;
      const bad: string[] = [];
      let h2: { fs: number; t: string } | null = null;
      let h3: { fs: number; t: string } | null = null;
      for (const h of Array.from(main.querySelectorAll('h2, h3, h4'))) {
        if (h.getClientRects().length === 0 || getComputedStyle(h).visibility === 'hidden') continue;
        if (h.closest('[class^="kit-"], [class*=" kit-"], .city-kit')) continue;
        const fs = parseFloat(getComputedStyle(h).fontSize);
        const t = (h.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 40);
        const parent = h.tagName === 'H3' ? h2 : h.tagName === 'H4' ? h3 : null;
        if (parent) {
          examined++;
          if (fs > parent.fs + 0.5) bad.push(`${h.tagName.toLowerCase()} ${fs}px "${t}" over ${parent.fs}px "${parent.t}"`);
        }
        if (h.tagName === 'H2') { h2 = { fs, t }; h3 = null; }
        else if (h.tagName === 'H3') h3 = { fs, t };
      }
      return { noMain: false, examined, bad };
    });
    const defects = [];
    if (r.noMain) {
      defects.push({ checkId: 'layout-heading-size-order', family: 'LAYOUT' as const, viewport, count: 1, message: 'the page has no <main>, so no heading could be judged' });
    } else if (r.bad.length) {
      defects.push({
        checkId: 'layout-heading-size-order',
        family: 'LAYOUT' as const,
        viewport,
        count: r.bad.length,
        message: `${r.bad.length} of ${r.examined} heading(s) paint larger than the heading they sit under: ${r.bad.slice(0, 6).join(' | ')}`,
      });
    }
    return { examined: r.examined, defects };
  },
});

/**
 * NO BODY HEADING OVER THREE LINES (the Known Issue 97 review, item 3; the user's type-fit
 * ruling of 2026-09-28, "no big headers ... No chunky title").
 *
 * ADVISORY. The scale made the long migrated headings taller: at 375, thirteen more body H2/H3s
 * wrap past three lines than the eight the preview disclosed. Every one standing today is a
 * migrated heading, most in its page's verbatim set (working rule 15), so shortening it is
 * content for that page's next board touch; each is pinned below by page and exact text and
 * named in Known Issue 97. A heading that is not pinned is reported.
 *
 * THE UNIT is one visible H2 or H3 in `<main>` outside a kit or city-kit component (the city
 * type-fit gate holds those). Lines are its painted line boxes (the Range's distinct bottoms,
 * as tests/render/lib/cityTypeFit.ts counts them). A page with no `<main>` is a defect.
 */
/**
 * The 21 body headings over three lines on 2026-09-29, all at 375 (none at 768 or 1280), each a
 * long migrated heading: pinned by page and exact text, and listed in Known Issue 97's "Next" for
 * that page's next board touch. The two for-sale boxed H2s are also in BOXED_H2_PINNED_LINES.
 */
const HEADING_LINES_PINNED: Record<string, string[]> = {
  'blue-staffy-health-uk': [
    "One of the Most Common Queries We Hear Is: “What Vaccines Does My Blue Staffy Need in the UK?” Here’s a Simple Breakdown:",
  ],
  'buy-staffy-puppies-for-sale-uk': [
    "What Are the Key Takeaways When Choosing BlueStaffyUK for KC Registered Blue Staffy Puppies in the UK?",
    "Why Does BlueStaffyUK Health Test Puppies and What Does It Mean to Have Staffies From L-2-HGA Tested Parents?",
    "What Are Common Staffordshire Bull Terrier Temperament Problems and How Do Our Parent Dogs Overcome Them?",
    "What Are the Best Dog Socialisation Tips, and How Can Puppy Crate Training Help With Staffy Separation Anxiety?",
    "How Does BlueStaffyUK Compare to Generic Classified Puppy Ads in the UK?",
    "What Makes BlueStaffyUK.uk Different From Backyard Breeders – and How Can You Tell a Good Breeder?",
    "How Does BlueStaffyUK Ensure Safe, Legal, and Stress-Free Puppy Transport Across the UK?",
  ],
  'uk-blue-staffy-puppy-buying-guide': [
    "Your Comprehensive Blue Staffy Puppy Buying Guide: Finding Your Perfect Bull Terrier Staffy With BlueStaffyUK.uk",
    "How to Find Excellent Blue Staffy Breeders UK?: What Is the Best Way to Find a Healthy Staffy Puppy From a Trusted UK Breeder?",
    "What Is the Typical Cost for a Kennel Club Registered Blue Staffy Puppy in the UK, and What Factors Affect the Price? & Questions to Ask Blue Staffy Breeders Before Buying",
    "What Health Tests Should a Blue Staffy Puppy Breeder Provide? What Are the L-2-HGA and the HC-HSF4 Tests in Staffies?",
    "What Is the Best Age to Bring Home a Blue Staffy Puppy, and Why Is Waiting Until They Are 8 Weeks Old Important?",
    "What Should I Do to Prepare My Home, and What Essential Items Do I Need to Buy for a New Blue Staffy Puppy?",
    "Your Essential Blue Staffy Puppy Socialisation Checklist! – How Do I Safely Introduce My Blue Staffy Puppy to Other Dogs and New People in the UK?",
    "How This Blue Staffy Puppy Buying Guide Helps You Avoid Common Mistakes on Delivery",
    "Step-By-Step Process for Using “Our Trusted DEFRA-Approved Pet Transport Partners – How to Get a Puppy Delivered Right to Your Door",
  ],
  'uk-locations/blue-staffy-puppies-uk': [
    "Bringing Your Dream Staffordshire Bull Terrier Puppy Closer, Anywhere in the UK",
    "Connecting Families Nationwide: Blue Staffy Puppies Delivered Across the UK",
    "Ready to Welcome a KC Registered Blue Staffordshire Bull Terrier UK?",
  ],
  'uk-staffordshire-bull-terrier-guide': [
    "Staffies and UK Law: Understanding the Breed’s Legal Status & Public Perception",
  ],
};

register({
  id: 'layout-heading-lines',
  family: 'LAYOUT',
  severity: 'advisory',
  describe: 'a body H2 or H3 wraps to three lines or fewer',
  minExamined: 2,
  async run(page: Page, viewport: number, ctx: CheckContext): Promise<CheckResult> {
    await page.evaluate(() => document.fonts.ready);
    const pinned = HEADING_LINES_PINNED[ctx?.slug ?? ''] ?? [];
    const r = await page.evaluate((pinned) => {
      const main = document.querySelector('main');
      if (!main) return { noMain: true, examined: 0, bad: [] as string[] };
      const lines = (el: Element) => {
        const range = document.createRange();
        range.selectNodeContents(el);
        const bottoms = Array.from(range.getClientRects())
          .filter((x) => x.width > 0 && x.height > 0).map((x) => Math.round(x.bottom)).sort((a, b) => a - b);
        return bottoms.filter((t, i) => i === 0 || t - bottoms[i - 1] > 3).length;
      };
      let examined = 0;
      const bad: string[] = [];
      for (const h of Array.from(main.querySelectorAll('h2, h3'))) {
        if (h.getClientRects().length === 0 || getComputedStyle(h).visibility === 'hidden') continue;
        if (h.closest('[class^="kit-"], [class*=" kit-"], .city-kit')) continue;
        examined++;
        const text = (h.textContent || '').trim().replace(/\s+/g, ' ');
        const n = lines(h);
        if (n > 3 && !pinned.includes(text)) bad.push(`${h.tagName.toLowerCase()} ${n} lines "${text}"`);
      }
      return { noMain: false, examined, bad };
    }, pinned);
    const defects = [];
    if (r.noMain) {
      defects.push({ checkId: 'layout-heading-lines', family: 'LAYOUT' as const, viewport, count: 1, message: 'the page has no <main>, so no heading could be judged' });
    } else if (r.bad.length) {
      defects.push({
        checkId: 'layout-heading-lines',
        family: 'LAYOUT' as const,
        viewport,
        count: r.bad.length,
        message: `${r.bad.length} of ${r.examined} body heading(s) wrap past three lines: ${r.bad.join(' | ')}`,
      });
    }
    return { examined: r.examined, defects };
  },
});

/**
 * A HERO'S COPY USES THE BAND IT HAS (the Known Issue 97 re-review, B1; the user's type-fit
 * ruling, "no chunky title").
 *
 * The blog template renders a post with no featured image as `layout: 'panel'`, `media: 'none'`.
 * In src/components/kit/Hero.astro the panel rule (a 14rem photo column beside the copy) came after
 * the media-none rule (one column) at the same specificity, so with no photo the H1 sat in the
 * 224px column, five tall lines at 1280, with 880px of empty band beside it.
 *
 * THE UNIT is one visible `.kit-hero`. Two readings:
 *   - a hero with no painted photo (`.pic` absent or 0 wide) fails when its copy is narrower than
 *     40% of the band's inner box: the other column is empty;
 *   - at 768 and wider, a hero whose title wraps past three lines fails, photo or not.
 * A page with no `<main>` is a defect.
 */
/**
 * Hero titles allowed past three lines from 768px, pinned by page and exact text, for the
 * title reading only (never the empty-column reading). Each is its page's migrated H1, which
 * working rule 15 carries word for word, in a two-column mosaic or stacked hero; each wraps to
 * four lines at one width (home and the buy page at 1280, the buying guide at 768) and did so
 * before Known Issue 97, which does not touch kit type. Listed in Known Issue 97's Next.
 */
const HERO_TITLE_PINNED: Record<string, string[]> = {
  index: ['Secure Your Blue Staffy Puppies for Sale UK: Safe Delivery & Verified Papers.'],
  'buy-blue-staffy-puppies-uk': ['Your One-Stop Shop to Buy Blue Staffy Puppies UK, Safely & Ethically'],
  'uk-blue-staffy-puppy-buying-guide': ['The Complete UK Blue Staffy Puppy Buying Guide: Find an Ethical Breeder, Avoid Scams & Prepare Your Home'],
};

register({
  id: 'layout-hero-copy-fills-band',
  family: 'LAYOUT',
  severity: 'blocking',
  describe: 'a photoless hero gives its copy the band, and a hero title stays within three lines from 768px',
  minExamined: 1,
  async run(page: Page, viewport: number, ctx: CheckContext): Promise<CheckResult> {
    await page.evaluate(() => document.fonts.ready);
    const pinned = HERO_TITLE_PINNED[ctx?.slug ?? ''] ?? [];
    const r = await page.evaluate((pinned) => {
      const main = document.querySelector('main');
      if (!main) return { noMain: true, examined: 0, bad: [] as string[] };
      const wide = document.documentElement.clientWidth >= 768;
      const lines = (el: Element) => {
        const range = document.createRange();
        range.selectNodeContents(el);
        const bottoms = Array.from(range.getClientRects())
          .filter((x) => x.width > 0 && x.height > 0).map((x) => Math.round(x.bottom)).sort((a, b) => a - b);
        return bottoms.filter((t, i) => i === 0 || t - bottoms[i - 1] > 3).length;
      };
      let examined = 0;
      const bad: string[] = [];
      for (const hero of Array.from(main.querySelectorAll('.kit-hero'))) {
        const hb = hero.getBoundingClientRect();
        if (hb.width < 1 || hb.height < 1) continue;
        const inner = hero.querySelector('.inner') || hero;
        const copy = hero.querySelector('.copy');
        const title = hero.querySelector('.title');
        if (!copy || !title) continue;
        examined++;
        const layout = hero.getAttribute('data-hero-layout') || 'hero';
        const pic = hero.querySelector('.pic');
        const painted = !!pic && pic.getBoundingClientRect().width >= 1;
        const cs = getComputedStyle(inner);
        const box = inner.getBoundingClientRect().width - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
        const cw = copy.getBoundingClientRect().width;
        if (!painted && cw < 0.4 * box) {
          bad.push(`${layout}: no photo, but the copy is ${Math.round(cw)}px of a ${Math.round(box)}px band`);
        }
        const n = lines(title);
        const text = (title.textContent || '').trim().replace(/\s+/g, ' ');
        if (wide && n > 3 && !pinned.includes(text)) bad.push(`${layout}: the title wraps to ${n} lines`);
      }
      return { noMain: false, examined, bad };
    }, pinned);
    if (r.noMain) {
      return { examined: 0, defects: [{ checkId: 'layout-hero-copy-fills-band', family: 'LAYOUT' as const, viewport, count: 1, message: 'the page has no <main>, so no hero could be judged' }] };
    }
    return {
      examined: r.examined,
      defects: r.bad.length
        ? [{ checkId: 'layout-hero-copy-fills-band', family: 'LAYOUT' as const, viewport, count: r.bad.length, message: r.bad.join(' | ') }]
        : [],
    };
  },
});

import { register, type CheckContext, type CheckResult } from '../lib/registry.js';
import type { Page } from '@playwright/test';

/**
 * The SCHEMA family reads the page's JSON-LD from the RENDERED document, then compares it
 * against what the page actually shows. That comparison is the reason these four checks
 * belong in the render harness rather than in a source grep:
 *
 *  - `schema-no-visible-date` is a statement about rendered TEXT, and the site's own schema
 *    is full of dates. A source grep for a date pattern reads the JSON-LD block and reports
 *    the page for the very node the rule mandates. innerText excludes <script> content, so
 *    measuring the painted page is what makes the check possible at all.
 *  - `schema-sold-not-instock` is schema-versus-rendered-state drift by definition.
 *
 * Extraction walks @graph, arrays, and nested values, because `@type` appears at every depth
 * on this site (a CollectionPage whose `about` is a Product whose `mainEntity` is an
 * ItemList). The four false-positive traps recorded in skills/manual-auditor-check.md all
 * come from pattern-matching the JSON text instead of parsing it; nothing here matches text.
 */

interface LdNode {
  types: string[];
  node: Record<string, unknown>;
  path: string;
  ancestorTypes: string[];
}
interface Extracted {
  nodes: LdNode[];
  blocks: number;
  unparseable: number;
}

/** Runs in the page. Returns every JSON-LD node, each tagged with the types that enclose it. */
const extract = (page: Page): Promise<Extracted> =>
  page.evaluate(() => {
    const nodes: {
      types: string[];
      node: Record<string, unknown>;
      path: string;
      ancestorTypes: string[];
    }[] = [];
    const walk = (v: unknown, path: string, parentTypes: string[]): void => {
      if (Array.isArray(v)) {
        v.forEach((x) => walk(x, path, parentTypes));
        return;
      }
      if (!v || typeof v !== 'object') return;
      const obj = v as Record<string, unknown>;
      const t = obj['@type'];
      const types: string[] = Array.isArray(t) ? (t as string[]) : t ? [t as string] : [];
      if (types.length) nodes.push({ types, node: obj, path, ancestorTypes: parentTypes });
      const nextAncestors = types.length ? parentTypes.concat(types) : parentTypes;
      for (const k of Object.keys(obj)) {
        if (k === '@type' || k === '@context') continue;
        walk(obj[k], `${path}.${k}`, nextAncestors);
      }
    };
    let blocks = 0;
    let unparseable = 0;
    for (const s of Array.from(
      document.querySelectorAll('script[type="application/ld+json"]'),
    )) {
      blocks++;
      try {
        walk(JSON.parse(s.textContent || ''), 'root', []);
      } catch {
        unparseable++;
      }
    }
    return { nodes, blocks, unparseable };
  });

/** A Product that is actually OFFERED — one carrying an `offers` key. */
const offered = (n: LdNode) => n.types.includes('Product') && n.node.offers !== undefined;
/** Products inside an ItemList are a catalogue listing, not the page's own single offer. */
const inItemList = (n: LdNode) => n.ancestorTypes.includes('ItemList');

register({
  id: 'schema-single-product-offer',
  family: 'SCHEMA',
  severity: 'advisory',
  describe: 'a listing page declares exactly one offered Product carrying exactly one Offer',
  minExamined: 1,
  async run(page: Page, viewport: number, ctx: CheckContext): Promise<CheckResult> {
    const { nodes } = await extract(page);
    const products = nodes.filter(offered);
    const standalone = products.filter((p) => !inItemList(p));

    // A Product with NO `offers` is a descriptive reference, not a listing — the hub's
    // CollectionPage carries `about: {@type: Product}` to name what the page is about, and
    // counting it as a second listing would report a correct page as broken. Measured on
    // the source project's widest for-sale page in dist/ before the predicate was chosen.
    const examined = products.length;
    const defects = [];

    if (ctx.pageType === 'puppy' && standalone.length !== 1) {
      defects.push({
        checkId: 'schema-single-product-offer',
        family: 'SCHEMA' as const,
        viewport,
        count: Math.max(1, Math.abs(standalone.length - 1)),
        message: `a puppy listing must declare exactly one offered Product; found ${standalone.length}`,
      });
    } else if (standalone.length > 1) {
      defects.push({
        checkId: 'schema-single-product-offer',
        family: 'SCHEMA' as const,
        viewport,
        count: standalone.length,
        message: `${standalone.length} offered Products outside an ItemList: ${standalone
          .map((p) => String(p.node.name ?? '(unnamed)').slice(0, 32))
          .join(' | ')}`,
      });
    }

    const badOffer: string[] = [];
    for (const p of standalone) {
      const o = p.node.offers;
      const list = Array.isArray(o) ? o : [o];
      const name = String(p.node.name ?? '(unnamed)').slice(0, 32);
      if (list.length > 1) {
        badOffer.push(`${name} carries ${list.length} offers nodes`);
        continue;
      }
      const type = (list[0] as { '@type'?: string } | undefined)?.['@type'];
      if (type !== 'Offer' && type !== 'AggregateOffer') {
        badOffer.push(`${name} offers @type is ${JSON.stringify(type)}`);
      } else if (ctx.pageType === 'puppy' && type === 'AggregateOffer') {
        // A single puppy is a single Offer. AggregateOffer is the litter/hub page's shape
        // and on a one-puppy page it advertises a price range that does not exist.
        // (Ported from the source project's listing-page rule; its animal noun is `puppy` here.)
        badOffer.push(`${name} uses AggregateOffer on a single-puppy page`);
      }
    }
    if (badOffer.length) {
      defects.push({
        checkId: 'schema-single-product-offer',
        family: 'SCHEMA' as const,
        viewport,
        count: badOffer.length,
        message: `malformed offers: ${badOffer.slice(0, 4).join(' | ')}`,
      });
    }

    return { examined, defects };
  },
});

register({
  id: 'schema-sold-not-instock',
  family: 'SCHEMA',
  // Promoted 2026-08-02, with its vacuity stated so nobody later reads its zero as
  // corpus-wide proof. It reported zero rows over 8 of 15 pages (24 page-viewports) and
  // examined ZERO on the other 7 — deliberately: the scope note below restricts it to
  // pages declaring exactly one standalone offered Product, and the other 7 are hubs,
  // guides and multi-listing pages. That is nothing-to-check, not a check that no-opped,
  // which is the distinction `minExamined` exists to police. Worth blocking on despite the
  // narrow scope: the defect it catches is a puppy shown Sold while its Offer still says
  // InStock, which is a commercial error, not a cosmetic one.
  severity: 'blocking',
  describe: 'a listing the page shows as sold may not declare InStock',
  minExamined: 1,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    const { nodes } = await extract(page);
    const standalone = nodes.filter((n) => offered(n) && !inItemList(n));

    // SCOPE, stated rather than left implicit: this judges pages declaring exactly ONE
    // offered Product. With several listings on one page a rendered "Sold" badge cannot be
    // attributed to a particular Offer without a card-boundary convention the markup does
    // not carry, and guessing the boundary by climbing ancestors is how a checker starts
    // reporting one card's badge against another card's schema. Multi-listing attribution
    // is left to the page's own build gate. On a single-listing page the attribution is
    // unambiguous, and that is the case the rule was written for: a sold puppy left InStock.
    if (standalone.length !== 1) return { examined: 0, defects: [] };

    const o = standalone[0].node.offers;
    const offer = (Array.isArray(o) ? o[0] : o) as { availability?: string } | undefined;
    const availability = String(offer?.availability ?? '');

    const sold = await page.evaluate(() => {
      // A BADGE, not prose: an element whose entire trimmed text is the status word.
      // "…Amie, sold last spring…" in a sentence is not a sold listing, and matching
      // the substring would make every cross-link to a placed puppy a defect.
      const root = document.querySelector('main') || document.body;
      const hits: string[] = [];
      for (const el of Array.from(root.querySelectorAll<HTMLElement>('*'))) {
        if (el.children.length) continue;
        if (el.getClientRects().length === 0) continue;
        const t = (el.textContent || '').trim();
        if (/^(sold|sold out|no longer available)$/i.test(t)) {
          hits.push(`${el.tagName.toLowerCase()} "${t}"`);
        }
      }
      return hits.slice(0, 4);
    });

    const defects =
      sold.length && /InStock/i.test(availability)
        ? [
            {
              checkId: 'schema-sold-not-instock',
              family: 'SCHEMA' as const,
              viewport,
              count: sold.length,
              message: `page renders a sold badge (${sold.join(', ')}) while its Offer declares ${availability}`,
            },
          ]
        : [];

    return { examined: 1, defects };
  },
});

register({
  id: 'schema-date-modified-present',
  family: 'SCHEMA',
  // Promoted 2026-08-02. Zero rows across all 15 corpus pages having examined 162 JSON-LD
  // blocks, non-zero on every page. Nothing conditional about it — every page carries
  // schema, so a future page shipping without `dateModified` cannot slip through silently.
  severity: 'blocking',
  describe: 'the page declares dateModified in JSON-LD — freshness lives in schema, only there',
  minExamined: 1,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    const { nodes, blocks, unparseable } = await extract(page);
    const defects = [];

    // A block that will not parse is not a passing page. Without this the check would
    // report "no dateModified" for a page whose schema is simply broken, pointing the
    // operator at the wrong repair.
    if (unparseable) {
      defects.push({
        checkId: 'schema-date-modified-present',
        family: 'SCHEMA' as const,
        viewport,
        count: unparseable,
        message: `${unparseable} of ${blocks} JSON-LD block(s) did not parse`,
      });
    }

    const has = nodes.some((n) => n.node.dateModified !== undefined);
    if (!has) {
      defects.push({
        checkId: 'schema-date-modified-present',
        family: 'SCHEMA' as const,
        viewport,
        count: 1,
        message: `no dateModified in any of the ${blocks} JSON-LD block(s) — scripts/generate_page_dates.py feeds this`,
      });
    }
    return { examined: Math.max(blocks, 1), defects };
  },
});

register({
  id: 'schema-no-visible-date',
  family: 'SCHEMA',
  // Promoted 2026-08-02. Zero rows across all 15 corpus pages, examined non-zero on every
  // one. Its examined unit is the page's rendered text, so it contributes exactly 1 per
  // page-viewport (45 total) rather than a large count — a coarse denominator, but a
  // present one on every page, which is the property promotion actually requires.
  severity: 'blocking',
  describe: 'no freshness stamp is rendered as visible text — schema carries it, the page never does',
  minExamined: 1,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    const hits = await page.evaluate(() => {
      // innerText, deliberately: it excludes <script> content, so the page's own
      // (mandatory) JSON-LD dateModified cannot be mistaken for a rendered stamp. A
      // source-level grep has no way to make that distinction and would flag the very
      // node the rule requires — one of the four traps in skills/manual-auditor-check.md.
      const text = (document.querySelector('main') || document.body).innerText || '';
      // Ported from scripts/aeo_audit.py::VISIBLE_DATE. A bare year in prose is fine
      // ("captive-bred since 2014"); the defect is the STAMP.
      // The day part is OPTIONAL: the stamp this site actually shipped and the breeder
      // reversed was "Updated June 2026", with no day. Requiring \d{1,2} there is how the
      // pattern silently stops matching the only form that has ever appeared here.
      const DAY = String.raw`(?:\d{1,2},?\s+)?`;
      const MONTH =
        'January|February|March|April|May|June|July|August|September|October|November|December';
      const patterns = [
        new RegExp(String.raw`(?:last\s+)?updated\s*:?\s*(?:on\s+)?(?:${MONTH})\s+${DAY}\d{4}`, 'gi'),
        /(?:last\s+)?updated\s*:?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}/gi,
        new RegExp(String.raw`(?:posted|published|revised)\s+(?:on\s+)?(?:${MONTH})\s+${DAY}\d{4}`, 'gi'),
        /\b\d{4}-\d{2}-\d{2}\b/g,
      ];
      const found: string[] = [];
      for (const p of patterns) {
        for (const m of text.match(p) || []) found.push(m.replace(/\s+/g, ' ').trim());
      }
      return found;
    });

    return {
      examined: 1,
      defects: hits.length
        ? [
            {
              checkId: 'schema-no-visible-date',
              family: 'SCHEMA' as const,
              viewport,
              count: hits.length,
              message: `${hits.length} visible date stamp(s): ${hits.slice(0, 5).join(' | ')} — freshness belongs in JSON-LD only`,
            },
          ]
        : [],
    };
  },
});

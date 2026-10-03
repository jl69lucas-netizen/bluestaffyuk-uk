import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Gauges, Limit } from '../types'

// BSUK session gauges. Every figure is the engine's own ($.session.usage()) or a count of
// lines in the repo's Gemini log; nothing is estimated here. The Gemini key is never read.
const PANE = 'bsuk-gauges'
const CACHE_MS = 60 * 60 * 1000 // this session's prompt cache lives one hour
const GEMINI_LOG = 'docs/reports/gemini-usage.jsonl'
const gauges = atom({ plugin: 'bsuk-gauges', key: 'gauges' } as const, null)

// BSUK tokens (src/styles/tokens.css)
const STEEL_700 = '#1F3A52'
const STEEL_300 = '#8FA3B8'
const BRASS_500 = '#C9A227'
const WARN = '#B5652A'
const TRACK = '#CFC8B8'

const pct = (n: number | null) => (n === null ? '—' : `${Math.round(n)}%`)
const label = (kind: string) =>
  kind === 'five_hour' ? '5h' : kind === 'seven_day' ? '7d' : kind.replace(/_/g, ' ')

function cacheLeftMs(g: Gauges): number | null {
  if (g.lastReplyAt === null) return null
  return Math.max(0, CACHE_MS - (g.now - g.lastReplyAt))
}

function cacheText(g: Gauges): string {
  const left = cacheLeftMs(g)
  if (left === null) return 'cache —'
  return left === 0 ? 'cache cold' : `cache ${Math.ceil(left / 60000)}m`
}

function statusLine(g: Gauges): string {
  const parts = [`ctx ${pct(g.ctxPercent)}`, cacheText(g)]
  for (const l of g.limits) parts.push(`${label(l.kind)} ${Math.round(l.percentUsed)}%`)
  if (g.usd !== null) parts.push(`$${g.usd.toFixed(2)}`)
  parts.push(`gemini ${g.geminiToday}`)
  return parts.join(' · ')
}

function ring(cx: number, cy: number, r: number, frac: number, colour: string, big: string, small: string) {
  const c = 2 * Math.PI * r
  const on = Math.max(0, Math.min(1, frac)) * c
  return `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${TRACK}" stroke-width="9"/>
<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${colour}" stroke-width="9" stroke-linecap="round"
 stroke-dasharray="${on.toFixed(1)} ${c.toFixed(1)}" transform="rotate(-90 ${cx} ${cy})"/>
<text x="${cx}" y="${cy + 6}" text-anchor="middle" font-size="16" font-weight="700" fill="${STEEL_700}">${big}</text>
<text x="${cx}" y="${cy + r + 22}" text-anchor="middle" font-size="12" fill="${STEEL_700}">${small}</text>`
}

function svg(g: Gauges): string {
  const left = cacheLeftMs(g)
  const ctxFrac = (g.ctxPercent ?? 0) / 100
  const ctxColour = (g.ctxPercent ?? 0) >= 80 ? WARN : STEEL_700
  const cacheFrac = left === null ? 0 : left / CACHE_MS
  const rows = g.limits
    .map((l, i) => {
      const y = 150 + i * 34
      const w = Math.max(0, Math.min(100, l.percentUsed)) * 2.2
      const reset = l.resetsAt ? new Date(l.resetsAt).toLocaleString([], { weekday: 'short', hour: '2-digit', minute: '2-digit' }) : ''
      return `<text x="16" y="${y}" font-size="12" fill="${STEEL_700}">${label(l.kind)} window · ${Math.round(l.percentUsed)}%${reset ? ' · resets ' + reset : ''}</text>
<rect x="16" y="${y + 6}" width="220" height="8" rx="4" fill="${TRACK}"/>
<rect x="16" y="${y + 6}" width="${w.toFixed(1)}" height="8" rx="4" fill="${l.percentUsed >= 80 ? WARN : BRASS_500}"/>`
    })
    .join('\n')
  const mins = Math.round((g.now - g.startedAt) / 60000)
  const footY = 150 + g.limits.length * 34 + 14
  const h = footY + 28
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 340 ${h}" width="340" height="${h}" font-family="system-ui, -apple-system, Segoe UI, sans-serif">
${ring(64, 62, 38, ctxFrac, ctxColour, pct(g.ctxPercent), 'context')}
${ring(170, 62, 38, cacheFrac, BRASS_500, left === null ? '—' : left === 0 ? 'cold' : Math.ceil(left / 60000) + 'm', '1-hour cache')}
<text x="276" y="56" text-anchor="middle" font-size="18" font-weight="700" fill="${STEEL_700}">${g.usd === null ? '—' : '$' + g.usd.toFixed(2)}</text>
<text x="276" y="74" text-anchor="middle" font-size="12" fill="${STEEL_300}">session cost</text>
<text x="276" y="106" text-anchor="middle" font-size="18" font-weight="700" fill="${STEEL_700}">${g.geminiToday}/${g.geminiOk}</text>
<text x="276" y="124" text-anchor="middle" font-size="12" fill="${STEEL_300}">gemini today/ok</text>
${rows}
<text x="16" y="${footY + 10}" font-size="12" fill="${STEEL_300}">session ${Math.floor(mins / 60)}h ${mins % 60}m · ${g.ctxTokens === null ? '' : Math.round(g.ctxTokens / 1000) + 'k of ' + Math.round(g.ctxWindow / 1000) + 'k tokens'}</text>
</svg>`
}

let lastReplyAt: number | null = null

async function refresh($: any) {
  const now = await $.clock.now()
  const u = await $.session.usage()
  let geminiToday = 0
  let geminiOk = 0
  try {
    const today = new Date(now).toISOString().slice(0, 10)
    const text: string = await $.fs.read(GEMINI_LOG)
    for (const line of text.split('\n')) {
      if (!line.startsWith('{')) continue
      const row = JSON.parse(line)
      if (String(row.ts || '').startsWith(today)) {
        geminiToday += 1
        if (row.status === 200) geminiOk += 1
      }
    }
  } catch {
    // no log in this folder: the gauge reads 0, which is the truth for this repo
  }
  const g: Gauges = {
    ctxPercent: u.context.percent ?? null,
    ctxTokens: u.context.tokens ?? null,
    ctxWindow: u.context.window,
    lastReplyAt,
    startedAt: u.startedAt,
    limits: (u.rateLimits ?? []).map((l: Limit) => ({ kind: l.kind, percentUsed: l.percentUsed, resetsAt: l.resetsAt })),
    usd: u.cost ? u.cost.usd : null,
    geminiToday,
    geminiOk,
    now,
  }
  await update($, gauges, () => g)
  $.ui.status(statusLine(g))
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'bsuk-gauges', description: 'Open the BSUK session gauges pane' })
    await refresh($)
    $.clock.every(30_000, () => {
      void refresh($)
    })
    return next(e)
  })

  on('command.run', { command: 'bsuk-gauges' }, async $ => {
    await refresh($)
    await $.ui.open({ id: PANE, title: 'Session gauges' })
    return { text: 'Session gauges opened.' }
  })

  on('turn.complete', async ($, e, next) => {
    const r = await next(e)
    lastReplyAt = await $.clock.now()
    await refresh($)
    return r
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const g = await read($, gauges)
    const els = $.ui.resolve(e) as any
    const { Box, Text } = els
    if (!g) return <Text dimColor>Reading the session…</Text>
    if (els.Svg) {
      return (
        <Box flexDirection="column">
          <els.Svg source={svg(g)} alt={statusLine(g)} />
        </Box>
      )
    }
    return (
      <Box flexDirection="column">
        <Text bold color={STEEL_300}>BSUK session gauges</Text>
        <Text>{statusLine(g)}</Text>
      </Box>
    )
  })
}

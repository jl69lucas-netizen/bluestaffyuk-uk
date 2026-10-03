import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Route, Row } from '../types'

// BSUK Route Map (breeder's pick A, answer board 2026-10-03 q01). The mod draws what
// scripts/pipeline_status.py prints and decides nothing itself: a row is done only when the
// repo holds the file that proves it.
const PANE = 'bsuk-route'
const route = atom({ plugin: 'bsuk-route', key: 'route' } as const, null)
const error = atom({ plugin: 'bsuk-route', key: 'error' } as const, null)

// Page boards by slug, for the links under the map. A slug not listed gets only the answer board.
const PAGE_BOARDS: Record<string, string> = {
  'blue-staffy-puppies-london': 'https://claude.ai/artifact/CbemmwUeW5qGEmEFog7ezz',
}

// BSUK tokens (src/styles/tokens.css), set for the dark pane: a steel-900 card, bone ink,
// brass for a STOP and for the row in progress.
const CARD = '#14202B'
const CARD_2 = '#1B2A38'
const INK = '#F4F1EA'
const INK_2 = '#B9C6D3'
const INK_3 = '#7F93A8'
const DONE = '#8FB3D4'
const BRASS = '#C9A227'
const TODO = '#3A4C5E'

const PHASE_LABEL: Record<string, string> = {
  Research: 'Research',
  Plan: 'Stops · plan & assets',
  Build: 'Build & harden',
  Close: 'Gates & close',
}

function esc(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

// A tall, vertical line: one station per page-run row, its name beside it in reading size.
// The markup is 880 wide so the pane scales it to its own width and the text stays large.
const W = 880
const LX = 92 // the line's x
const ROW = 74
const HEAD = 64

function mark(r: Row, y: number): string {
  const done = r.state === 'done'
  const now = r.state === 'now'
  if (r.stop) {
    const fill = done || now ? BRASS : CARD
    const stroke = done || now ? BRASS : TODO
    return `<rect x="${LX - 17}" y="${y - 17}" width="34" height="34" rx="4" transform="rotate(45 ${LX} ${y})" fill="${fill}" stroke="${stroke}" stroke-width="3"/>
<text x="${LX}" y="${y + 8}" font-size="22" font-weight="800" text-anchor="middle" fill="${done || now ? CARD : INK_3}">${r.stop}</text>`
  }
  if (now) {
    return `<circle cx="${LX}" cy="${y}" r="26" fill="${BRASS}" opacity=".22"><animate attributeName="r" values="18;30;18" dur="1.8s" repeatCount="indefinite"/></circle>
<circle cx="${LX}" cy="${y}" r="17" fill="${BRASS}"/><text x="${LX}" y="${y + 7}" font-size="18" font-weight="800" text-anchor="middle" fill="${CARD}">${r.row}</text>`
  }
  return `<circle cx="${LX}" cy="${y}" r="16" fill="${done ? DONE : CARD}" stroke="${done ? DONE : TODO}" stroke-width="4"/>
<text x="${LX}" y="${y + 6}" font-size="15" font-weight="700" text-anchor="middle" fill="${done ? CARD : INK_3}">${r.row}</text>`
}

function svg(rt: Route): string {
  let y = 150
  let body = ''
  let prevY: number | null = null
  let prevLit = true
  const lines: string[] = []
  for (const phase of ['Research', 'Plan', 'Build', 'Close']) {
    const rows = rt.rows.filter(r => r.phase === phase)
    if (!rows.length) continue
    const done = rows.filter(r => r.state === 'done').length
    body += `<text x="${LX + 44}" y="${y}" font-size="17" font-weight="800" letter-spacing="2.5" fill="${INK_3}">${esc(PHASE_LABEL[phase].toUpperCase())}</text>
<text x="${W - 40}" y="${y}" font-size="17" font-weight="700" text-anchor="end" fill="${done === rows.length ? DONE : INK_3}">${done}/${rows.length}</text>`
    y += HEAD - 10
    for (const r of rows) {
      const lit = r.state !== 'todo'
      if (prevY !== null) {
        lines.push(lit && prevLit
          ? `<line x1="${LX}" y1="${prevY}" x2="${LX}" y2="${y}" stroke="${DONE}" stroke-width="8" stroke-linecap="round"/>`
          : `<line x1="${LX}" y1="${prevY}" x2="${LX}" y2="${y}" stroke="${TODO}" stroke-width="6" stroke-linecap="round" stroke-dasharray="2 12"/>`)
      }
      const now = r.state === 'now'
      if (now) body += `<rect x="24" y="${y - 32}" width="${W - 48}" height="64" rx="14" fill="${CARD_2}" stroke="${BRASS}" stroke-width="2"/>`
      const name = `${r.stop ? 'STOP ' + r.stop + ' · ' : ''}${esc(r.name)}`
      const right = r.state === 'done' ? (r.stop ? 'approved' : 'done') : now ? 'in progress' : ''
      body += `<g><title>Row ${r.row} · ${esc(r.name)} · ${r.state} · ${esc(r.evidence)}</title>
${mark(r, y)}
<text x="${LX + 44}" y="${y + 9}" font-size="${now ? 28 : 25}" font-weight="${now || r.stop ? 750 : 500}" fill="${r.state === 'todo' ? INK_3 : INK}">${name}</text>
<text x="${W - 44}" y="${y + 8}" font-size="18" font-weight="700" text-anchor="end" fill="${now ? BRASS : r.stop && r.state === 'done' ? BRASS : DONE}">${right}</text></g>`
      prevY = y
      prevLit = lit
      y += ROW
    }
    y += 26
  }
  const H = y + 10
  const pct = Math.round((rt.rows.filter(r => r.state === 'done').length / rt.rows.length) * 100)
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" font-family="system-ui, -apple-system, Segoe UI, sans-serif">
<rect x="0" y="0" width="${W}" height="${H}" rx="20" fill="${CARD}"/>
<text x="40" y="62" font-size="34" font-weight="800" fill="${INK}">${esc(rt.slug)}</text>
<text x="40" y="100" font-size="20" fill="${INK_2}">STOP ${rt.stops_done}/4 · ${pct}% of the run proved · ${esc(rt.branch)}</text>
<rect x="40" y="114" width="${W - 80}" height="8" rx="4" fill="${TODO}"/><rect x="40" y="114" width="${((W - 80) * pct) / 100}" height="8" rx="4" fill="${BRASS}"/>
${lines.join('\n')}
${body}
</svg>`
}

function statusLine(rt: Route): string {
  const dots = [1, 2, 3, 4].map(n => (n <= rt.stops_done ? '●' : '○')).join('')
  const now = rt.now ? `row ${rt.now} ${rt.now_name}` : 'all rows proved'
  const needs = rt.needs_you.length ? ` · ▲ ${rt.needs_you.length} waiting on you` : ''
  return `BSUK ${rt.slug.replace(/^blue-staffy-puppies-/, '')} ${dots} STOP ${rt.stops_done}/4 · ${now}${needs}`
}

async function refresh($: any) {
  try {
    const r = await $.process.run(['python3', 'scripts/pipeline_status.py'], { timeoutMs: 20_000 })
    if (r.exitCode !== 0) {
      await update($, error, () => (r.stderr || r.stdout || 'pipeline_status.py failed').slice(0, 300))
      $.ui.status(undefined)
      return
    }
    const rt: Route = JSON.parse(r.stdout)
    await update($, route, () => rt)
    await update($, error, () => null)
    $.ui.status(statusLine(rt))
  } catch (err) {
    // not a BSUK checkout (no script here): stay quiet rather than draw a guess
    await update($, error, () => String(err).slice(0, 300))
    $.ui.status(undefined)
  }
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'bsuk-route', description: 'Open the BSUK Route Map for the page in progress' })
    await refresh($)
    $.clock.every(60_000, () => {
      void refresh($)
    })
    return next(e)
  })

  on('command.run', { command: 'bsuk-route' }, async $ => {
    await refresh($)
    await $.ui.open({ id: PANE, title: 'Route map' })
    return { text: 'Route map opened.' }
  })

  on('turn.complete', async ($, e, next) => {
    const r = await next(e)
    await refresh($)
    return r
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const rt = await read($, route)
    const err = await read($, error)
    const els = $.ui.resolve(e) as any
    const { Box, Text, Link } = els
    if (!rt) return <Text dimColor>{err ? `No route: ${err}` : 'Reading the page run…'}</Text>
    const board = PAGE_BOARDS[rt.slug]
    return (
      <Box flexDirection="column">
        {els.Svg ? (
          <els.Svg source={svg(rt)} alt={statusLine(rt)} isInteractive />
        ) : (
          <Box flexDirection="column">
            {rt.rows.map(r => (
              <Text color={r.state === 'now' ? BRASS : undefined} dimColor={r.state === 'todo'}>
                {r.state === 'done' ? '●' : r.state === 'now' ? '◉' : '○'} {String(r.row).padStart(2)} {r.stop ? `STOP ${r.stop} · ` : ''}{r.name}
              </Text>
            ))}
          </Box>
        )}
        {rt.needs_you.map(n => (
          <Text color={BRASS}>▲ {n}</Text>
        ))}
        <Text dimColor>{rt.commit}</Text>
        <Box flexDirection="row" gap={2}>
          <Link href={rt.answer_board} label="Answer board" />
          {board ? <Link href={board} label="Page board" /> : null}
        </Box>
      </Box>
    )
  })
}

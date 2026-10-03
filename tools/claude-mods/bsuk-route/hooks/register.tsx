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

// BSUK tokens (src/styles/tokens.css)
const STEEL_900 = '#14202B'
const STEEL_700 = '#1F3A52'
const STEEL_300 = '#8FA3B8'
const BRASS_500 = '#C9A227'
const TODO = '#CFC8B8'
const PANEL = '#FFFFFF'

const PHASES = ['Research', 'Plan', 'Build', 'Close']
const PHASE_LABEL: Record<string, string> = {
  Research: 'RESEARCH',
  Plan: 'STOPS · PLAN & ASSETS',
  Build: 'BUILD & HARDEN',
  Close: 'GATES & CLOSE',
}

function esc(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

function station(r: Row, x: number, y: number): string {
  const done = r.state === 'done'
  const now = r.state === 'now'
  const tip = `<title>Row ${r.row} · ${esc(r.name)} · ${r.state}${r.state === 'done' ? '' : ' · ' + esc(r.evidence)}</title>`
  let mark: string
  if (r.stop) {
    const fill = done ? BRASS_500 : now ? BRASS_500 : PANEL
    const stroke = done || now ? STEEL_900 : TODO
    mark = `<rect x="${x - 10}" y="${y - 10}" width="20" height="20" transform="rotate(45 ${x} ${y})" fill="${fill}" stroke="${stroke}" stroke-width="1.5"/>
<text x="${x}" y="${y + 4}" font-size="10" font-weight="700" text-anchor="middle" fill="${done || now ? STEEL_900 : STEEL_300}">${r.stop}</text>`
  } else if (now) {
    mark = `<circle cx="${x}" cy="${y}" r="13" fill="${BRASS_500}" opacity=".28"><animate attributeName="r" values="9;15;9" dur="1.8s" repeatCount="indefinite"/></circle>
<circle cx="${x}" cy="${y}" r="8" fill="${BRASS_500}" stroke="${STEEL_900}" stroke-width="2"/>`
  } else {
    mark = `<circle cx="${x}" cy="${y}" r="7" fill="${PANEL}" stroke="${done ? STEEL_700 : TODO}" stroke-width="3"/>${done ? `<circle cx="${x}" cy="${y}" r="3" fill="${STEEL_700}"/>` : ''}`
  }
  const label = now ? `${r.row} now` : String(r.row)
  return `<g>${tip}${mark}<text x="${x}" y="${y + 24}" font-size="10" text-anchor="middle" fill="${now ? STEEL_900 : STEEL_300}" font-weight="${now ? 700 : 400}">${label}</text></g>`
}

function svg(rt: Route): string {
  const W = 360
  const left = 24
  const right = 336
  let y = 70
  let body = ''
  for (const phase of PHASES) {
    const rows = rt.rows.filter(r => r.phase === phase)
    if (!rows.length) continue
    const step = rows.length > 1 ? (right - left) / (rows.length - 1) : 0
    const xs = rows.map((_, i) => left + i * step)
    // the line: solid steel up to the last done/now station, dashed grey after it
    const lastLit = rows.reduce((k, r, i) => (r.state !== 'todo' ? i : k), -1)
    const ly = y + 26
    body += `<text x="16" y="${y}" font-size="10.5" font-weight="700" letter-spacing=".08em" fill="${STEEL_300}">${esc(PHASE_LABEL[phase])}</text>`
    if (lastLit >= 0) body += `<line x1="${left}" y1="${ly}" x2="${xs[lastLit]}" y2="${ly}" stroke="${STEEL_700}" stroke-width="5" stroke-linecap="round"/>`
    if (lastLit < rows.length - 1) {
      const from = lastLit >= 0 ? xs[lastLit] : left
      body += `<line x1="${from}" y1="${ly}" x2="${right}" y2="${ly}" stroke="${TODO}" stroke-width="5" stroke-linecap="round" stroke-dasharray="2 8"/>`
    }
    rows.forEach((r, i) => {
      body += station(r, xs[i], ly)
    })
    y += 70
  }
  const H = y - 10
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" font-family="system-ui, -apple-system, Segoe UI, sans-serif">
<rect x="0" y="0" width="${W}" height="${H}" rx="10" fill="${PANEL}"/>
<text x="16" y="26" font-size="15" font-weight="700" fill="${STEEL_900}">${esc(rt.slug)}</text>
<text x="16" y="44" font-size="12" fill="${STEEL_300}">STOP ${rt.stops_done}/4 · branch ${esc(rt.branch)}</text>
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
    const now = rt.rows.find(r => r.state === 'now')
    const next3 = rt.rows.filter(r => r.state === 'todo').slice(0, 3)
    const board = PAGE_BOARDS[rt.slug]
    return (
      <Box flexDirection="column">
        {els.Svg ? (
          <els.Svg source={svg(rt)} alt={statusLine(rt)} isInteractive />
        ) : (
          <Box flexDirection="column">
            {rt.rows.map(r => (
              <Text color={r.state === 'now' ? BRASS_500 : undefined} dimColor={r.state === 'todo'}>
                {r.state === 'done' ? '●' : r.state === 'now' ? '◉' : '○'} {String(r.row).padStart(2)} {r.stop ? `STOP ${r.stop} · ` : ''}{r.name}
              </Text>
            ))}
          </Box>
        )}
        <Text bold>Now: {now ? `row ${now.row} · ${now.name}` : 'every row proved'}</Text>
        {next3.length > 0 && <Text dimColor>Next: {next3.map(r => `${r.row} ${r.name}`).join(' → ')}</Text>}
        {rt.needs_you.map(n => (
          <Text color={BRASS_500}>▲ {n}</Text>
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

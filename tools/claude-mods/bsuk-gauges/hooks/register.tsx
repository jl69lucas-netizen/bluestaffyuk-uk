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
const STEEL_300 = '#8FA3B8'
const BRASS_500 = '#C9A227'
const WARN = '#B5652A'
const STEEL_900 = '#14202B'

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
  // The page run (scripts/pipeline_status.py, when this is a BSUK checkout) and the agent count.
  let stop: number | null = null
  let row: number | null = null
  let rowName: string | null = null
  try {
    const r = await $.process.run(['python3', 'scripts/pipeline_status.py'], { timeoutMs: 20_000 })
    if (r.exitCode === 0) {
      const rt = JSON.parse(r.stdout)
      stop = rt.stops_done
      row = rt.now
      rowName = rt.now_name
    }
  } catch {
    // not a BSUK checkout: the band leaves the page run out
  }
  let agentsRunning = 0
  try {
    agentsRunning = (await $.agent.list()).filter((a: any) => a.status === 'running').length
  } catch {}
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
    stop,
    row,
    rowName,
    agentsRunning,
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

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const g = await read($, gauges)
    if (!g || e.props.hasSurvey) return next(e)
    const { Box, Text } = $.ui.resolve(e) as any
    // Big-value readout: each value a bold chip on brass (orange when it needs attention),
    // each label quiet beside it, so the numbers read from across the room.
    const left = cacheLeftMs(g)
    const chip = (name: string, value: string, warn = false) => (
      <Text>
        <Text color={STEEL_300}>{name} </Text>
        <Text bold backgroundColor={warn ? WARN : BRASS_500} color={STEEL_900}> {value} </Text>
        <Text>   </Text>
      </Text>
    )
    const items = [
      chip('CONTEXT', pct(g.ctxPercent), (g.ctxPercent ?? 0) >= 80),
      chip('CACHE', left === null ? '—' : left === 0 ? 'cold' : `${Math.ceil(left / 60000)}m`, left !== null && left < 10 * 60000),
      ...g.limits.map(l => chip(label(l.kind).toUpperCase(), `${Math.round(l.percentUsed)}%`, l.percentUsed >= 80)),
      ...(g.usd !== null ? [chip('COST', `$${g.usd.toFixed(2)}`)] : []),
      ...(g.stop !== null ? [chip('STOP', `${g.stop}/4`)] : []),
      ...(g.row !== null ? [chip('ROW', `${g.row}`)] : []),
      chip('AGENTS', `${g.agentsRunning}`),
      chip('GEMINI', `${g.geminiToday}`),
    ]
    return (
      <Box flexDirection="row" flexWrap="wrap" backgroundColor={STEEL_900} paddingX={1}>
        {items}
      </Box>
    )
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const g = await read($, gauges)
    const { Box, Text } = $.ui.resolve(e) as any
    if (!g) return <Text dimColor>Reading the session…</Text>
    // Text cards, not a picture: values are bold brass chips at reading size.
    const left = cacheLeftMs(g)
    const BAR = 30
    const bar = (frac: number, warn: boolean) => {
      const lit = Math.max(0, Math.min(BAR, Math.round(frac * BAR)))
      return (
        <Text>
          <Text color={warn ? WARN : BRASS_500}>{'█'.repeat(lit)}</Text>
          <Text color={'#3A4C5E'}>{'█'.repeat(BAR - lit)}</Text>
        </Text>
      )
    }
    const card = (name: string, value: string, note: string, frac: number | null, warn = false) => (
      <Box flexDirection="column" width="100%" backgroundColor={STEEL_900} borderStyle="round" borderColor={warn ? WARN : BRASS_500} paddingX={2} paddingY={1}>
        <Box flexDirection="row" justifyContent="space-between" width="100%">
          <Text bold color={STEEL_300}>{name}</Text>
          <Text bold backgroundColor={warn ? WARN : BRASS_500} color={STEEL_900}> {value} </Text>
        </Box>
        {frac !== null ? bar(frac, warn) : null}
        <Text color={STEEL_300}>{note}</Text>
      </Box>
    )
    const mins = Math.round((g.now - g.startedAt) / 60000)
    return (
      <Box flexDirection="column" width="100%" gap={1}>
        {card('CONTEXT', pct(g.ctxPercent), g.ctxTokens === null ? '' : `${Math.round(g.ctxTokens / 1000)}k of ${Math.round(g.ctxWindow / 1000)}k tokens`, (g.ctxPercent ?? 0) / 100, (g.ctxPercent ?? 0) >= 80)}
        {card('1-HOUR CACHE', left === null ? '—' : left === 0 ? 'cold' : `${Math.ceil(left / 60000)}m`, left === null ? 'no reply yet' : left === 0 ? 'the next turn re-reads everything' : 'warm: the next turn is cheap', left === null ? null : left / CACHE_MS, left !== null && left < 10 * 60000)}
        {g.limits.map(l => card(`${label(l.kind).toUpperCase()} LIMIT`, `${Math.round(l.percentUsed)}%`, l.resetsAt ? `resets ${new Date(l.resetsAt).toLocaleString([], { weekday: 'short', hour: '2-digit', minute: '2-digit' })}` : '', l.percentUsed / 100, l.percentUsed >= 80))}
        {card('SESSION COST', g.usd === null ? '—' : `$${g.usd.toFixed(2)}`, `session ${Math.floor(mins / 60)}h ${mins % 60}m`, null)}
        {g.stop !== null ? card('PAGE RUN', `STOP ${g.stop}/4 · row ${g.row ?? '—'}`, g.rowName ?? '', null) : null}
        {card('AGENTS RUNNING', `${g.agentsRunning}`, 'open /bsuk-agents for each card', null)}
        {card('GEMINI TODAY', `${g.geminiToday} calls`, `${g.geminiOk} succeeded · the log keeps no £ figure`, null)}
      </Box>
    )
  })
}

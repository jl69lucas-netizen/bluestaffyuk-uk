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
    const { Box, Text, Link } = $.ui.resolve(e) as any
    if (!rt) return <Text dimColor>{err ? `No route: ${err}` : 'Reading the page run…'}</Text>
    // Real text, not a picture: it fills the pane at reading size on every surface.
    const proved = rt.rows.filter(r => r.state === 'done').length
    const BAR = 28
    const lit = Math.round((proved / rt.rows.length) * BAR)
    const board = PAGE_BOARDS[rt.slug]
    const phases = ['Research', 'Plan', 'Build', 'Close']
    return (
      <Box flexDirection="column" width="100%" gap={1}>
        <Box flexDirection="column" width="100%" backgroundColor={CARD} borderStyle="round" borderColor={BRASS} paddingX={2} paddingY={1}>
          <Text bold color={INK}>{rt.slug}</Text>
          <Text color={INK_2}>
            STOP {rt.stops_done}/4 · {proved} of {rt.rows.length} rows proved · {rt.branch}
          </Text>
          <Text>
            <Text color={BRASS}>{'█'.repeat(lit)}</Text>
            <Text color={TODO}>{'█'.repeat(BAR - lit)}</Text>
          </Text>
          {rt.needs_you.length > 0 ? (
            rt.needs_you.map(n => (
              <Text bold color={BRASS}>▲ Waiting on you: {n}</Text>
            ))
          ) : (
            <Text color={DONE}>Nothing is waiting on you.</Text>
          )}
        </Box>
        {phases.map(phase => {
          const rows = rt.rows.filter(r => r.phase === phase)
          const done = rows.filter(r => r.state === 'done').length
          const complete = done === rows.length
          return (
            <Box flexDirection="column" width="100%" backgroundColor={CARD} borderStyle="round" borderColor={complete ? DONE : TODO} paddingX={2} paddingY={1}>
              <Box flexDirection="row" justifyContent="space-between" width="100%">
                <Text bold color={INK_3}>{PHASE_LABEL[phase].toUpperCase()}</Text>
                <Text bold color={complete ? DONE : INK_3}>{done}/{rows.length}</Text>
              </Box>
              {rows.map(r => {
                const now = r.state === 'now'
                const isDone = r.state === 'done'
                const glyph = r.stop ? (isDone || now ? '◆' : '◇') : now ? '◉' : isDone ? '●' : '○'
                const status = isDone ? (r.stop ? 'approved' : 'done') : now ? 'in progress' : ''
                return (
                  <Box flexDirection="row" justifyContent="space-between" width="100%" backgroundColor={now ? CARD_2 : undefined}>
                    <Text color={r.state === 'todo' ? INK_3 : INK} bold={now || !!r.stop}>
                      <Text color={r.stop ? BRASS : now ? BRASS : isDone ? DONE : TODO}>{glyph} </Text>
                      {String(r.row).padStart(2, ' ')}  {r.stop ? `STOP ${r.stop} · ` : ''}{r.name}
                    </Text>
                    <Text color={now || (r.stop && isDone) ? BRASS : DONE}>{status}</Text>
                  </Box>
                )
              })}
            </Box>
          )
        })}
        <Box flexDirection="row" gap={3}>
          <Link href={rt.answer_board} label="Answer board" />
          {board ? <Link href={board} label="Page board" /> : null}
        </Box>
        <Text dimColor>{rt.commit}</Text>
      </Box>
    )
  })
}

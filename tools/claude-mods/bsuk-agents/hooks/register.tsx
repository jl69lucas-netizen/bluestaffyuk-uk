import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { AgentCard, Kind } from '../types'

// BSUK Agent Cards (breeder's pick A, 2026-10-03). One card per background agent: its job,
// what kind of work it is doing now (from the tool it last called), how long it has run and
// a strip of its last 20 actions. It reads only what the engine reports; it never reads an
// agent's transcript and sends nothing anywhere.
const PANE = 'bsuk-agents'
const cards = atom({ plugin: 'bsuk-agents', key: 'cards' } as const, {})
const STRIP = 20
const SHOW_DONE = 6

// BSUK tokens (src/styles/tokens.css), set for the dark pane
const CARD = '#14202B'
const CARD_2 = '#1B2A38'
const INK = '#F4F1EA'
const INK_2 = '#B9C6D3'
const INK_3 = '#7F93A8'
const DONE = '#8FB3D4'
const BRASS = '#C9A227'
const TODO = '#3A4C5E'
const FAIL = '#D98E5F'

const KIND: Record<Kind, { label: string; colour: string }> = {
  research: { label: 'Research', colour: '#8FB3D4' },
  read: { label: 'Reading', colour: '#7F93A8' },
  write: { label: 'Writing', colour: '#C9A227' },
  test: { label: 'Testing', colour: '#7FC79B' },
  commit: { label: 'Committing', colour: '#D98E5F' },
  other: { label: 'Working', colour: '#5B7C99' },
}
const ZERO: Record<Kind, number> = { research: 0, read: 0, write: 0, test: 0, commit: 0, other: 0 }

function base(p: unknown): string {
  const s = String(p || '')
  return s.split('/').filter(Boolean).pop() || s
}

function one(s: string, n = 64): string {
  const t = s.replace(/\s+/g, ' ').trim()
  return t.length > n ? t.slice(0, n - 1) + '…' : t
}

// What kind of work a tool call is, from its name and arguments.
function classify(e: any): { kind: Kind; text: string } {
  const tool: string = e.tool || ''
  if (tool === 'Bash') {
    const cmd: string = String(e.command || '')
    if (/\bgit\s+(commit|add|push|tag)\b/.test(cmd)) return { kind: 'commit', text: one(cmd) }
    if (/pytest|npm (run|test)|check:|build|playwright|validate|gate|tsc|node .*\.m?js/.test(cmd)) return { kind: 'test', text: one(cmd) }
    if (/^\s*(cat|sed -n|head|tail|grep|rg|ls|find|wc|git (log|show|diff|status))\b/.test(cmd)) return { kind: 'read', text: one(cmd) }
    return { kind: 'other', text: one(cmd) }
  }
  if (/^(Write|Edit|MultiEdit|NotebookEdit)$/.test(tool)) return { kind: 'write', text: `${tool} · ${base(e.file_path || e.notebook_path)}` }
  if (/^(Read|Grep|Glob|LS|NotebookRead)$/.test(tool)) return { kind: 'read', text: `${tool} · ${base(e.file_path || e.path || e.pattern)}` }
  if (/WebFetch|WebSearch|firecrawl|dataforseo|serp_|kw_data|browser|navigate|scrape|search/i.test(tool)) {
    let where = String(e.url || e.query || '')
    try {
      if (e.url) where = new URL(String(e.url)).host
    } catch {}
    return { kind: 'research', text: one(`${tool.replace(/^mcp__[^_]+__/, '')} · ${where}`) }
  }
  if (tool === 'Skill') return { kind: 'read', text: `Skill · ${e.skill || ''}` }
  return { kind: 'other', text: one(tool.replace(/^mcp__[^_]+__/, '')) }
}

function since(ms: number): string {
  const m = Math.max(0, Math.round(ms / 60000))
  return m < 60 ? `${m}m` : `${Math.floor(m / 60)}h ${m % 60}m`
}

function statusLine(all: AgentCard[]): string | undefined {
  if (!all.length) return undefined
  const running = all.filter(c => c.status === 'running').length
  const done = all.filter(c => c.status === 'done').length
  const failed = all.filter(c => c.status === 'failed').length
  return `agents ${running} running · ${done} done${failed ? ` · ${failed} failed` : ''}`
}

function blank(id: string, now: number): AgentCard {
  return {
    id, description: id, type: '', model: '', startedAt: now, endedAt: null, status: 'running',
    calls: 0, lastKind: null, lastText: '', history: [], counts: { ...ZERO },
  }
}

async function sync($: any) {
  // The engine's own list keeps statuses honest and adds agents launched before this mod loaded.
  const now = await $.clock.now()
  let list: any[] = []
  try {
    list = await $.agent.list()
  } catch {
    return
  }
  await update($, cards, (all: Record<string, AgentCard>) => {
    const next = { ...all }
    for (const a of list) {
      const c = next[a.id] ? { ...next[a.id] } : blank(a.id, now)
      c.description = a.description || c.description
      c.type = a.type || c.type
      const st = String(a.status || '')
      if (st === 'running') c.status = 'running'
      else if (st === 'completed') c.status = 'done'
      else if (st) c.status = 'failed'
      if (c.status !== 'running' && c.endedAt === null) c.endedAt = now
      next[a.id] = c
    }
    return next
  })
  $.ui.status(statusLine(Object.values(await read($, cards)) as AgentCard[]))
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'bsuk-agents', description: 'Open the BSUK Agent Cards for every background agent' })
    await sync($)
    $.clock.every(10_000, () => {
      void sync($)
    })
    return next(e)
  })

  on('command.run', { command: 'bsuk-agents' }, async $ => {
    await sync($)
    await $.ui.open({ id: PANE, title: 'Agents' })
    return { text: 'Agent cards opened.' }
  })

  on('agent.spawn', async ($, e, next) => {
    const r: any = await next(e)
    if (r && r.agentId) {
      const now = await $.clock.now()
      await update($, cards, (all: Record<string, AgentCard>) => ({
        ...all,
        [r.agentId]: { ...blank(r.agentId, now), description: e.description || r.agentId, type: e.subagentType, model: String(r.model || '') },
      }))
    }
    return r
  })

  on('tool.call', async ($, e, next) => {
    const id = (e as any).agentId
    if (id) {
      const { kind, text } = classify(e)
      const now = await $.clock.now()
      await update($, cards, (all: Record<string, AgentCard>) => {
        const c = all[id] ? { ...all[id] } : blank(id, now)
        c.calls += 1
        c.lastKind = kind
        c.lastText = text
        c.history = [...c.history, kind].slice(-STRIP)
        c.counts = { ...c.counts, [kind]: (c.counts[kind] || 0) + 1 }
        return { ...all, [id]: c }
      })
    }
    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    const r = await next(e)
    const id = (e as any).agentId
    if (id) {
      const now = await $.clock.now()
      await update($, cards, (all: Record<string, AgentCard>) => {
        if (!all[id]) return all
        return { ...all, [id]: { ...all[id], status: (e as any).isAborted ? 'failed' : 'done', endedAt: now } }
      })
      $.ui.status(statusLine(Object.values(await read($, cards)) as AgentCard[]))
    }
    return r
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e) as any
    const now = await $.clock.now()
    const all = Object.values(await read($, cards)) as AgentCard[]
    if (!all.length) return <Text dimColor>No background agents yet this session.</Text>
    const running = all.filter(c => c.status === 'running').sort((a, b) => a.startedAt - b.startedAt)
    const finished = all.filter(c => c.status !== 'running').sort((a, b) => (b.endedAt || 0) - (a.endedAt || 0))
    const failed = finished.filter(c => c.status === 'failed').length
    const total = { ...ZERO }
    for (const c of all) for (const k of Object.keys(c.counts) as Kind[]) total[k] += c.counts[k] || 0
    const sum = Object.values(total).reduce((a, b) => a + b, 0) || 1
    const BAR = 30
    const kinds = (Object.keys(KIND) as Kind[]).filter(k => total[k] > 0)

    const card = (c: AgentCard) => {
      const live = c.status === 'running'
      const age = since((c.endedAt || now) - c.startedAt)
      const k = c.lastKind ? KIND[c.lastKind] : null
      return (
        <Box flexDirection="column" width="100%" backgroundColor={CARD} borderStyle="round" borderColor={live ? BRASS : c.status === 'failed' ? FAIL : DONE} paddingX={2} paddingY={live ? 1 : 0}>
          <Box flexDirection="row" justifyContent="space-between" width="100%">
            <Text bold={live} color={INK} wrap="truncate-end">
              <Text color={live ? BRASS : c.status === 'failed' ? FAIL : DONE}>{live ? '◉ ' : c.status === 'failed' ? '✕ ' : '● '}</Text>
              {c.description}
            </Text>
            <Text color={live ? BRASS : DONE}>{live ? age : `${c.status === 'failed' ? 'stopped' : 'done'} · ${age}`}</Text>
          </Box>
          <Text color={INK_3}>
            {[c.type, c.model].filter(Boolean).join(' · ')}{c.type || c.model ? ' · ' : ''}{c.calls} tool calls
          </Text>
          {live && k ? (
            <Text wrap="truncate-end">
              <Text bold backgroundColor={k.colour} color={CARD}> {k.label} </Text>
              <Text color={INK_2}> {c.lastText}</Text>
            </Text>
          ) : null}
          {live && c.history.length ? (
            <Text>
              {c.history.map(h => (
                <Text color={KIND[h].colour}>▮</Text>
              ))}
            </Text>
          ) : null}
        </Box>
      )
    }

    return (
      <Box flexDirection="column" width="100%" gap={1}>
        <Box flexDirection="column" width="100%" backgroundColor={CARD} borderStyle="round" borderColor={BRASS} paddingX={2} paddingY={1}>
          <Box flexDirection="row" justifyContent="space-between" width="100%">
            <Text bold color={INK}>Background agents</Text>
            <Text bold color={running.length ? BRASS : DONE}>{running.length} running</Text>
          </Box>
          <Text color={INK_2}>
            {running.length} running · {finished.length - failed} done{failed ? ` · ${failed} stopped` : ''}
          </Text>
          <Text>
            {kinds.map(k => (
              <Text color={KIND[k].colour}>{'█'.repeat(Math.max(1, Math.round((total[k] / sum) * BAR)))}</Text>
            ))}
          </Text>
          <Text>
            {kinds.map(k => (
              <Text color={KIND[k].colour}>■ <Text color={INK_3}>{KIND[k].label}  </Text></Text>
            ))}
          </Text>
        </Box>
        {running.map(card)}
        {finished.slice(0, SHOW_DONE).map(card)}
        {finished.length > SHOW_DONE ? <Text color={INK_3}>+ {finished.length - SHOW_DONE} more finished</Text> : null}
        <Box backgroundColor={CARD_2} paddingX={1}>
          <Text color={TODO}>Work type comes from each agent's last tool call.</Text>
        </Box>
      </Box>
    )
  })
}

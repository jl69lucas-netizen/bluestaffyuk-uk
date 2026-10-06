export type Tools = { skills: string[]; agents: string[]; scripts: string[]; npm: string[] }

export type Row = { row: number; name: string; phase: string; state: 'done' | 'now' | 'todo'; stop: number | null; evidence: string; tools?: Tools }

export type Route = {
  slug: string
  branch: string
  commit: string
  rows: Row[]
  now: number | null
  now_name: string | null
  stops_done: number
  page_written: boolean
  needs_you: string[]
  recent?: { hash: string; ts: string; subject: string }[]
  dirty?: number
  answer_board: string
}

declare module 'claude-code' {
  interface PluginState {
    'bsuk-route': { route: Route | null; error: string | null; now: number; skillsUsed: Record<string, number> }
  }
}

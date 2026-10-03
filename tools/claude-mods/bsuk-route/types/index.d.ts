export type Row = { row: number; name: string; phase: string; state: 'done' | 'now' | 'todo'; stop: number | null; evidence: string }

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
  answer_board: string
}

declare module 'claude-code' {
  interface PluginState {
    'bsuk-route': { route: Route | null; error: string | null }
  }
}

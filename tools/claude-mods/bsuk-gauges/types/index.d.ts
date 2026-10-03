export type Limit = { kind: string; percentUsed: number; resetsAt?: string }

export type Gauges = {
  ctxPercent: number | null
  ctxTokens: number | null
  ctxWindow: number
  lastReplyAt: number | null
  startedAt: number
  limits: Limit[]
  usd: number | null
  geminiToday: number
  geminiOk: number
  now: number
  stop: number | null
  row: number | null
  rowName: string | null
  agentsRunning: number
}

declare module 'claude-code' {
  interface PluginState {
    'bsuk-gauges': { gauges: Gauges | null }
  }
}

export type Kind = 'research' | 'read' | 'write' | 'test' | 'commit' | 'other'

export type AgentCard = {
  id: string
  description: string
  type: string
  model: string
  startedAt: number
  endedAt: number | null
  status: 'running' | 'done' | 'failed'
  calls: number
  lastKind: Kind | null
  lastText: string
  history: Kind[]
  counts: Record<Kind, number>
}

declare module 'claude-code' {
  interface PluginState {
    'bsuk-agents': { cards: Record<string, AgentCard> }
  }
}

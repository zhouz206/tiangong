export interface WebSocketMessage {
  type: string
  payload: unknown
  timestamp: string
}

export interface ConnectionMessage extends WebSocketMessage {
  type: 'connection' | 'disconnection'
  payload: {
    status?: string
    reason?: string
  }
}

export interface ErrorMessage extends WebSocketMessage {
  type: 'error'
  payload: {
    error: string
  }
}

export interface AgentMessage extends WebSocketMessage {
  type: 'agent_message'
  payload: {
    agent_id: string
    agent_name: string
    content: string
    message_type: 'text' | 'status' | 'result'
  }
}

export interface TaskUpdateMessage extends WebSocketMessage {
  type: 'task_update'
  payload: {
    task_id: string
    status: string
    progress?: number
    result?: string
  }
}

export interface ProjectUpdateMessage extends WebSocketMessage {
  type: 'project_update'
  payload: {
    project_id: string
    phase?: string
    status?: string
  }
}

type WebSocketMessageHandler = (message: WebSocketMessage) => void

export class WebSocketClient {
  private ws: WebSocket | null = null
  private url: string
  private reconnectInterval: number = 5000
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private handlers: Map<string, Set<WebSocketMessageHandler>> = new Map()
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5

  constructor(url: string) {
    this.url = url
  }

  connect(): void {
    try {
      this.ws = new WebSocket(this.url)

      this.ws.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
        this.emit('connection', { status: 'connected' })
      }

      this.ws.onclose = (event) => {
        console.log('WebSocket closed', event.reason)
        this.emit('disconnection', { reason: event.reason })
        this.attemptReconnect()
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        this.emit('error', { error: 'Connection error' })
      }

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          this.emit(message.type, message)
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e)
        }
      }
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
      this.attemptReconnect()
    }
  }

  disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  send(type: string, payload: unknown): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket is not connected')
      return
    }

    const message: WebSocketMessage = {
      type,
      payload,
      timestamp: new Date().toISOString(),
    }

    this.ws.send(JSON.stringify(message))
  }

  on(eventType: string, handler: WebSocketMessageHandler): () => void {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, new Set())
    }
    this.handlers.get(eventType)!.add(handler)

    return () => {
      this.handlers.get(eventType)?.delete(handler)
    }
  }

  private emit(eventType: string, payload: unknown): void {
    const handlers = this.handlers.get(eventType)
    if (handlers) {
      const message: WebSocketMessage = {
        type: eventType,
        payload,
        timestamp: new Date().toISOString(),
      }
      handlers.forEach((handler) => handler(message))
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached')
      this.emit('error', { error: 'Max reconnection attempts reached' })
      return
    }

    if (this.reconnectTimer) {
      return
    }

    this.reconnectAttempts++
    console.log(
      `Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`
    )

    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null
      this.connect()
    }, this.reconnectInterval * this.reconnectAttempts)
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

let wsClient: WebSocketClient | null = null

export const getWebSocketClient = (url?: string): WebSocketClient => {
  if (!wsClient) {
    const wsUrl = url || import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'
    wsClient = new WebSocketClient(wsUrl)
  }
  return wsClient
}

export const connectWebSocket = (url?: string): void => {
  const client = getWebSocketClient(url)
  client.connect()
}

export const disconnectWebSocket = (): void => {
  if (wsClient) {
    wsClient.disconnect()
  }
}

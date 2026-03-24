import { useState, useEffect, useCallback } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import { Wifi, WifiOff, RefreshCw, AlertTriangle } from 'lucide-react'
import { cn } from '@/lib/utils'
import {
  getWebSocketClient,
  type WebSocketMessage,
} from '@/utils/websocket'

interface ConnectionStatus {
  connected: boolean
  reconnecting: boolean
  error?: string
  lastMessage?: string
}

interface WebSocketStatusIndicatorProps {
  onMessage?: (message: WebSocketMessage) => void
}

export function WebSocketStatusIndicator({ onMessage }: WebSocketStatusIndicatorProps) {
  const [status, setStatus] = useState<ConnectionStatus>({
    connected: false,
    reconnecting: false,
  })
  const [open, setOpen] = useState(false)

  const handleMessage = useCallback((message: WebSocketMessage) => {
    setStatus((prev) => ({
      ...prev,
      lastMessage: `${message.type} - ${new Date(message.timestamp).toLocaleTimeString()}`,
    }))
    onMessage?.(message)
  }, [onMessage])

  useEffect(() => {
    const client = getWebSocketClient()

    const unsubscribeConnection = client.on('connection', () => {
      setStatus({ connected: true, reconnecting: false })
    })

    const unsubscribeDisconnection = client.on('disconnection', () => {
      setStatus((prev) => ({ ...prev, connected: false, reconnecting: true }))
    })

    const unsubscribeError = client.on('error', (msg) => {
      const errorPayload = msg.payload as { error: string }
      setStatus((prev) => ({ ...prev, error: errorPayload?.error }))
    })

    client.on('agent_message', handleMessage)
    client.on('task_update', handleMessage)
    client.on('project_update', handleMessage)

    // Connect on mount
    if (!client.isConnected()) {
      client.connect()
    }

    return () => {
      unsubscribeConnection()
      unsubscribeDisconnection()
      unsubscribeError()
    }
  }, [handleMessage])

  const handleReconnect = () => {
    const client = getWebSocketClient()
    client.disconnect()
    setTimeout(() => client.connect(), 500)
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger>
        <Button
          variant="ghost"
          size="sm"
          className={cn(
            'h-8 gap-2',
            status.connected && 'text-green-600',
            status.reconnecting && 'text-yellow-600',
            status.error && 'text-red-600'
          )}
        >
          {status.connected ? (
            <Wifi className="h-4 w-4" />
          ) : status.reconnecting ? (
            <RefreshCw className="h-4 w-4 animate-spin" />
          ) : (
            <WifiOff className="h-4 w-4" />
          )}
          <span className="hidden sm:inline">
            {status.connected ? '已连接' : status.reconnecting ? '重连中...' : '未连接'}
          </span>
        </Button>
      </PopoverTrigger>
      <PopoverContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="font-medium">WebSocket 连接</h4>
            <Badge variant={status.connected ? 'default' : 'secondary'}>
              {status.connected ? '在线' : status.reconnecting ? '重连中' : '离线'}
            </Badge>
          </div>

          {status.error && (
            <div className="flex items-start gap-2 text-sm text-destructive">
              <AlertTriangle className="h-4 w-4 mt-0.5" />
              <p>{status.error}</p>
            </div>
          )}

          {status.lastMessage && (
            <div className="space-y-1">
              <p className="text-sm font-medium">最后消息</p>
              <p className="text-xs text-muted-foreground bg-muted p-2 rounded">
                {status.lastMessage}
              </p>
            </div>
          )}

          {!status.connected && (
            <Button size="sm" onClick={handleReconnect} className="w-full">
              <RefreshCw className="h-4 w-4 mr-2" />
              重新连接
            </Button>
          )}
        </div>
      </PopoverContent>
    </Popover>
  )
}

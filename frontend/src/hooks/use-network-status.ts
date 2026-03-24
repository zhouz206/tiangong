import { useState, useEffect, useCallback } from 'react'

type NetworkStatus = 'online' | 'offline' | 'slow'

interface UseNetworkStatusReturn {
  isOnline: boolean
  status: NetworkStatus
  isSlow: boolean
  lastChecked: Date | null
  reconnect: () => void
}

// 检测网络速度
async function checkConnectionSpeed(): Promise<number> {
  const start = Date.now()
  try {
    const response = await fetch('/api/health', {
      method: 'HEAD',
      cache: 'no-cache',
    })
    if (response.ok) {
      return Date.now() - start
    }
  } catch {
    // Fallback: try to load a small image or just return timeout
  }
  return Date.now() - start
}

export function useNetworkStatus(): UseNetworkStatusReturn {
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [status, setStatus] = useState<NetworkStatus>(navigator.onLine ? 'online' : 'offline')
  const [lastChecked, setLastChecked] = useState<Date | null>(null)

  const checkStatus = useCallback(async () => {
    const online = navigator.onLine
    setIsOnline(online)

    if (online) {
      // 检测连接速度
      const latency = await checkConnectionSpeed()
      if (latency > 1000) {
        setStatus('slow')
      } else {
        setStatus('online')
      }
    } else {
      setStatus('offline')
    }

    setLastChecked(new Date())
  }, [])

  const reconnect = useCallback(() => {
    checkStatus()
  }, [checkStatus])

  useEffect(() => {
    // 初始检查
    checkStatus()

    // 监听网络状态变化
    const handleOnline = () => checkStatus()
    const handleOffline = () => checkStatus()

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    // 定期检查网络状态（每 30 秒）
    const interval = setInterval(checkStatus, 30000)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
      clearInterval(interval)
    }
  }, [checkStatus])

  return {
    isOnline,
    status,
    isSlow: status === 'slow',
    lastChecked,
    reconnect,
  }
}

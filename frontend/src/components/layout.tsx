import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import {
  LayoutDashboard,
  FolderKanban,
  Bot,
  BookOpen,
  Settings,
  Moon,
  Sun,
  Menu,
} from 'lucide-react'
import { useState } from 'react'
import { useTheme } from 'next-themes'
import { useNetworkStatus } from '@/hooks/use-network-status'
import { Badge } from '@/components/ui/badge'
import { WifiOff } from 'lucide-react'

const navigation = [
  { name: '仪表盘', href: '/', icon: LayoutDashboard },
  { name: '项目', href: '/projects', icon: FolderKanban },
  { name: 'Agent', href: '/agents', icon: Bot },
  { name: '知识库', href: '/knowledge', icon: BookOpen },
  { name: '设置', href: '/settings', icon: Settings },
]

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation()
  const { theme, setTheme } = useTheme()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { isOnline, status } = useNetworkStatus()

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* 离线提示 */}
      {!isOnline && (
        <div className="fixed top-0 left-0 right-0 z-[100] bg-destructive text-destructive-foreground px-4 py-2 text-center text-sm font-medium">
          <WifiOff className="inline-block h-4 w-4 mr-2" />
          当前已离线，部分功能可能无法使用
        </div>
      )}
      {status === 'slow' && isOnline && (
        <div className="fixed top-0 left-0 right-0 z-[100] bg-yellow-500 text-white px-4 py-2 text-center text-sm font-medium">
          <WifiOff className="inline-block h-4 w-4 mr-2" />
          网络连接较慢
        </div>
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r bg-card transition-transform duration-300 lg:static lg:translate-x-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Logo */}
        <div className="flex h-16 items-center border-b px-6">
          <h1 className="text-lg font-bold text-foreground">天工 TianGong</h1>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 overflow-y-auto p-4">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link key={item.name} to={item.href}>
                <Button
                  variant={isActive ? 'secondary' : 'ghost'}
                  className="w-full justify-start gap-3"
                  onClick={() => setSidebarOpen(false)}
                >
                  <item.icon className="h-5 w-5" />
                  {item.name}
                </Button>
              </Link>
            )
          })}
        </nav>

        {/* Theme Toggle */}
        <div className="border-t p-4">
          <Button
            variant="outline"
            className="w-full justify-start gap-3"
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          >
            {theme === 'dark' ? (
              <Sun className="h-5 w-5" />
            ) : (
              <Moon className="h-5 w-5" />
            )}
            {theme === 'dark' ? '浅色模式' : '深色模式'}
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Header */}
        <header className="flex h-16 items-center justify-between border-b bg-card px-6 lg:hidden">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            <Menu className="h-6 w-6" />
          </Button>
          <h1 className="text-lg font-bold">天工 TianGong</h1>
          <div className="w-10" />
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>

      {/* Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  )
}

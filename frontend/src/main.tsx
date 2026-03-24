import React, { useEffect } from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { useSettingsStore } from './stores/settings'
import './index.css'

// 导入真实页面组件
import Dashboard from './pages/dashboard'
import Projects from './pages/projects'
import ProjectDetail from './pages/project-detail'
import Agents from './pages/agents'
import Knowledge from './pages/knowledge'
import Settings from './pages/settings'

function App() {
  const { theme } = useSettingsStore()
  
  // 同步主题到 HTML 元素
  useEffect(() => {
    const root = document.documentElement
    root.classList.remove('light', 'dark')
    if (theme === 'system') {
      const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      root.classList.add(systemDark ? 'dark' : 'light')
    } else {
      root.classList.add(theme)
    }
  }, [theme])
  
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">天工 TianGong</h1>
              </div>
              <div className="flex items-center space-x-4">
                <a href="/" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">仪表盘</a>
                <a href="/projects" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">项目</a>
                <a href="/agents" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Agent</a>
                <a href="/knowledge" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">知识库</a>
                <a href="/settings" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">设置</a>
              </div>
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/projects/:id" element={<ProjectDetail />} />
            <Route path="/agents" element={<Agents />} />
            <Route path="/knowledge" element={<Knowledge />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)

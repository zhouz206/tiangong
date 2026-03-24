import React, { useEffect } from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { useSettingsStore } from './stores/settings'
import './index.css'

// 页面组件（占位符）
function Dashboard() { return <div className="p-4"><h1 className="text-2xl font-bold">仪表盘</h1><p className="mt-2">项目概览和统计</p></div> }
function Projects() { return <div className="p-4"><h1 className="text-2xl font-bold">项目列表</h1><p className="mt-2">创建和管理项目</p></div> }
function ProjectDetail() { return <div className="p-4"><h1 className="text-2xl font-bold">项目详情</h1><p className="mt-2">任务流和 Agent 状态</p></div> }
function Agents() { return <div className="p-4"><h1 className="text-2xl font-bold">Agent</h1><p className="mt-2">8 个 Agent 角色</p></div> }
function Knowledge() { return <div className="p-4"><h1 className="text-2xl font-bold">知识库</h1><p className="mt-2">文档浏览和搜索</p></div> }
function Settings() { return <div className="p-4"><h1 className="text-2xl font-bold">设置</h1><p className="mt-2">主题、API、模型配置</p></div> }

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-background">
        <nav className="border-b p-4">
          <div className="flex gap-4">
            <a href="/" className="hover:underline">仪表盘</a>
            <a href="/projects" className="hover:underline">项目</a>
            <a href="/agents" className="hover:underline">Agent</a>
            <a href="/knowledge" className="hover:underline">知识库</a>
            <a href="/settings" className="hover:underline">设置</a>
          </div>
        </nav>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/projects" element={<Projects />} />
          <Route path="/projects/:id" element={<ProjectDetail />} />
          <Route path="/agents" element={<Agents />} />
          <Route path="/knowledge" element={<Knowledge />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
         <Route path="/agents" element={<Agents />} />
          <Route path="/knowledge" element={<Knowledge />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)

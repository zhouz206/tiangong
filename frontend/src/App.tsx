import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from './components/theme-provider'
import { Toaster } from './components/ui/toaster'
import { ErrorBoundary } from './components/ErrorBoundary'
import Layout from './components/layout'
import { connectWebSocket } from './utils/websocket'
import { Suspense, lazy } from 'react'
import { LoadingState } from './components/LoadingState'

// Pages - 路由懒加载
const Dashboard = lazy(() => import('./pages/dashboard'))
const Projects = lazy(() => import('./pages/projects'))
const ProjectDetail = lazy(() => import('./pages/project-detail'))
const Agents = lazy(() => import('./pages/agents'))
const Knowledge = lazy(() => import('./pages/knowledge'))
const Settings = lazy(() => import('./pages/settings'))
const NotFound = lazy(() => import('./pages/NotFound'))

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
})

// Connect WebSocket on app mount
connectWebSocket()

function App() {
  return (
    <ErrorBoundary
      onError={(error, errorInfo) => {
        console.error('App error:', error, errorInfo)
      }}
    >
      <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="system" storageKey="tiangong-theme">
        <BrowserRouter>
          <Layout>
            <Suspense fallback={<LoadingState type="page" />}>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/projects" element={<Projects />} />
                <Route path="/projects/:id" element={<ProjectDetail />} />
                <Route path="/agents" element={<Agents />} />
                <Route path="/knowledge" element={<Knowledge />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="*" element={<NotFound />} />
              </Routes>
            </Suspense>
          </Layout>
        </BrowserRouter>
        <Toaster />
      </ThemeProvider>
    </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App

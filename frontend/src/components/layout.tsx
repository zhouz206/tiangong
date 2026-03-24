import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  
  const navigation = [
    { name: '仪表盘', href: '/' },
    { name: '项目', href: '/projects' },
    { name: 'Agent', href: '/agents' },
    { name: '知识库', href: '/knowledge' },
    { name: '设置', href: '/settings' }
  ];
  
  const isActive = (path: string) => location.pathname === path;
  
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* 顶部导航 */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="md:hidden p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <span className="sr-only">打开菜单</span>
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <Link to="/" className="flex items-center ml-4 md:ml-0">
                <span className="text-xl font-bold text-gray-900 dark:text-white">天工 TianGong</span>
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600 dark:text-gray-400">v1.0.0</span>
            </div>
          </div>
        </nav>
      </header>
      
      {/* 侧边栏（移动端） */}
      {sidebarOpen && (
        <div className="md:hidden fixed inset-0 z-40 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)}>
          <div className="fixed inset-y-0 left-0 w-64 bg-white dark:bg-gray-800 shadow-xl" onClick={e => e.stopPropagation()}>
            <nav className="p-4 space-y-2">
              {navigation.map(item => (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`block px-4 py-2 rounded-md ${
                    isActive(item.href)
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                  onClick={() => setSidebarOpen(false)}
                >
                  {item.name}
                </Link>
              ))}
            </nav>
          </div>
        </div>
      )}
      
      {/* 主内容区 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
}

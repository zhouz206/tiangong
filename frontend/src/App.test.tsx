/** @vitest-environment jsdom */
import { test, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from './pages/dashboard';
import { useProjectStore } from './stores/project';

// Mock stores
vi.mock('./stores/project', () => ({
  useProjectStore: vi.fn(() => ({
    projects: [
      { id: '1', name: '测试项目 1', description: '描述 1', progress: 75, phase: 'executing', status: 'active' },
      { id: '2', name: '测试项目 2', description: '描述 2', progress: 50, phase: 'planning', status: 'active' }
    ]
  }))
}));

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

test('Dashboard 渲染统计卡片', () => {
  renderWithRouter(<Dashboard />);
  
  expect(screen.getByText('仪表盘')).toBeInTheDocument();
  expect(screen.getByText('总项目数')).toBeInTheDocument();
  expect(screen.getByText('进行中')).toBeInTheDocument();
});

test('Dashboard 显示项目列表', () => {
  renderWithRouter(<Dashboard />);
  
  expect(screen.getByText('测试项目 1')).toBeInTheDocument();
  expect(screen.getByText('测试项目 2')).toBeInTheDocument();
});

test('Dashboard 新建项目按钮存在', () => {
  renderWithRouter(<Dashboard />);
  
  expect(screen.getByText('新建项目')).toBeInTheDocument();
});

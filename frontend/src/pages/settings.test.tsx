import { test, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Settings from './settings';
import { useSettingsStore } from '../stores/settings';

vi.mock('../stores/settings', () => ({
  useSettingsStore: vi.fn(),
}));

beforeEach(() => {
  vi.clearAllMocks();
  vi.useFakeTimers();
  Object.defineProperty(document.documentElement, 'classList', {
    value: {
      remove: vi.fn(),
      add: vi.fn(),
      contains: vi.fn(),
    },
    writable: true,
  });
});

afterEach(() => {
  vi.useRealTimers();
});

test('Settings 页面渲染', () => {
  (useSettingsStore as vi.Mock).mockReturnValue({
    theme: 'system',
    apiEndpoint: 'http://localhost:8000',
    modelConfig: { model: 'qwen-3.5-plus', temperature: '0.7' },
    setTheme: vi.fn(),
    setApiEndpoint: vi.fn(),
    setModelConfig: vi.fn(),
  });

  render(<Settings />);

  expect(screen.getByText('设置')).toBeInTheDocument();
  expect(screen.getByText('配置你的工作空间和偏好')).toBeInTheDocument();
});

test('Settings 页面 - 主题切换为浅色', () => {
  const mockSetTheme = vi.fn();

  (useSettingsStore as vi.Mock).mockReturnValue({
    theme: 'dark',
    apiEndpoint: 'http://localhost:8000',
    modelConfig: { model: 'qwen-3.5-plus', temperature: '0.7' },
    setTheme: mockSetTheme,
    setApiEndpoint: vi.fn(),
    setModelConfig: vi.fn(),
  });

  render(<Settings />);

  const lightThemeButton = screen.getByText('浅色').closest('button');
  fireEvent.click(lightThemeButton!);

  expect(mockSetTheme).toHaveBeenCalledWith('light');
});

test('Settings 页面 - 主题切换为深色', () => {
  const mockSetTheme = vi.fn();

  (useSettingsStore as vi.Mock).mockReturnValue({
    theme: 'light',
    apiEndpoint: 'http://localhost:8000',
    modelConfig: { model: 'qwen-3.5-plus', temperature: '0.7' },
    setTheme: mockSetTheme,
    setApiEndpoint: vi.fn(),
    setModelConfig: vi.fn(),
  });

  render(<Settings />);

  const darkThemeButton = screen.getByText('深色').closest('button');
  fireEvent.click(darkThemeButton!);

  expect(mockSetTheme).toHaveBeenCalledWith('dark');
});

test('Settings 页面 - 主题切换为系统', () => {
  const mockSetTheme = vi.fn();

  (useSettingsStore as vi.Mock).mockReturnValue({
    theme: 'light',
    apiEndpoint: 'http://localhost:8000',
    modelConfig: { model: 'qwen-3.5-plus', temperature: '0.7' },
    setTheme: mockSetTheme,
    setApiEndpoint: vi.fn(),
    setModelConfig: vi.fn(),
  });

  render(<Settings />);

  const systemThemeButton = screen.getByText('系统').closest('button');
  fireEvent.click(systemThemeButton!);

  expect(mockSetTheme).toHaveBeenCalledWith('system');
});

test('Settings 页面 - 保存 API 配置', () => {
  const mockSetApiEndpoint = vi.fn();

  (useSettingsStore as vi.Mock).mockReturnValue({
    theme: 'system',
    apiEndpoint: 'http://localhost:8000',
    modelConfig: { model: 'qwen-3.5-plus', temperature: '0.7' },
    setTheme: vi.fn(),
    setApiEndpoint: mockSetApiEndpoint,
    setModelConfig: vi.fn(),
  });

  render(<Settings />);

  const apiInput = screen.getByPlaceholderText('http://localhost:8000');
  fireEvent.change(apiInput, { target: { value: 'http://new-api:8000' } });

  const saveButton = screen.getByText('保存配置').closest('button');
  fireEvent.click(saveButton!);

  vi.advanceTimersByTime(600);

  expect(mockSetApiEndpoint).toHaveBeenCalledWith('http://new-api:8000');
});

test('Settings 页面 - 保存 API 配置后显示提示', () => {
  const mockSetApiEndpoint = vi.fn();

  (useSettingsStore as vi.Mock).mockReturnValue({
    theme: 'system',
    apiEndpoint: 'http://localhost:8000',
    modelConfig: { model: 'qwen-3.5-plus', temperature: '0.7' },
    setTheme: vi.fn(),
    setApiEndpoint: mockSetApiEndpoint,
    setModelConfig: vi.fn(),
  });

  render(<Settings />);

  const saveButton = screen.getAllByText('保存配置')[0];
  fireEvent.click(saveButton);

  vi.advanceTimersByTime(600);

  expect(screen.getByText('设置已保存！')).toBeInTheDocument();

  vi.advanceTimersByTime(2000);
  expect(screen.queryByText('设置已保存！')).not.toBeInTheDocument();
});

test('Settings 页面 - 保存模型配置', () => {
  const mockSetModelConfig = vi.fn();

  (useSettingsStore as vi.Mock).mockReturnValue({
    theme: 'system',
    apiEndpoint: 'http://localhost:8000',
    modelConfig: { model: 'qwen-3.5-plus', temperature: '0.7' },
    setTheme: vi.fn(),
    setApiEndpoint: vi.fn(),
    setModelConfig: mockSetModelConfig,
  });

  render(<Settings />);

  const modelSelect = screen.getByDisplayValue('qwen-3.5-plus');
  fireEvent.change(modelSelect, { target: { value: 'gpt-4o' } });

  const saveButton = screen.getAllByText('保存配置')[1];
  fireEvent.click(saveButton);

  vi.advanceTimersByTime(600);

  expect(mockSetModelConfig).toHaveBeenCalledWith({ model: 'gpt-4o', temperature: '0.7' });
});

test('Settings 页面 - 调整温度滑块', () => {
  const mockSetModelConfig = vi.fn();

  (useSettingsStore as vi.Mock).mockReturnValue({
    theme: 'system',
    apiEndpoint: 'http://localhost:8000',
    modelConfig: { model: 'qwen-3.5-plus', temperature: '0.7' },
    setTheme: vi.fn(),
    setApiEndpoint: vi.fn(),
    setModelConfig: mockSetModelConfig,
  });

  render(<Settings />);

  const temperatureSlider = screen.getByRole('slider');
  fireEvent.change(temperatureSlider, { target: { value: '0.9' } });

  expect(mockSetModelConfig).toHaveBeenCalledWith({ model: 'qwen-3.5-plus', temperature: '0.9' });
});

test('Settings 页面 - 重置所有设置', () => {
  const mockSetTheme = vi.fn();
  const mockSetApiEndpoint = vi.fn();
  const mockSetModelConfig = vi.fn();

  global.confirm = vi.fn(() => true);

  (useSettingsStore as vi.Mock).mockReturnValue({
    theme: 'dark',
    apiEndpoint: 'http://custom-api:9000',
    modelConfig: { model: 'gpt-4o', temperature: '0.9' },
    setTheme: mockSetTheme,
    setApiEndpoint: mockSetApiEndpoint,
    setModelConfig: mockSetModelConfig,
  });

  render(<Settings />);

  const resetButton = screen.getByText('重置所有设置');
  fireEvent.click(resetButton);

  expect(mockSetTheme).toHaveBeenCalledWith('system');
  expect(mockSetApiEndpoint).toHaveBeenCalledWith('http://localhost:8000');
  expect(mockSetModelConfig).toHaveBeenCalledWith({ model: 'qwen-3.5-plus', temperature: '0.7' });
});

test('Settings 页面 - 取消重置', () => {
  const mockSetTheme = vi.fn();

  global.confirm = vi.fn(() => false);

  (useSettingsStore as vi.Mock).mockReturnValue({
    theme: 'dark',
    apiEndpoint: 'http://localhost:8000',
    modelConfig: { model: 'qwen-3.5-plus', temperature: '0.7' },
    setTheme: mockSetTheme,
    setApiEndpoint: vi.fn(),
    setModelConfig: vi.fn(),
  });

  render(<Settings />);

  const resetButton = screen.getByText('重置所有设置');
  fireEvent.click(resetButton);

  expect(mockSetTheme).not.toHaveBeenCalled();
});

test('Settings 页面 - 显示当前主题', () => {
  (useSettingsStore as vi.Mock).mockReturnValue({
    theme: 'dark',
    apiEndpoint: 'http://localhost:8000',
    modelConfig: { model: 'qwen-3.5-plus', temperature: '0.7' },
    setTheme: vi.fn(),
    setApiEndpoint: vi.fn(),
    setModelConfig: vi.fn(),
  });

  render(<Settings />);

  expect(screen.getAllByText('深色')[0]).toBeInTheDocument();
});

test('Settings 页面 - 快捷键显示', () => {
  (useSettingsStore as vi.Mock).mockReturnValue({
    theme: 'system',
    apiEndpoint: 'http://localhost:8000',
    modelConfig: { model: 'qwen-3.5-plus', temperature: '0.7' },
    setTheme: vi.fn(),
    setApiEndpoint: vi.fn(),
    setModelConfig: vi.fn(),
  });

  render(<Settings />);

  expect(screen.getByText('新建项目')).toBeInTheDocument();
  expect(screen.getByText('Ctrl + N')).toBeInTheDocument();
  expect(screen.getByText('Ctrl + K')).toBeInTheDocument();
  expect(screen.getByText('Ctrl + S')).toBeInTheDocument();
});

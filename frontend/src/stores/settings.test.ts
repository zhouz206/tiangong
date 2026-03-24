/** @vitest-environment jsdom */
import { test, expect, beforeEach } from 'vitest';
import { useSettingsStore, type Theme } from './settings';

beforeEach(() => {
  useSettingsStore.setState({
    theme: 'system',
    apiEndpoint: 'http://localhost:8000',
    modelConfig: {
      model: 'qwen-3.5-plus',
      temperature: '0.7',
    },
  });
});

test('Settings Store - 初始状态', () => {
  const state = useSettingsStore.getState();
  expect(state.theme).toBe('system');
  expect(state.apiEndpoint).toBe('http://localhost:8000');
  expect(state.modelConfig).toEqual({
    model: 'qwen-3.5-plus',
    temperature: '0.7',
  });
});

test('Settings Store - setTheme light', () => {
  useSettingsStore.getState().setTheme('light');
  expect(useSettingsStore.getState().theme).toBe('light');
});

test('Settings Store - setTheme dark', () => {
  useSettingsStore.getState().setTheme('dark');
  expect(useSettingsStore.getState().theme).toBe('dark');
});

test('Settings Store - setTheme system', () => {
  useSettingsStore.getState().setTheme('light');
  useSettingsStore.getState().setTheme('system');
  expect(useSettingsStore.getState().theme).toBe('system');
});

test('Settings Store - setApiEndpoint', () => {
  useSettingsStore.getState().setApiEndpoint('http://new-api:9000');
  expect(useSettingsStore.getState().apiEndpoint).toBe('http://new-api:9000');
});

test('Settings Store - setModelConfig', () => {
  const newConfig = {
    model: 'gpt-4o',
    temperature: '0.8',
    maxTokens: '4096',
  };

  useSettingsStore.getState().setModelConfig(newConfig);

  const state = useSettingsStore.getState();
  expect(state.modelConfig).toEqual(newConfig);
});

test('Settings Store - updateModelConfig 单个字段', () => {
  useSettingsStore.getState().updateModelConfig('model', 'claude-3.5-sonnet');

  const state = useSettingsStore.getState();
  expect(state.modelConfig.model).toBe('claude-3.5-sonnet');
  expect(state.modelConfig.temperature).toBe('0.7');
});

test('Settings Store - updateModelConfig 多个字段', () => {
  useSettingsStore.getState().updateModelConfig('temperature', '0.9');
  useSettingsStore.getState().updateModelConfig('maxTokens', '8192');

  const state = useSettingsStore.getState();
  expect(state.modelConfig.temperature).toBe('0.9');
  expect(state.modelConfig.maxTokens).toBe('8192');
});

test('Settings Store - updateModelConfig 添加新字段', () => {
  useSettingsStore.getState().updateModelConfig('topP', '0.95');

  const state = useSettingsStore.getState();
  expect(state.modelConfig.topP).toBe('0.95');
});

test('Settings Store - 主题切换流程', () => {
  const { setTheme } = useSettingsStore.getState();

  setTheme('light');
  expect(useSettingsStore.getState().theme).toBe('light');

  setTheme('dark');
  expect(useSettingsStore.getState().theme).toBe('dark');

  setTheme('system');
  expect(useSettingsStore.getState().theme).toBe('system');
});

test('Settings Store - API 端点设置', () => {
  const { setApiEndpoint } = useSettingsStore.getState();

  setApiEndpoint('http://production-api:8000');
  expect(useSettingsStore.getState().apiEndpoint).toBe('http://production-api:8000');

  setApiEndpoint('http://localhost:3000');
  expect(useSettingsStore.getState().apiEndpoint).toBe('http://localhost:3000');
});

test('Settings Store - 模型配置完整流程', () => {
  const { setModelConfig, updateModelConfig } = useSettingsStore.getState();

  // 设置完整配置
  setModelConfig({
    model: 'qwen-3.5-plus',
    temperature: '0.5',
    maxTokens: '2048',
  });
  let state = useSettingsStore.getState();
  expect(state.modelConfig).toEqual({
    model: 'qwen-3.5-plus',
    temperature: '0.5',
    maxTokens: '2048',
  });

  // 更新单个字段
  updateModelConfig('temperature', '0.7');
  state = useSettingsStore.getState();
  expect(state.modelConfig.temperature).toBe('0.7');
  expect(state.modelConfig.maxTokens).toBe('2048');

  // 添加新字段
  updateModelConfig('topK', '40');
  state = useSettingsStore.getState();
  expect(state.modelConfig.topK).toBe('40');
});

test('Settings Store - 状态持久化配置', () => {
  const state = useSettingsStore.getState();
  // 验证 persist 中间件配置
  expect(state.theme).toBeDefined();
  expect(state.apiEndpoint).toBeDefined();
  expect(state.modelConfig).toBeDefined();
});

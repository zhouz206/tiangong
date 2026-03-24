import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { useSettingsStore } from '../stores/settings';

export default function Settings() {
  const { theme, apiEndpoint, modelConfig, setTheme, setApiEndpoint, setModelConfig } = useSettingsStore();
  const [localApiEndpoint, setLocalApiEndpoint] = useState(apiEndpoint);
  const [localModelConfig, setLocalModelConfig] = useState(modelConfig);
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  // 同步主题到 HTML 元素
  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove('light', 'dark');
    if (theme === 'system') {
      const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.classList.add(systemDark ? 'dark' : 'light');
    } else {
      root.classList.add(theme);
    }
  }, [theme]);

  // 监听系统主题变化
  useEffect(() => {
    if (theme !== 'system') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = () => {
      const root = document.documentElement;
      root.classList.remove('light', 'dark');
      root.classList.add(mediaQuery.matches ? 'dark' : 'light');
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme]);

  const handleSaveApi = () => {
    setSaving(true);
    // 模拟 API 验证
    setTimeout(() => {
      setApiEndpoint(localApiEndpoint);
      setSaving(false);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    }, 500);
  };

  const handleSaveModel = () => {
    setSaving(true);
    setModelConfig(localModelConfig);
    setTimeout(() => {
      setSaving(false);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    }, 500);
  };

  const handleReset = () => {
    if (confirm('确定要重置所有设置吗？')) {
      setTheme('system');
      setApiEndpoint('http://localhost:8000');
      setModelConfig({
        model: 'qwen-3.5-plus',
        temperature: '0.7'
      });
      setLocalApiEndpoint('http://localhost:8000');
      setLocalModelConfig({
        model: 'qwen-3.5-plus',
        temperature: '0.7'
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* 页面标题 */}
      <div className="flex justify-between items-center flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">设置</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">配置你的工作空间和偏好</p>
        </div>
        <Button variant="outline" onClick={handleReset}>重置所有设置</Button>
      </div>

      {/* 保存提示 */}
      {saved && (
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
          <p className="text-green-600 dark:text-green-400">设置已保存！</p>
        </div>
      )}

      {/* 主题设置 */}
      <Card>
        <CardHeader>
          <CardTitle>主题</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <button
              onClick={() => setTheme('light')}
              className={`p-6 rounded-lg border-2 transition-all ${
                theme === 'light'
                  ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="text-3xl mb-2">☀️</div>
              <div className="font-medium text-gray-900 dark:text-white">浅色</div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">明亮主题</div>
            </button>
            <button
              onClick={() => setTheme('dark')}
              className={`p-6 rounded-lg border-2 transition-all ${
                theme === 'dark'
                  ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="text-3xl mb-2">🌙</div>
              <div className="font-medium text-gray-900 dark:text-white">深色</div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">护眼主题</div>
            </button>
            <button
              onClick={() => setTheme('system')}
              className={`p-6 rounded-lg border-2 transition-all ${
                theme === 'system'
                  ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="text-3xl mb-2">💻</div>
              <div className="font-medium text-gray-900 dark:text-white">系统</div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">跟随系统</div>
            </button>
          </div>
          <div className="mt-4 flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
            <span>当前主题：</span>
            <span className="font-medium">
              {theme === 'light' ? '浅色' : theme === 'dark' ? '深色' : '系统（自动跟随）'}
            </span>
          </div>
        </CardContent>
      </Card>

      {/* API 配置 */}
      <Card>
        <CardHeader>
          <CardTitle>API 配置</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              API 端点
            </label>
            <Input
              value={localApiEndpoint}
              onChange={(e) => setLocalApiEndpoint(e.target.value)}
              placeholder="http://localhost:8000"
            />
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              后端 API 服务地址
            </p>
          </div>
          <div className="flex items-center gap-4">
            <Button onClick={handleSaveApi} disabled={saving}>
              {saving ? '保存中...' : '保存配置'}
            </Button>
            <span className="text-sm text-gray-500">
              {apiEndpoint === localApiEndpoint ? '已保存' : '未保存'}
            </span>
          </div>
        </CardContent>
      </Card>

      {/* 模型配置 */}
      <Card>
        <CardHeader>
          <CardTitle>模型配置</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              默认模型
            </label>
            <select
              value={localModelConfig.model || 'qwen-3.5-plus'}
              onChange={(e) => setLocalModelConfig({ ...localModelConfig, model: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-800 dark:text-white"
            >
              <option value="qwen-3.5-plus">Qwen 3.5 Plus</option>
              <option value="gpt-4o">GPT-4o</option>
              <option value="claude-3.5-sonnet">Claude 3.5 Sonnet</option>
              <option value="ollama-local">Ollama (本地)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              温度 (Temperature)
            </label>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={localModelConfig.temperature || '0.7'}
                onChange={(e) => setLocalModelConfig({ ...localModelConfig, temperature: e.target.value })}
                className="flex-1"
              />
              <span className="text-sm font-medium w-12 text-right">
                {localModelConfig.temperature || '0.7'}
              </span>
            </div>
            <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400 mt-1">
              <span>精确 (0)</span>
              <span>创意 (1)</span>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              最大生成长度
            </label>
            <input
              type="number"
              value={localModelConfig.maxTokens || '4096'}
              onChange={(e) => setLocalModelConfig({ ...localModelConfig, maxTokens: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-800 dark:text-white"
              min="256"
              max="8192"
              step="256"
            />
          </div>
          <div className="flex items-center gap-4">
            <Button onClick={handleSaveModel} disabled={saving}>
              {saving ? '保存中...' : '保存配置'}
            </Button>
            <span className="text-sm text-gray-500">
              {JSON.stringify(modelConfig) === JSON.stringify(localModelConfig) ? '已保存' : '未保存'}
            </span>
          </div>
        </CardContent>
      </Card>

      {/* 快捷键设置 */}
      <Card>
        <CardHeader>
          <CardTitle>快捷键</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b dark:border-gray-700">
              <span className="text-sm text-gray-700 dark:text-gray-300">新建项目</span>
              <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded text-xs font-mono">Ctrl + N</kbd>
            </div>
            <div className="flex justify-between items-center py-2 border-b dark:border-gray-700">
              <span className="text-sm text-gray-700 dark:text-gray-300">搜索</span>
              <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded text-xs font-mono">Ctrl + K</kbd>
            </div>
            <div className="flex justify-between items-center py-2 border-b dark:border-gray-700">
              <span className="text-sm text-gray-700 dark:text-gray-300">保存</span>
              <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded text-xs font-mono">Ctrl + S</kbd>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-sm text-gray-700 dark:text-gray-300">帮助</span>
              <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded text-xs font-mono">?</kbd>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 关于 */}
      <Card>
        <CardHeader>
          <CardTitle>关于</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              <strong className="text-gray-900 dark:text-white">天工 (TianGong)</strong> v1.0.0
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              让 AI 像专业团队一样为你工作
            </p>
            <div className="pt-2 border-t dark:border-gray-700">
              <p className="text-xs text-gray-500">
                基于 gstack 流程构建 | MIT License
              </p>
            </div>
            <div className="pt-2 flex gap-4">
              <a href="#" className="text-sm text-blue-600 hover:underline">查看文档</a>
              <a href="#" className="text-sm text-blue-600 hover:underline">GitHub</a>
              <a href="#" className="text-sm text-blue-600 hover:underline">反馈问题</a>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

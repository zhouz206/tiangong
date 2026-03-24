import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { useSettingsStore } from '../stores/settings';

export default function Settings() {
  const { theme, apiEndpoint, setTheme, setApiEndpoint } = useSettingsStore();
  const [localApiEndpoint, setLocalApiEndpoint] = React.useState(apiEndpoint);
  
  const handleSave = () => {
    setApiEndpoint(localApiEndpoint);
    alert('设置已保存！');
  };
  
  return (
    <div className="space-y-6 max-w-4xl">
      {/* 页面标题 */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">设置</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">配置你的工作空间和偏好</p>
      </div>
      
      {/* 主题设置 */}
      <Card>
        <CardHeader>
          <CardTitle>主题</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <Button
              variant={theme === 'light' ? 'primary' : 'outline'}
              onClick={() => setTheme('light')}
            >
              ☀️ 浅色
            </Button>
            <Button
              variant={theme === 'dark' ? 'primary' : 'outline'}
              onClick={() => setTheme('dark')}
            >
              🌙 深色
            </Button>
            <Button
              variant={theme === 'system' ? 'primary' : 'outline'}
              onClick={() => setTheme('system')}
            >
              💻 系统
            </Button>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
            当前主题：{theme === 'light' ? '浅色' : theme === 'dark' ? '深色' : '系统'}
          </p>
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
          <Button onClick={handleSave}>保存配置</Button>
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
            <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-800 dark:text-white">
              <option>Qwen 3.5 Plus</option>
              <option>GPT-4o</option>
              <option>Claude-3.5-Sonnet</option>
              <option>Ollama (本地)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              温度 (Temperature)
            </label>
            <input 
              type="range" 
              min="0" 
              max="1" 
              step="0.1" 
              defaultValue="0.7"
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400">
              <span>精确 (0)</span>
              <span>创意 (1)</span>
            </div>
          </div>
          <Button>保存配置</Button>
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
              <strong>天工 (TianGong)</strong> v1.0.0
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              让 AI 像专业团队一样为你工作
            </p>
            <div className="pt-2 border-t dark:border-gray-700">
              <p className="text-xs text-gray-500">
                基于 gstack 流程构建 | MIT License
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

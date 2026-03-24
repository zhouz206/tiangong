import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { useSettingsStore } from '../stores/settings';

export default function Settings() {
  const { theme, apiEndpoint, setTheme, setApiEndpoint } = useSettingsStore();
  
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">设置</h1>
      
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
              浅色
            </Button>
            <Button
              variant={theme === 'dark' ? 'primary' : 'outline'}
              onClick={() => setTheme('dark')}
            >
              深色
            </Button>
            <Button
              variant={theme === 'system' ? 'primary' : 'outline'}
              onClick={() => setTheme('system')}
            >
              系统
            </Button>
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
            <label className="block text-sm font-medium mb-1">API 端点</label>
            <Input
              value={apiEndpoint}
              onChange={(e) => setApiEndpoint(e.target.value)}
              placeholder="http://localhost:8000"
            />
          </div>
          <Button>保存配置</Button>
        </CardContent>
      </Card>
      
      {/* 模型配置 */}
      <Card>
        <CardHeader>
          <CardTitle>模型配置</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">默认模型</label>
            <select className="w-full px-3 py-2 border rounded-md dark:bg-gray-800 dark:border-gray-700">
              <option>Qwen 3.5 Plus</option>
              <option>GPT-4o</option>
              <option>Claude-3.5-Sonnet</option>
            </select>
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
          <p className="text-sm text-gray-600 dark:text-gray-400">
            天工 (TianGong) v1.0.0
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
            让 AI 像专业团队一样为你工作
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

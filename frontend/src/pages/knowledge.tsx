import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { useKnowledgeStore } from '../stores/knowledge';

// Mock 数据
const mockDocuments = [
  { id: '1', title: '项目需求文档', category: '技术文档', tags: ['需求', '规划'], created_at: '2026-03-20' },
  { id: '2', title: '架构设计文档', category: '技术文档', tags: ['架构', '设计'], created_at: '2026-03-21' },
  { id: '3', title: 'API 接口文档', category: '技术文档', tags: ['API', '接口'], created_at: '2026-03-22' },
  { id: '4', title: '测试报告', category: '测试报告', tags: ['测试', '质量'], created_at: '2026-03-23' },
  { id: '5', title: '用户手册', category: '产品文档', tags: ['用户', '手册'], created_at: '2026-03-24' },
];

const mockCategories = ['技术文档', '产品文档', '测试报告', '会议纪要', '流程规范'];
const mockTags = ['需求', '架构', 'API', '测试', '用户', '设计', '规划'];

export default function Knowledge() {
  const { documents, setDocuments } = useKnowledgeStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  
  React.useEffect(() => {
    if (documents.length === 0) {
      setDocuments(mockDocuments);
    }
  }, []);
  
  const docList = documents.length > 0 ? documents : mockDocuments;
  
  const filteredDocs = docList.filter(doc => {
    const matchesSearch = doc.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || doc.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });
  
  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">知识库</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">管理和搜索项目知识</p>
        </div>
        <Button>上传文档</Button>
      </div>
      
      {/* 搜索和筛选 */}
      <div className="flex flex-col md:flex-row gap-4">
        <Input
          placeholder="搜索文档..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1"
          icon={
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          }
        />
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-800 dark:text-white"
        >
          <option value="all">全部分类</option>
          {mockCategories.map(cat => (
            <option key={cat} value={cat}>{cat}</option>
          ))}
        </select>
      </div>
      
      {/* 标签云 */}
      <Card>
        <CardHeader>
          <CardTitle>热门标签</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {mockTags.map(tag => (
              <Badge key={tag} variant="default" className="cursor-pointer hover:bg-blue-600">
                {tag}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>
      
      {/* 文档列表 */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          文档列表 ({filteredDocs.length})
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredDocs.map(doc => (
            <Card key={doc.id} className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <CardTitle className="text-lg">{doc.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between mb-2">
                  <Badge variant="default">{doc.category}</Badge>
                  <span className="text-xs text-gray-500">{doc.created_at}</span>
                </div>
                <div className="flex flex-wrap gap-1">
                  {doc.tags.map(tag => (
                    <Badge key={tag} variant="default" className="text-xs bg-gray-100 dark:bg-gray-700">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}

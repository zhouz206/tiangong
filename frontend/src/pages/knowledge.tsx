import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { useKnowledgeStore } from '../stores/knowledge';

export default function Knowledge() {
  const { documents, categories, tags } = useKnowledgeStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  
  const defaultDocs = [
    { id: '1', title: '项目需求文档', category: '技术文档', tags: ['需求', '规划'] },
    { id: '2', title: '架构设计文档', category: '技术文档', tags: ['架构', '设计'] },
    { id: '3', title: 'API 接口文档', category: '技术文档', tags: ['API', '接口'] },
    { id: '4', title: '测试报告', category: '测试报告', tags: ['测试', '质量'] },
    { id: '5', title: '用户手册', category: '产品文档', tags: ['用户', '手册'] }
  ];
  
  const defaultCategories = ['技术文档', '产品文档', '测试报告', '会议纪要'];
  const defaultTags = ['需求', '架构', 'API', '测试', '用户'];
  
  const docList = documents.length > 0 ? documents : defaultDocs;
  const categoryList = categories.length > 0 ? categories : defaultCategories;
  const tagList = tags.length > 0 ? tags : defaultTags;
  
  const filteredDocs = docList.filter(doc => {
    const matchesSearch = doc.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || doc.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">知识库</h1>
        <Button>上传文档</Button>
      </div>
      
      {/* 搜索和筛选 */}
      <div className="flex flex-col md:flex-row gap-4">
        <Input
          placeholder="搜索文档..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1"
        />
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="px-4 py-2 border rounded-md dark:bg-gray-800 dark:border-gray-700"
        >
          <option value="all">全部分类</option>
          {categoryList.map(cat => (
            <option key={cat} value={cat}>{cat}</option>
          ))}
        </select>
      </div>
      
      {/* 标签云 */}
      <div className="flex flex-wrap gap-2">
        {tagList.map(tag => (
          <Badge key={tag} variant="default">{tag}</Badge>
        ))}
      </div>
      
      {/* 文档列表 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredDocs.map(doc => (
          <Card key={doc.id} className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <CardTitle className="text-lg">{doc.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <Badge variant="default">{doc.category}</Badge>
              </div>
              <div className="flex flex-wrap gap-1 mt-2">
                {doc.tags.map(tag => (
                  <Badge key={tag} variant="default" className="text-xs">{tag}</Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Loading } from '../components/ui/loading';
import { useKnowledgeStore, type KnowledgeDocument } from '../stores/knowledge';
import { knowledgeApi } from '../utils/api';

// Mock 数据用于降级
const mockDocuments: KnowledgeDocument[] = [
  { id: '1', title: '项目需求文档', category: '技术文档', tags: ['需求', '规划'], created_at: '2026-03-20' },
  { id: '2', title: '架构设计文档', category: '技术文档', tags: ['架构', '设计'], created_at: '2026-03-21' },
  { id: '3', title: 'API 接口文档', category: '技术文档', tags: ['API', '接口'], created_at: '2026-03-22' },
  { id: '4', title: '测试报告', category: '测试报告', tags: ['测试', '质量'], created_at: '2026-03-23' },
  { id: '5', title: '用户手册', category: '产品文档', tags: ['用户', '手册'], created_at: '2026-03-24' },
];

const mockCategories = ['技术文档', '产品文档', '测试报告', '会议纪要', '流程规范'];
const mockTags = ['需求', '架构', 'API', '测试', '用户', '设计', '规划'];

export default function Knowledge() {
  const { documents, setDocuments, addDocument, deleteDocument, categories, setCategories, tags, setTags, searchQuery, setSearchQuery } = useKnowledgeStore();
  const [loading, setLoading] = useState(false);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  React.useEffect(() => {
    loadKnowledge();
  }, []);

  const loadKnowledge = async () => {
    setLoading(true);
    setError(null);
    try {
      const [docsRes, categoriesRes, tagsRes] = await Promise.all([
        knowledgeApi.search(''),
        knowledgeApi.getCategories(),
        knowledgeApi.getTags()
      ]);
      setDocuments(docsRes.documents || docsRes || mockDocuments);
      setCategories(categoriesRes.categories || categoriesRes || mockCategories);
      setTags(tagsRes.tags || tagsRes || mockTags);
    } catch (err) {
      console.error('加载知识库失败:', err);
      setError('加载失败，使用本地数据');
      if (documents.length === 0) {
        setDocuments(mockDocuments);
      }
      if (categories.length === 0) {
        setCategories(mockCategories);
      }
      if (tags.length === 0) {
        setTags(mockTags);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleUploadDocument = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const newDoc: KnowledgeDocument = {
      id: `doc-${Date.now()}`,
      title: formData.get('title') as string,
      category: formData.get('category') as string,
      tags: (formData.get('tags') as string).split(',').map(t => t.trim()).filter(Boolean),
      content: formData.get('content') as string,
      created_at: new Date().toISOString().split('T')[0]
    };

    try {
      await knowledgeApi.addDocument(newDoc);
    } catch (err) {
      console.error('上传文档失败:', err);
    }

    // 更新本地状态
    addDocument(newDoc);
    setUploadDialogOpen(false);
  };

  const handleDeleteDocument = async (docId: string) => {
    if (!confirm('确定要删除这个文档吗？')) return;

    try {
      await knowledgeApi.deleteDocument(docId);
    } catch (err) {
      console.error('删除文档失败:', err);
    }

    // 更新本地状态
    deleteDocument(docId);
  };

  const docList = documents.length > 0 ? documents : mockDocuments;
  const categoryList = categories.length > 0 ? categories : mockCategories;
  const tagList = tags.length > 0 ? tags : mockTags;

  const [selectedCategory, setSelectedCategory] = useState('all');

  const filteredDocs = docList.filter(doc => {
    const matchesSearch = doc.title.toLowerCase().includes((searchQuery || '').toLowerCase());
    const matchesCategory = selectedCategory === 'all' || doc.category === selectedCategory;
    const matchesTag = !selectedTag || doc.tags?.includes(selectedTag);
    return matchesSearch && matchesCategory && matchesTag;
  });

  if (loading && documents.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loading size="lg" text="加载知识库..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex justify-between items-center flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">知识库</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">管理和搜索项目知识</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={loadKnowledge} disabled={loading}>
            {loading ? '刷新中...' : '刷新'}
          </Button>
          <Button onClick={() => setUploadDialogOpen(true)}>上传文档</Button>
        </div>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
          <p className="text-yellow-600 dark:text-yellow-400">{error}</p>
        </div>
      )}

      {/* 搜索和筛选 */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Input
            placeholder="搜索文档..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
          <svg className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-800 dark:text-white"
        >
          <option value="all">全部分类</option>
          {categoryList.map(cat => (
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
            <Badge
              variant={!selectedTag ? 'success' : 'default'}
              className="cursor-pointer"
              onClick={() => setSelectedTag(null)}
            >
              全部
            </Badge>
            {tagList.map(tag => (
              <Badge
                key={tag}
                variant={selectedTag === tag ? 'success' : 'default'}
                className="cursor-pointer hover:bg-blue-600"
                onClick={() => setSelectedTag(selectedTag === tag ? null : tag)}
              >
                {tag}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 文档列表 */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            文档列表 ({filteredDocs.length})
          </h2>
          {(searchQuery || selectedCategory !== 'all' || selectedTag) && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setSearchQuery('');
                setSelectedCategory('all');
                setSelectedTag(null);
              }}
            >
              清除筛选
            </Button>
          )}
        </div>
        {filteredDocs.length === 0 ? (
          <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow-md">
            <p className="text-gray-600 dark:text-gray-400">暂无文档</p>
            <Button className="mt-4" onClick={() => setUploadDialogOpen(true)}>上传第一个文档</Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredDocs.map(doc => (
              <Card key={doc.id} className="hover:shadow-lg transition-shadow cursor-pointer group">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-lg">{doc.title}</CardTitle>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteDocument(doc.id);
                      }}
                      className="opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-700 transition-opacity p-1"
                      title="删除文档"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between mb-2">
                    <Badge variant="default">{doc.category}</Badge>
                    <span className="text-xs text-gray-500">{doc.created_at}</span>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {doc.tags?.map(tag => (
                      <Badge
                        key={tag}
                        variant="default"
                        className="text-xs bg-gray-100 dark:bg-gray-700 cursor-pointer hover:bg-blue-100 dark:hover:bg-blue-900"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedTag(selectedTag === tag ? null : tag);
                        }}
                      >
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* 上传文档对话框 */}
      {uploadDialogOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">上传文档</h2>
            <form onSubmit={handleUploadDocument}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">文档标题</label>
                  <input
                    name="title"
                    required
                    placeholder="输入文档标题"
                    className="w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">分类</label>
                  <select
                    name="category"
                    required
                    className="w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  >
                    {categoryList.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                    <option value="其他">其他</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">标签（用逗号分隔）</label>
                  <input
                    name="tags"
                    placeholder="例如：需求，规划，设计"
                    className="w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">内容摘要</label>
                  <textarea
                    name="content"
                    placeholder="输入文档内容摘要..."
                    rows={4}
                    className="w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                </div>
              </div>
              <div className="flex gap-2 mt-6">
                <Button type="button" variant="outline" onClick={() => setUploadDialogOpen(false)} className="flex-1">取消</Button>
                <Button type="submit" className="flex-1">上传</Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

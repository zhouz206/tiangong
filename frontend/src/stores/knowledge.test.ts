/** @vitest-environment jsdom */
import { test, expect, beforeEach } from 'vitest';
import { useKnowledgeStore, type KnowledgeDocument } from './knowledge';

beforeEach(() => {
  useKnowledgeStore.setState({
    documents: [],
    categories: [],
    tags: [],
    searchQuery: '',
    loading: false,
    error: null,
  });
});

test('Knowledge Store - 初始状态', () => {
  const state = useKnowledgeStore.getState();
  expect(state.documents).toEqual([]);
  expect(state.categories).toEqual([]);
  expect(state.tags).toEqual([]);
  expect(state.searchQuery).toBe('');
  expect(state.loading).toBe(false);
  expect(state.error).toBeNull();
});

test('Knowledge Store - setDocuments', () => {
  const mockDocuments: KnowledgeDocument[] = [
    { id: '1', title: '文档 1', category: '技术文档', tags: ['需求'], created_at: '2026-03-20' },
    { id: '2', title: '文档 2', category: '产品文档', tags: ['用户'], created_at: '2026-03-21' },
  ];

  useKnowledgeStore.getState().setDocuments(mockDocuments);

  const state = useKnowledgeStore.getState();
  expect(state.documents).toEqual(mockDocuments);
  expect(state.error).toBeNull();
});

test('Knowledge Store - addDocument', () => {
  useKnowledgeStore.getState().setDocuments([
    { id: '1', title: '文档 1', category: '技术文档', tags: ['需求'], created_at: '2026-03-20' },
  ]);

  const newDoc: KnowledgeDocument = {
    id: '2',
    title: '新文档',
    category: '技术文档',
    tags: ['设计'],
    content: '内容',
    created_at: '2026-03-22',
  };

  useKnowledgeStore.getState().addDocument(newDoc);

  const state = useKnowledgeStore.getState();
  expect(state.documents).toHaveLength(2);
  expect(state.documents[1]).toEqual(newDoc);
});

test('Knowledge Store - deleteDocument', () => {
  useKnowledgeStore.getState().setDocuments([
    { id: '1', title: '文档 1', category: '技术文档', tags: ['需求'], created_at: '2026-03-20' },
    { id: '2', title: '文档 2', category: '产品文档', tags: ['用户'], created_at: '2026-03-21' },
  ]);

  useKnowledgeStore.getState().deleteDocument('1');

  const state = useKnowledgeStore.getState();
  expect(state.documents).toHaveLength(1);
  expect(state.documents[0].id).toBe('2');
});

test('Knowledge Store - setCategories', () => {
  const categories = ['技术文档', '产品文档', '测试报告'];

  useKnowledgeStore.getState().setCategories(categories);

  const state = useKnowledgeStore.getState();
  expect(state.categories).toEqual(categories);
});

test('Knowledge Store - setTags', () => {
  const tags = ['需求', '架构', 'API', '测试'];

  useKnowledgeStore.getState().setTags(tags);

  const state = useKnowledgeStore.getState();
  expect(state.tags).toEqual(tags);
});

test('Knowledge Store - setSearchQuery', () => {
  useKnowledgeStore.getState().setSearchQuery('搜索关键词');

  const state = useKnowledgeStore.getState();
  expect(state.searchQuery).toBe('搜索关键词');
});

test('Knowledge Store - setSearchQuery 清空', () => {
  useKnowledgeStore.getState().setSearchQuery('关键词');
  useKnowledgeStore.getState().setSearchQuery('');

  const state = useKnowledgeStore.getState();
  expect(state.searchQuery).toBe('');
});

test('Knowledge Store - setLoading', () => {
  useKnowledgeStore.getState().setLoading(true);
  expect(useKnowledgeStore.getState().loading).toBe(true);

  useKnowledgeStore.getState().setLoading(false);
  expect(useKnowledgeStore.getState().loading).toBe(false);
});

test('Knowledge Store - setError', () => {
  useKnowledgeStore.getState().setError('错误信息');
  expect(useKnowledgeStore.getState().error).toBe('错误信息');

  useKnowledgeStore.getState().setError(null);
  expect(useKnowledgeStore.getState().error).toBeNull();
});

test('Knowledge Store - addDocument 带完整字段', () => {
  const fullDoc: KnowledgeDocument = {
    id: '1',
    title: '完整文档',
    category: '技术文档',
    tags: ['需求', '规划'],
    content: '这是文档内容摘要',
    created_at: '2026-03-25',
  };

  useKnowledgeStore.getState().addDocument(fullDoc);

  const state = useKnowledgeStore.getState();
  expect(state.documents[0]).toEqual(fullDoc);
  expect(state.documents[0].tags).toHaveLength(2);
});

test('Knowledge Store - deleteDocument 不存在的 ID', () => {
  useKnowledgeStore.getState().setDocuments([
    { id: '1', title: '文档 1', category: '技术文档', tags: [], created_at: '2026-03-20' },
  ]);

  useKnowledgeStore.getState().deleteDocument('999');

  const state = useKnowledgeStore.getState();
  expect(state.documents).toHaveLength(1);
});

test('Knowledge Store - 筛选操作', () => {
  useKnowledgeStore.getState().setDocuments([
    { id: '1', title: '需求文档', category: '技术文档', tags: ['需求'], created_at: '2026-03-20' },
    { id: '2', title: '用户手册', category: '产品文档', tags: ['用户'], created_at: '2026-03-21' },
    { id: '3', title: 'API 文档', category: '技术文档', tags: ['API'], created_at: '2026-03-22' },
  ]);

  const state = useKnowledgeStore.getState();

  // 按分类筛选
  const techDocs = state.documents.filter(d => d.category === '技术文档');
  expect(techDocs).toHaveLength(2);

  // 按标签筛选
  const taggedDocs = state.documents.filter(d => d.tags?.includes('需求'));
  expect(taggedDocs).toHaveLength(1);

  // 按标题搜索（只匹配包含"文档"的）
  const searchDocs = state.documents.filter(d =>
    d.title.includes('文档')
  );
  expect(searchDocs).toHaveLength(2);
});

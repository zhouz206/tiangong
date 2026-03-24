import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Search, BookOpen, FileText, Link, Code, Lightbulb, MessageSquare, Plus } from 'lucide-react'
import { useKnowledgeStore, KnowledgeDocument } from '@/stores/knowledge-store'
import { knowledgeApi } from '@/utils/api-services'
import { useToast } from '@/hooks/use-toast'
import { DocumentUpload } from '@/components/DocumentUpload'
import { LoadingState } from '@/components/LoadingState'
import { EmptyState } from '@/components/EmptyState'

export default function Knowledge() {
  const { toast } = useToast()
  const { documents, setDocuments, categories, tags, setCategories, setTags, addDocument } = useKnowledgeStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(true)
  const [activeCategory, setActiveCategory] = useState<string | null>(null)
  const [uploadOpen, setUploadOpen] = useState(false)

  useEffect(() => {
    loadKnowledge()
  }, [])

  const loadKnowledge = async () => {
    try {
      setLoading(true)
      const [docResult, catResult, tagResult] = await Promise.all([
        knowledgeApi.getList(),
        knowledgeApi.getCategories(),
        knowledgeApi.getTags(),
      ])
      setDocuments(docResult.data)
      setCategories(catResult.data)
      setTags(tagResult.data)
    } catch (error) {
      toast({
        title: '加载失败',
        description: '无法加载知识库',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  const searchDocuments = async () => {
    if (!searchQuery.trim()) {
      loadKnowledge()
      return
    }
    try {
      const result = await knowledgeApi.search(searchQuery)
      setDocuments(result.data)
    } catch (error) {
      toast({
        title: '搜索失败',
        description: '无法执行搜索',
        variant: 'destructive',
      })
    }
  }

  const getTypeIcon = (type: KnowledgeDocument['type']) => {
    switch (type) {
      case 'project_doc': return FileText
      case 'discussion': return MessageSquare
      case 'reference': return Link
      case 'experience': return Lightbulb
      case 'code_snippet': return Code
      default: return BookOpen
    }
  }

  const getTypeName = (type: KnowledgeDocument['type']) => {
    const names = {
      project_doc: '项目文档',
      discussion: '讨论记录',
      reference: '参考资料',
      experience: '经验总结',
      code_snippet: '代码片段',
    }
    return names[type]
  }

  const filteredDocuments = activeCategory
    ? documents.filter((doc) => doc.category === activeCategory)
    : documents

  const handleUpload = async (data: {
    title: string
    content: string
    type: KnowledgeDocument['type']
    tags: string[]
    category?: string
  }) => {
    try {
      const result = await knowledgeApi.create(data)
      addDocument(result.data as KnowledgeDocument)
      toast({
        title: '上传成功',
        description: `文档"${data.title}"已上传`,
      })
    } catch (error) {
      toast({
        title: '上传失败',
        description: '无法上传文档',
        variant: 'destructive',
      })
    }
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">知识库</h1>
          <p className="text-sm sm:text-base text-muted-foreground">管理和检索项目知识</p>
        </div>
        <Button onClick={() => setUploadOpen(true)} className="w-full sm:w-auto">
          <Plus className="mr-2 h-4 w-4" />
          <span className="hidden sm:inline">添加文档</span>
          <span className="sm:hidden">添加</span>
        </Button>
      </div>

      {/* Search - 移动端优化 */}
      <div className="flex flex-col sm:flex-row gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="搜索知识库..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && searchDocuments()}
            className="pl-10"
          />
        </div>
        {searchQuery && (
          <Button variant="outline" onClick={() => { setSearchQuery(''); loadKnowledge() }} className="w-full sm:w-auto">
            清除
          </Button>
        )}
      </div>

      {/* Documents Grid - 响应式布局优化 */}
      {loading ? (
        <LoadingState type="card" count={6} />
      ) : filteredDocuments.length === 0 ? (
        <EmptyState
          icon="file"
          title={searchQuery ? '没有找到匹配的文档' : '暂无文档'}
          description={searchQuery ? '尝试其他搜索条件' : '上传第一个文档开始知识管理'}
          actionLabel={!searchQuery ? '上传文档' : undefined}
          onAction={() => setUploadOpen(true)}
        />
      ) : (
        <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
          {filteredDocuments.map((doc) => {
            const TypeIcon = getTypeIcon(doc.type)
            return (
              <Card key={doc.id} className="cursor-pointer hover:bg-accent">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <TypeIcon className="h-5 w-5 text-muted-foreground" />
                      <CardTitle className="text-lg line-clamp-1">{doc.title}</CardTitle>
                    </div>
                  </div>
                  <CardDescription className="line-clamp-2">
                    {doc.content}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">{getTypeName(doc.type)}</span>
                      <span className="text-muted-foreground">
                        {new Date(doc.created_at).toLocaleDateString('zh-CN')}
                      </span>
                    </div>
                    {doc.tags.length > 0 && (
                      <div className="flex gap-1 flex-wrap">
                        {doc.tags.map((tag) => (
                          <span
                            key={tag}
                            className="px-2 py-0.5 bg-secondary text-secondary-foreground rounded-full text-xs"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}

      {/* Tags */}
      {tags.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>热门标签</CardTitle>
            <CardDescription>快速浏览相关文档</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2 flex-wrap">
              {tags.map((tag) => (
                <span
                  key={tag}
                  className="px-3 py-1 bg-secondary text-secondary-foreground rounded-full text-sm cursor-pointer hover:bg-accent"
                >
                  #{tag}
                </span>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <DocumentUpload
        open={uploadOpen}
        onOpenChange={setUploadOpen}
        onUpload={handleUpload}
        existingCategories={categories}
        existingTags={tags}
      />
    </div>
  )
}

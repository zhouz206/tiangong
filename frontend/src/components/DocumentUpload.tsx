import { useState, useCallback, useRef } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Upload, File, X, CheckCircle, AlertCircle, FileText, Code, Link, Lightbulb } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { KnowledgeDocument } from '@/stores/knowledge-store'

export interface UploadFile {
  file: File
  id: string
  progress: number
  status: 'pending' | 'uploading' | 'success' | 'error'
  error?: string
}

interface DocumentUploadProps {
  open?: boolean
  onOpenChange?: (open: boolean) => void
  onUpload: (data: {
    title: string
    content: string
    type: KnowledgeDocument['type']
    tags: string[]
    category?: string
  }) => Promise<void>
  existingCategories?: string[]
  existingTags?: string[]
}

const typeOptions = [
  { value: 'project_doc', label: '项目文档', icon: FileText },
  { value: 'discussion', label: '讨论记录', icon: FileText },
  { value: 'reference', label: '参考资料', icon: Link },
  { value: 'experience', label: '经验总结', icon: Lightbulb },
  { value: 'code_snippet', label: '代码片段', icon: Code },
]

const getTypeIcon = (type: string) => {
  const option = typeOptions.find((o) => o.value === type)
  return option?.icon || File
}

export function DocumentUpload({
  open,
  onOpenChange,
  onUpload,
  existingCategories = [],
  existingTags = [],
}: DocumentUploadProps) {
  const [files, setFiles] = useState<UploadFile[]>([])
  const [currentDoc, setCurrentDoc] = useState<{
    title: string
    content: string
    type: KnowledgeDocument['type']
    tags: string[]
    category: string
  } | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [newTag, setNewTag] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = useCallback((selectedFiles: FileList | null) => {
    if (!selectedFiles) return

    const newFiles: UploadFile[] = Array.from(selectedFiles).map((file) => ({
      file,
      id: `${file.name}-${Date.now()}-${Math.random()}`,
      progress: 0,
      status: 'pending' as const,
    }))

    setFiles((prev) => [...prev, ...newFiles])
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    handleFileSelect(e.dataTransfer.files)
  }, [handleFileSelect])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id))
  }

  const handleUploadFile = async (uploadFile: UploadFile) => {
    setFiles((prev) =>
      prev.map((f) => (f.id === uploadFile.id ? { ...f, status: 'uploading' } : f))
    )

    try {
      // 模拟上传进度
      for (let i = 0; i <= 100; i += 10) {
        await new Promise((resolve) => setTimeout(resolve, 100))
        setFiles((prev) =>
          prev.map((f) =>
            f.id === uploadFile.id ? { ...f, progress: i } : f
          )
        )
      }

      // 读取文件内容
      const content = await readFileContent(uploadFile.file)

      setCurrentDoc({
        title: uploadFile.file.name.replace(/\.[^/.]+$/, ''),
        content,
        type: 'project_doc',
        tags: [],
        category: '',
      })
    } catch (error) {
      setFiles((prev) =>
        prev.map((f) =>
          f.id === uploadFile.id
            ? { ...f, status: 'error', error: '读取文件失败' }
            : f
        )
      )
    }
  }

  const readFileContent = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => resolve(e.target?.result as string)
      reader.onerror = reject
      reader.readAsText(file)
    })
  }

  const handleAddTag = () => {
    if (newTag && currentDoc && !currentDoc.tags.includes(newTag)) {
      setCurrentDoc({ ...currentDoc, tags: [...currentDoc.tags, newTag] })
      setNewTag('')
    }
  }

  const handleRemoveTag = (tag: string) => {
    if (currentDoc) {
      setCurrentDoc({ ...currentDoc, tags: currentDoc.tags.filter((t) => t !== tag) })
    }
  }

  const handleSubmit = async () => {
    if (!currentDoc) return

    setIsUploading(true)
    try {
      await onUpload(currentDoc)
      setFiles([])
      setCurrentDoc(null)
      onOpenChange?.(false)
    } catch (error) {
      console.error('Upload failed:', error)
    } finally {
      setIsUploading(false)
    }
  }

  const handleBatchUpload = async () => {
    const pendingFiles = files.filter((f) => f.status === 'pending' || f.status === 'error')
    for (const file of pendingFiles) {
      await handleUploadFile(file)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            上传文档
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Drop Zone */}
          <div
            className={cn(
              'border-2 border-dashed rounded-lg p-8 text-center transition-colors',
              'hover:border-primary hover:bg-primary/5 cursor-pointer'
            )}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              multiple
              accept=".txt,.md,.json,.js,.ts,.py,.java,.go,.rs"
              onChange={(e) => handleFileSelect(e.target.files)}
            />
            <Upload className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-sm font-medium">点击或拖拽文件到此处上传</p>
            <p className="text-xs text-muted-foreground mt-1">
              支持 .txt, .md, .json, .js, .ts, .py 等格式
            </p>
          </div>

          {/* File List */}
          {files.length > 0 && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>文件列表 ({files.length})</Label>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleBatchUpload}
                  disabled={isUploading}
                >
                  批量上传
                </Button>
              </div>

              <div className="space-y-2 max-h-48 overflow-y-auto">
                {files.map((uploadFile) => {
                  const Icon = getTypeIcon(uploadFile.file.type)
                  return (
                    <Card key={uploadFile.id}>
                      <CardContent className="p-3">
                        <div className="flex items-center gap-3">
                          <Icon className="h-5 w-5 text-muted-foreground" />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate">
                              {uploadFile.file.name}
                            </p>
                            {uploadFile.status !== 'pending' && (
                              <Progress value={uploadFile.progress} className="h-1 mt-1" />
                            )}
                          </div>
                          {uploadFile.status === 'success' && (
                            <CheckCircle className="h-5 w-5 text-green-500" />
                          )}
                          {uploadFile.status === 'error' && (
                            <AlertCircle className="h-5 w-5 text-red-500" />
                          )}
                          {uploadFile.status === 'pending' && (
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={() => handleUploadFile(uploadFile)}
                            >
                              上传
                            </Button>
                          )}
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => removeFile(uploadFile.id)}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  )
                })}
              </div>
            </div>
          )}

          {/* Document Form */}
          {currentDoc && (
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>文档信息</CardTitle>
                  <CardDescription>完善文档的元数据</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-2">
                    <Label htmlFor="doc-title">标题</Label>
                    <Input
                      id="doc-title"
                      value={currentDoc.title}
                      onChange={(e) =>
                        setCurrentDoc({ ...currentDoc, title: e.target.value })
                      }
                    />
                  </div>

                  <div className="grid gap-2">
                    <Label htmlFor="doc-type">类型</Label>
                    <Select
                      value={currentDoc.type}
                      onValueChange={(value: KnowledgeDocument['type']) =>
                        setCurrentDoc({ ...currentDoc, type: value })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {typeOptions.map((option) => {
                          const OptionIcon = option.icon
                          return (
                            <SelectItem key={option.value} value={option.value}>
                              <div className="flex items-center gap-2">
                                <OptionIcon className="h-4 w-4" />
                                {option.label}
                              </div>
                            </SelectItem>
                          )
                        })}
                      </SelectContent>
                    </Select>
                  </div>

                  {existingCategories.length > 0 && (
                    <div className="grid gap-2">
                      <Label htmlFor="doc-category">分类</Label>
                      <Select
                        value={currentDoc.category}
                        onValueChange={(value: string) =>
                          setCurrentDoc({ ...currentDoc, category: value })
                        }
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="选择分类" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="">无分类</SelectItem>
                          {existingCategories.map((cat) => (
                            <SelectItem key={cat} value={cat}>
                              {cat}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  )}

                  <div className="grid gap-2">
                    <Label htmlFor="doc-content">内容</Label>
                    <Textarea
                      id="doc-content"
                      value={currentDoc.content}
                      onChange={(e) =>
                        setCurrentDoc({ ...currentDoc, content: e.target.value })
                      }
                      rows={8}
                    />
                  </div>

                  <div className="grid gap-2">
                    <Label>标签</Label>
                    <div className="flex gap-2">
                      <Input
                        value={newTag}
                        onChange={(e) => setNewTag(e.target.value)}
                        placeholder="输入标签..."
                        onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
                      />
                      <Button type="button" onClick={handleAddTag}>
                        添加
                      </Button>
                    </div>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {currentDoc.tags.map((tag) => (
                        <Badge key={tag} variant="secondary">
                          #{tag}
                          <X
                            className="ml-1 h-3 w-3 cursor-pointer"
                            onClick={() => handleRemoveTag(tag)}
                          />
                        </Badge>
                      ))}
                      {existingTags
                        .filter((t) => !currentDoc.tags.includes(t))
                        .slice(0, 5)
                        .map((tag) => (
                          <Badge
                            key={tag}
                            variant="outline"
                            className="cursor-pointer"
                            onClick={() => handleAddTag()}
                          >
                            +{tag}
                          </Badge>
                        ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange?.(false)}>
            取消
          </Button>
          {currentDoc && (
            <Button onClick={handleSubmit} disabled={isUploading || !currentDoc.title.trim()}>
              确认上传
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

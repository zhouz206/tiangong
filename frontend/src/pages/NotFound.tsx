import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Home, ArrowLeft } from 'lucide-react'

export default function NotFound() {
  const navigate = useNavigate()

  return (
    <div className="min-h-[80vh] flex items-center justify-center p-4">
      <Card className="w-full max-w-md border-dashed">
        <CardContent className="flex flex-col items-center justify-center py-12">
          <div className="text-6xl font-bold text-muted-foreground mb-4">404</div>
          <h1 className="text-2xl font-semibold mb-2">页面未找到</h1>
          <p className="text-muted-foreground text-center mb-8">
            抱歉，您访问的页面不存在或已被移除。
          </p>
          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={() => navigate(-1)}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              返回上一页
            </Button>
            <Button onClick={() => navigate('/')}>
              <Home className="h-4 w-4 mr-2" />
              返回首页
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

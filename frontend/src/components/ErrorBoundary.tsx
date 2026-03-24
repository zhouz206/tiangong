import { Component, ErrorInfo, ReactNode } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { AlertTriangle, RefreshCw, FileText } from 'lucide-react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    this.props.onError?.(error, errorInfo)
  }

  private handleRetry = () => {
    this.setState({ hasError: false, error: undefined })
    window.location.reload()
  }

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="min-h-[400px] flex items-center justify-center p-4">
          <Card className="max-w-md w-full border-destructive/50">
            <CardHeader>
              <div className="flex items-center gap-3">
                <AlertTriangle className="h-6 w-6 text-destructive" />
                <CardTitle>出错了</CardTitle>
              </div>
              <CardDescription>
                {this.state.error?.message || '发生未知错误'}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-sm text-muted-foreground bg-muted p-3 rounded-md overflow-auto max-h-32">
                <div className="flex items-start gap-2">
                  <FileText className="h-4 w-4 mt-0.5 flex-shrink-0" />
                  <pre className="text-xs">
                    {this.state.error?.stack || '无堆栈信息'}
                  </pre>
                </div>
              </div>
              <div className="flex gap-2">
                <Button onClick={this.handleRetry} className="flex-1">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  重新加载
                </Button>
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => window.history.back()}
                >
                  返回
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary

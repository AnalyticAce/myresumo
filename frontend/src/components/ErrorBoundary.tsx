import { useRouteError, isRouteErrorResponse, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertCircle, Home, RefreshCw } from 'lucide-react'

export function ErrorBoundary() {
  const error = useRouteError()
  const navigate = useNavigate()

  let title = 'Something went wrong'
  let message = 'An unexpected error occurred. Please try again.'

  if (isRouteErrorResponse(error)) {
    if (error.status === 404) {
      title = 'Page not found'
      message = 'The page you are looking for does not exist.'
    } else if (error.status === 500) {
      title = 'Server error'
      message = 'There was a problem with the server. Please try again later.'
    } else {
      title = `Error ${error.status}`
      message = error.statusText || message
    }
  } else if (error instanceof Error) {
    message = error.message
  }

  return (
    <div className="min-h-[60vh] flex items-center justify-center p-4">
      <Card className="max-w-md w-full">
        <CardHeader className="text-center">
          <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground text-center">{message}</p>
          <div className="flex gap-2 justify-center">
            <Button variant="outline" onClick={() => globalThis.location.reload()}>
              <RefreshCw className="mr-2 h-4 w-4" />
              Retry
            </Button>
            <Button onClick={() => navigate('/')}>
              <Home className="mr-2 h-4 w-4" />
              Go Home
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}


import { MasterCV } from '@/types/resume'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Download, Trash2, Eye, TrendingUp } from 'lucide-react'
import { formatDateTime } from '@/utils/formatters'
import { useDownloadMasterCV, useDeleteMasterCV } from '@/hooks/useMasterCV'

interface MasterCVCardProps {
  masterCV: MasterCV
  className?: string
  onPreview?: (masterCV: MasterCV) => void
}

export function MasterCVCard({ masterCV, className = '', onPreview }: MasterCVCardProps) {
  const downloadMasterCV = useDownloadMasterCV()
  const deleteMasterCV = useDeleteMasterCV()

  const handleDownload = (): void => {
    downloadMasterCV.mutate(masterCV.id)
  }

  const handleDelete = (): void => {
    if (window.confirm('Are you sure you want to delete this Master CV?')) {
      deleteMasterCV.mutate(masterCV.id)
    }
  }

  const handlePreview = (): void => {
    if (onPreview) {
      onPreview(masterCV)
    }
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="space-y-2">
          <CardTitle className="text-lg">{masterCV.originalFilename}</CardTitle>
          <div className="flex items-center gap-2">
            <Badge variant="secondary">Master CV</Badge>
            <Badge variant="outline">
              Used {masterCV.usageCount} times
            </Badge>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="space-y-2 text-sm">
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Uploaded:</span>
            <span>{formatDateTime(masterCV.uploadedAt)}</span>
          </div>
          
          {masterCV.lastUsed && (
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Last Used:</span>
              <span>{formatDateTime(masterCV.lastUsed)}</span>
            </div>
          )}
          
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Usage:</span>
            <div className="flex items-center gap-1">
              <TrendingUp className="h-3 w-3" />
              <span>{masterCV.usageCount} times</span>
            </div>
          </div>
        </div>

        <div className="flex gap-2 pt-2">
          <Button
            size="sm"
            variant="outline"
            onClick={handlePreview}
            className="flex-1"
          >
            <Eye className="mr-2 h-4 w-4" />
            Preview
          </Button>
          
          <Button
            size="sm"
            variant="outline"
            onClick={handleDownload}
            disabled={downloadMasterCV.isPending}
          >
            <Download className="h-4 w-4" />
          </Button>
          
          <Button
            size="sm"
            variant="ghost"
            onClick={handleDelete}
            disabled={deleteMasterCV.isPending}
          >
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

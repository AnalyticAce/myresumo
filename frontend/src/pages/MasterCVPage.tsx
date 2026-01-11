import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { MasterCVCard } from '@/components/master-cv/MasterCVCard'
import { Plus, Search, Upload, FileText, LayoutGrid, List, Eye, Download, Trash2 } from 'lucide-react'
import { MasterCV } from '@/types/resume'
import { apiClient } from '@/api/client'
import { toast } from 'sonner'
import { formatDateTime } from '@/utils/formatters'
import { useDownloadMasterCV, useDeleteMasterCV } from '@/hooks/useMasterCV'

interface MasterCVFromAPI {
  id: string
  title: string
  master_filename?: string
  master_file_type?: string
  master_updated_at?: string
  master_content?: string
}

// Store raw API data alongside transformed data for preview
interface MasterCVWithContent extends MasterCV {
  content?: string
}

export function MasterCVPage() {
  const [search, setSearch] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [viewMode, setViewMode] = useState<'card' | 'table'>('card')
  const [previewCV, setPreviewCV] = useState<MasterCVWithContent | null>(null)
  const queryClient = useQueryClient()
  const downloadMasterCV = useDownloadMasterCV()
  const deleteMasterCV = useDeleteMasterCV()

  // Fetch master CVs from API
  const { data: masterCVsData, isLoading, error } = useQuery({
    queryKey: ['master-cvs'],
    queryFn: async () => {
      const { data } = await apiClient.get<MasterCVFromAPI[]>('/resume/master-cvs')
      return data
    },
  })

  // Transform API data to frontend format
  const masterCVs: MasterCVWithContent[] = (masterCVsData || []).map((cv) => ({
    id: cv.id,
    userId: 'local-user',
    filename: cv.master_filename || cv.title,
    originalFilename: cv.master_filename || cv.title,
    fileUrl: `/api/resume/master-cv/${cv.id}`,
    uploadedAt: cv.master_updated_at || new Date().toISOString(),
    usageCount: 0,
    lastUsed: cv.master_updated_at,
    content: cv.master_content,
  }))

  const filteredCVs = masterCVs.filter(cv =>
    cv.originalFilename.toLowerCase().includes(search.toLowerCase())
  )

  const handlePreview = async (cv: MasterCV) => {
    // Fetch full content for preview
    try {
      const { data } = await apiClient.get<MasterCVFromAPI>(`/resume/master-cv/${cv.id}`)
      setPreviewCV({
        ...cv,
        content: data.master_content,
      })
    } catch {
      toast.error('Failed to load preview')
    }
  }

  const handleTableDelete = (id: string) => {
    if (globalThis.confirm('Are you sure you want to delete this Master CV?')) {
      deleteMasterCV.mutate(id)
    }
  }

  const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setIsUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('title', file.name.replace(/\.[^/.]+$/, ''))
      formData.append('user_id', 'local-user')

      await apiClient.post('/resume/master-cv', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })

      toast.success('Master CV uploaded successfully')
      queryClient.invalidateQueries({ queryKey: ['master-cvs'] })
    } catch (err) {
      console.error('Upload failed:', err)
      toast.error('Failed to upload Master CV')
    } finally {
      setIsUploading(false)
      // Reset input
      event.target.value = ''
    }
  }

  const handleCreateNew = () => {
    document.getElementById('file-upload')?.click()
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-destructive">Error loading Master CVs. Please try again.</p>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Master CVs</h1>
          <p className="text-muted-foreground">Manage your master resumes for optimization</p>
        </div>
        <Button onClick={handleCreateNew} disabled={isUploading}>
          <Plus className="mr-2 h-4 w-4" />
          {isUploading ? 'Uploading...' : 'Upload Master CV'}
        </Button>
      </div>

      <input
        id="file-upload"
        type="file"
        accept=".pdf,.docx,.doc,.md,.markdown,.txt"
        onChange={handleUpload}
        className="hidden"
      />

      <div className="flex gap-4 flex-wrap items-center">
        <div className="relative flex-1 min-w-[300px]">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search Master CVs..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="flex gap-2">
          <Button
            variant={viewMode === 'card' ? 'default' : 'outline'}
            size="icon"
            onClick={() => setViewMode('card')}
            title="Card view"
          >
            <LayoutGrid className="h-4 w-4" />
          </Button>
          <Button
            variant={viewMode === 'table' ? 'default' : 'outline'}
            size="icon"
            onClick={() => setViewMode('table')}
            title="Table view"
          >
            <List className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-muted rounded w-3/4" />
                <div className="h-3 bg-muted rounded w-1/2" />
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="h-3 bg-muted rounded" />
                  <div className="h-3 bg-muted rounded" />
                  <div className="h-3 bg-muted rounded w-2/3" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : filteredCVs.length === 0 ? (
        <Card className="text-center py-12">
          <CardContent>
            <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Master CVs Found</h3>
            <p className="text-muted-foreground mb-4">
              {search ? 'Try adjusting your search terms' : 'Upload your first Master CV to get started'}
            </p>
            <Button onClick={handleCreateNew}>
              <Upload className="mr-2 h-4 w-4" />
              Upload Master CV
            </Button>
          </CardContent>
        </Card>
      ) : (
        <>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <span>{filteredCVs.length} Master CV{filteredCVs.length === 1 ? '' : 's'}</span>
            {search && <span>filtered by "{search}"</span>}
          </div>

          {viewMode === 'card' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredCVs.map((cv) => (
                <MasterCVCard key={cv.id} masterCV={cv} onPreview={handlePreview} />
              ))}
            </div>
          ) : (
            <div className="border rounded-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-muted">
                  <tr>
                    <th className="text-left p-3 font-medium">Name</th>
                    <th className="text-left p-3 font-medium">Uploaded</th>
                    <th className="text-left p-3 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredCVs.map((cv) => (
                    <tr key={cv.id} className="border-t hover:bg-muted/50">
                      <td className="p-3">{cv.originalFilename}</td>
                      <td className="p-3 text-muted-foreground text-sm">
                        {formatDateTime(cv.uploadedAt)}
                      </td>
                      <td className="p-3">
                        <div className="flex gap-2">
                          <Button variant="ghost" size="sm" onClick={() => handlePreview(cv)}>
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm" onClick={() => downloadMasterCV.mutate(cv.id)}>
                            <Download className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm" onClick={() => handleTableDelete(cv.id)}>
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {/* Preview Dialog */}
      <Dialog open={!!previewCV} onOpenChange={(open) => !open && setPreviewCV(null)}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle>{previewCV?.originalFilename}</DialogTitle>
          </DialogHeader>
          <div className="flex-1 overflow-auto">
            <pre className="whitespace-pre-wrap text-sm font-mono bg-muted p-4 rounded">
              {previewCV?.content || 'Loading...'}
            </pre>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}

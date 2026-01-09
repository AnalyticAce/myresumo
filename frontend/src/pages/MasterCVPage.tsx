import { useState } from 'react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { MasterCVCard } from '@/components/master-cv/MasterCVCard'
import { Plus, Search, Upload, FileText } from 'lucide-react'
import { MasterCV } from '@/types/resume'

// Mock data for now
const mockMasterCVs: MasterCV[] = [
  {
    id: '1',
    userId: 'user1',
    filename: 'master_cv_2024.pdf',
    originalFilename: 'My Master CV 2024.pdf',
    fileUrl: '/api/master-cvs/1/download',
    uploadedAt: '2024-01-15T10:30:00Z',
    usageCount: 12,
    lastUsed: '2024-01-20T14:20:00Z'
  },
  {
    id: '2',
    userId: 'user1',
    filename: 'technical_resume.pdf',
    originalFilename: 'Technical Resume.pdf',
    fileUrl: '/api/master-cvs/2/download',
    uploadedAt: '2024-01-10T09:15:00Z',
    usageCount: 8,
    lastUsed: '2024-01-18T16:45:00Z'
  },
  {
    id: '3',
    userId: 'user1',
    filename: 'management_resume.pdf',
    originalFilename: 'Management Resume.pdf',
    fileUrl: '/api/master-cvs/3/download',
    uploadedAt: '2023-12-20T11:30:00Z',
    usageCount: 5,
    lastUsed: '2024-01-12T10:00:00Z'
  }
]

export function MasterCVPage() {
  const [search, setSearch] = useState('')
  const [isUploading, setIsUploading] = useState(false)

  // const { data: masterCVs, isLoading } = useQuery({
  //   queryKey: ['master-cvs'],
  //   queryFn: () => masterCVAPI.getAll(),
  // })

  const masterCVs = mockMasterCVs // Using mock data for now
  const isLoading = false

  const filteredCVs = masterCVs.filter(cv =>
    cv.originalFilename.toLowerCase().includes(search.toLowerCase())
  )

  const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setIsUploading(true)
    try {
      // TODO: Implement actual upload
      // await masterCVAPI.upload(file)
      await new Promise(resolve => setTimeout(resolve, 2000)) // Simulate upload
      // Refresh data
    } catch (error) {
      console.error('Upload failed:', error)
    } finally {
      setIsUploading(false)
    }
  }

  const handleCreateNew = () => {
    document.getElementById('file-upload')?.click()
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
        accept=".pdf,.docx,.doc"
        onChange={handleUpload}
        className="hidden"
      />

      <div className="flex gap-4 flex-wrap">
        <div className="relative flex-1 min-w-[300px]">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search Master CVs..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
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
            <span>{filteredCVs.length} Master CV{filteredCVs.length !== 1 ? 's' : ''}</span>
            {search && <span>filtered by "{search}"</span>}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCVs.map((cv) => (
              <MasterCVCard key={cv.id} masterCV={cv} />
            ))}
          </div>
        </>
      )}
    </div>
  )
}

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Plus, Search, Mail, FileText, Download } from 'lucide-react'

// Mock cover letter data
const mockCoverLetters = [
  {
    id: '1',
    resumeId: 'res_1',
    company: 'Google',
    position: 'Senior Software Engineer',
    createdAt: '2024-01-15T10:30:00Z',
    downloadUrl: '/api/cover-letters/1/download'
  },
  {
    id: '2',
    resumeId: 'res_2',
    company: 'Microsoft',
    position: 'Frontend Developer',
    createdAt: '2024-01-10T14:20:00Z',
    downloadUrl: '/api/cover-letters/2/download'
  },
  {
    id: '3',
    resumeId: 'res_3',
    company: 'Amazon',
    position: 'Full Stack Developer',
    createdAt: '2024-01-08T09:15:00Z',
    downloadUrl: '/api/cover-letters/3/download'
  }
]

export function CoverLetterPage() {
  const [search, setSearch] = useState('')
  const coverLetters = mockCoverLetters // Using mock data for now

  const filteredLetters = coverLetters.filter(letter =>
    letter.company.toLowerCase().includes(search.toLowerCase()) ||
    letter.position.toLowerCase().includes(search.toLowerCase())
  )

  const handleDownload = async (coverLetter: typeof mockCoverLetters[0]) => {
    try {
      // TODO: Implement actual download
      const response = await fetch(coverLetter.downloadUrl)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${coverLetter.company}_CoverLetter.pdf`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Download failed:', error)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Cover Letters</h1>
          <p className="text-muted-foreground">Manage your generated cover letters</p>
        </div>
        <Button onClick={() => window.location.href = '/optimize'}>
          <Plus className="mr-2 h-4 w-4" />
          Generate New
        </Button>
      </div>

      <div className="flex gap-4 flex-wrap">
        <div className="relative flex-1 min-w-[300px]">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by company or position..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {filteredLetters.length === 0 ? (
        <Card className="text-center py-12">
          <CardContent>
            <Mail className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Cover Letters Found</h3>
            <p className="text-muted-foreground mb-4">
              {search ? 'Try adjusting your search terms' : 'Generate your first cover letter to get started'}
            </p>
            <Button onClick={() => window.location.href = '/optimize'}>
              <FileText className="mr-2 h-4 w-4" />
              Generate Cover Letter
            </Button>
          </CardContent>
        </Card>
      ) : (
        <>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <span>{filteredLetters.length} Cover Letter{filteredLetters.length !== 1 ? 's' : ''}</span>
            {search && <span>filtered by "{search}"</span>}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredLetters.map((letter) => (
              <Card key={letter.id}>
                <CardHeader>
                  <div className="space-y-1">
                    <h3 className="font-semibold text-lg">{letter.position}</h3>
                    <p className="text-sm text-muted-foreground">{letter.company}</p>
                  </div>
                </CardHeader>

                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Generated:</span>
                    <span className="font-medium">{formatDate(letter.createdAt)}</span>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Type:</span>
                    <Badge variant="secondary">AI Generated</Badge>
                  </div>

                  <Button
                    onClick={() => handleDownload(letter)}
                    className="w-full"
                    variant="outline"
                  >
                    <Download className="mr-2 h-4 w-4" />
                    Download Cover Letter
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </>
      )}
    </div>
  )
}

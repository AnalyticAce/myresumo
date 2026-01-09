import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ResumeCard } from '@/components/dashboard/ResumeCard'
import { Plus, Search } from 'lucide-react'
import { ResumeStatus, ResumeFormat, TemplateType } from '@/types'

// Mock data for now
const mockResumes = [
  {
    id: '1',
    userId: 'user1',
    company: 'Google',
    position: 'Senior Software Engineer',
    status: ResumeStatus.APPLIED,
    atsScore: 85,
    format: ResumeFormat.PDF,
    sourceType: 'master_cv' as const,
    sourceName: 'My Master CV 2024',
    template: TemplateType.MODERN,
    hasCoverLetter: true,
    createdAt: '2024-01-15T10:30:00Z',
    updatedAt: '2024-01-15T10:30:00Z',
  },
  {
    id: '2',
    userId: 'user1',
    company: 'Microsoft',
    position: 'Frontend Developer',
    status: ResumeStatus.INTERVIEW,
    atsScore: 92,
    format: ResumeFormat.DOCX,
    sourceType: 'upload' as const,
    sourceName: 'resume_upload.pdf',
    template: TemplateType.PROFESSIONAL,
    hasCoverLetter: false,
    createdAt: '2024-01-10T14:20:00Z',
    updatedAt: '2024-01-12T09:15:00Z',
  },
]

export function DashboardPage() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')

  const filteredResumes = mockResumes.filter(resume => 
    resume.company.toLowerCase().includes(search.toLowerCase()) ||
    resume.position.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Resume Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Manage your optimized resumes and track applications
          </p>
        </div>
        <Button onClick={() => navigate('/optimize')}>
          <Plus className="mr-2 h-4 w-4" />
          New Resume
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

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filteredResumes.map((resume) => (
          <ResumeCard key={resume.id} resume={resume} />
        ))}
      </div>

      {filteredResumes.length === 0 && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No resumes found</p>
        </div>
      )}
    </div>
  )
}

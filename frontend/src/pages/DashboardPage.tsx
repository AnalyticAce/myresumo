import { useState, useMemo, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { ResumeCard } from '@/components/dashboard/ResumeCard'
import { Plus, Search, Loader2, FileText, LayoutGrid, List, ArrowUpDown } from 'lucide-react'
import { ResumeStatus, ResumeFormat, TemplateType } from '@/types'
import { Resume } from '@/types/resume'
import { apiClient } from '@/api/client'
import { toast } from 'sonner'

interface ResumeFromAPI {
  id: string
  title: string
  matching_score?: number | null
  application_status?: string
  target_company?: string
  target_role?: string
  main_job_title?: string
  skills_preview?: string[]
  created_at: string
  updated_at: string
}

type SortField = 'company' | 'position' | 'date' | 'status' | 'score'
type SortDirection = 'asc' | 'desc'
type ViewMode = 'card' | 'table'

// Map API status to frontend enum
function mapStatus(apiStatus?: string): ResumeStatus {
  switch (apiStatus) {
    case 'applied': return ResumeStatus.APPLIED
    case 'interview': return ResumeStatus.INTERVIEW
    case 'answered': return ResumeStatus.ANSWERED
    case 'rejected': return ResumeStatus.REJECTED
    default: return ResumeStatus.NOT_APPLIED
  }
}

// Map frontend enum to API status
function mapStatusToAPI(status: ResumeStatus): string {
  switch (status) {
    case ResumeStatus.APPLIED: return 'applied'
    case ResumeStatus.INTERVIEW: return 'interview'
    case ResumeStatus.ANSWERED: return 'answered'
    case ResumeStatus.REJECTED: return 'rejected'
    default: return 'not_applied'
  }
}

export function DashboardPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [viewMode, setViewMode] = useState<ViewMode>(() => {
    const saved = localStorage.getItem('dashboard-view-mode')
    return (saved === 'card' || saved === 'table') ? saved : 'card'
  })
  const [sortField, setSortField] = useState<SortField>(() => {
    const saved = localStorage.getItem('dashboard-sort-field')
    return (saved as SortField) || 'date'
  })
  const [sortDirection, setSortDirection] = useState<SortDirection>(() => {
    const saved = localStorage.getItem('dashboard-sort-direction')
    return (saved === 'asc' || saved === 'desc') ? saved : 'desc'
  })

  // Persist preferences to localStorage
  useEffect(() => {
    localStorage.setItem('dashboard-view-mode', viewMode)
  }, [viewMode])

  useEffect(() => {
    localStorage.setItem('dashboard-sort-field', sortField)
  }, [sortField])

  useEffect(() => {
    localStorage.setItem('dashboard-sort-direction', sortDirection)
  }, [sortDirection])

  // Fetch resumes from API
  const { data: resumesData, isLoading, error } = useQuery({
    queryKey: ['resumes', 'local-user'],
    queryFn: async () => {
      const { data } = await apiClient.get<ResumeFromAPI[]>('/resume/user/local-user')
      return data
    },
  })

  // Status update mutation
  const updateStatus = useMutation({
    mutationFn: async ({ id, status }: { id: string; status: string }) => {
      await apiClient.patch(`/resume/${id}/status`, { application_status: status })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes'] })
      toast.success('Status updated successfully')
    },
    onError: () => {
      toast.error('Failed to update status')
    },
  })

  // Transform API data to frontend format
  const resumes: Resume[] = (resumesData || []).map((r) => ({
    id: r.id,
    userId: 'local-user',
    title: r.title,
    company: r.target_company || 'Unknown Company',
    position: r.target_role || r.main_job_title || r.title || 'Unknown Position',
    status: mapStatus(r.application_status),
    atsScore: r.matching_score || 0,
    isOptimized: r.matching_score != null && r.matching_score > 0,
    format: ResumeFormat.PDF,
    sourceType: 'master_cv' as const,
    sourceName: r.title,
    template: TemplateType.MODERN,
    hasCoverLetter: false,
    createdAt: r.created_at,
    updatedAt: r.updated_at,
  }))

  // Filter and sort resumes
  const filteredAndSortedResumes = useMemo(() => {
    let result = resumes.filter(resume =>
      (resume.company ?? '').toLowerCase().includes(search.toLowerCase()) ||
      (resume.position ?? '').toLowerCase().includes(search.toLowerCase())
    )

    // Sort
    result.sort((a, b) => {
      let comparison = 0
      switch (sortField) {
        case 'company':
          comparison = (a.company ?? '').localeCompare(b.company ?? '')
          break
        case 'position':
          comparison = (a.position ?? '').localeCompare(b.position ?? '')
          break
        case 'date':
          comparison = new Date(a.createdAt ?? 0).getTime() - new Date(b.createdAt ?? 0).getTime()
          break
        case 'status':
          comparison = a.status.localeCompare(b.status)
          break
        case 'score':
          comparison = (a.atsScore ?? 0) - (b.atsScore ?? 0)
          break
      }
      return sortDirection === 'asc' ? comparison : -comparison
    })

    return result
  }, [resumes, search, sortField, sortDirection])

  const handleStatusChange = (resumeId: string, newStatus: ResumeStatus) => {
    updateStatus.mutate({ id: resumeId, status: mapStatusToAPI(newStatus) })
  }

  const toggleSortDirection = () => {
    setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc')
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <span className="ml-2 text-muted-foreground">Loading resumes...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-destructive">Error loading resumes. Please try again.</p>
      </div>
    )
  }

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

      <div className="flex gap-4 flex-wrap items-center">
        <div className="relative flex-1 min-w-[300px]">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by company or position..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Sort controls */}
        <div className="flex items-center gap-2">
          <Select value={sortField} onValueChange={(v) => setSortField(v as SortField)}>
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="date">Date</SelectItem>
              <SelectItem value="company">Company</SelectItem>
              <SelectItem value="position">Position</SelectItem>
              <SelectItem value="status">Status</SelectItem>
              <SelectItem value="score">ATS Score</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" size="icon" onClick={toggleSortDirection} title={sortDirection === 'asc' ? 'Ascending' : 'Descending'}>
            <ArrowUpDown className={`h-4 w-4 ${sortDirection === 'desc' ? 'rotate-180' : ''}`} />
          </Button>
        </div>

        {/* View toggle */}
        <div className="flex border rounded-md">
          <Button
            variant={viewMode === 'card' ? 'default' : 'ghost'}
            size="icon"
            onClick={() => setViewMode('card')}
            className="rounded-r-none"
            title="Card view"
          >
            <LayoutGrid className="h-4 w-4" />
          </Button>
          <Button
            variant={viewMode === 'table' ? 'default' : 'ghost'}
            size="icon"
            onClick={() => setViewMode('table')}
            className="rounded-l-none"
            title="Table view"
          >
            <List className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {filteredAndSortedResumes.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">No Resumes Yet</h3>
          <p className="text-muted-foreground mb-4">
            Create your first optimized resume to get started
          </p>
          <Button onClick={() => navigate('/optimize')}>
            <Plus className="mr-2 h-4 w-4" />
            Create Resume
          </Button>
        </div>
      ) : viewMode === 'card' ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredAndSortedResumes.map((resume) => (
            <ResumeCard key={resume.id} resume={resume} onStatusChange={handleStatusChange} />
          ))}
        </div>
      ) : (
        <div className="border rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-muted">
              <tr>
                <th className="text-left p-3 font-medium">Company</th>
                <th className="text-left p-3 font-medium">Position</th>
                <th className="text-left p-3 font-medium">Status</th>
                <th className="text-left p-3 font-medium">ATS Score</th>
                <th className="text-left p-3 font-medium">Created</th>
                <th className="text-left p-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredAndSortedResumes.map((resume) => (
                <tr key={resume.id} className="border-t hover:bg-muted/50">
                  <td className="p-3">{resume.company}</td>
                  <td className="p-3">{resume.position}</td>
                  <td className="p-3">
                    <Select
                      value={resume.status}
                      onValueChange={(v) => handleStatusChange(resume.id, v as ResumeStatus)}
                    >
                      <SelectTrigger className="w-[130px] h-8">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value={ResumeStatus.NOT_APPLIED}>Not Applied</SelectItem>
                        <SelectItem value={ResumeStatus.APPLIED}>Applied</SelectItem>
                        <SelectItem value={ResumeStatus.ANSWERED}>Answered</SelectItem>
                        <SelectItem value={ResumeStatus.INTERVIEW}>Interview</SelectItem>
                        <SelectItem value={ResumeStatus.REJECTED}>Rejected</SelectItem>
                      </SelectContent>
                    </Select>
                  </td>
                  <td className="p-3">
                    {resume.isOptimized && resume.atsScore !== undefined ? (
                      <span className={(resume.atsScore ?? 0) >= 70 ? 'text-green-600' : (resume.atsScore ?? 0) >= 50 ? 'text-yellow-600' : 'text-red-600'}>
                        {resume.atsScore}%
                      </span>
                    ) : (
                      <span className="text-muted-foreground">—</span>
                    )}
                  </td>
                  <td className="p-3 text-muted-foreground text-sm">
                    {resume.createdAt ? new Date(resume.createdAt).toLocaleDateString() : 'N/A'}
                  </td>
                  <td className="p-3">
                    <Button variant="ghost" size="sm" onClick={() => navigate(`/resume/${resume.id}`)}>
                      View
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

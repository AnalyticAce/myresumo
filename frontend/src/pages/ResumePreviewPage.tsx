import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { ArrowLeft, Download, Loader2 } from 'lucide-react'
import { apiClient } from '@/api/client'
import ReactMarkdown from 'react-markdown'

interface ResumeData {
  id: string
  title: string
  optimized_content?: string
  original_content?: string
  target_company?: string
  target_role?: string
  matching_score?: number
}

export function ResumePreviewPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const { data: resume, isLoading, error } = useQuery({
    queryKey: ['resume', id],
    queryFn: async () => {
      const { data } = await apiClient.get<ResumeData>(`/resume/${id}`)
      return data
    },
    enabled: !!id,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error || !resume) {
    return (
      <div className="max-w-4xl mx-auto py-8">
        <Button variant="ghost" onClick={() => navigate(-1)} className="mb-4">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>
        <div className="text-center py-12">
          <p className="text-destructive">Resume not found or failed to load.</p>
        </div>
      </div>
    )
  }

  const content = resume.optimized_content || resume.original_content || 'No content available'

  return (
    <div className="max-w-4xl mx-auto py-8">
      <div className="flex items-center justify-between mb-6">
        <Button variant="ghost" onClick={() => navigate(-1)}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Dashboard
        </Button>
        <Button variant="outline">
          <Download className="mr-2 h-4 w-4" />
          Download PDF
        </Button>
      </div>

      <div className="mb-4">
        <h1 className="text-2xl font-bold">{resume.title}</h1>
        {resume.target_company && resume.target_role && (
          <p className="text-muted-foreground">
            {resume.target_role} at {resume.target_company}
          </p>
        )}
        {resume.matching_score != null && (
          <p className="text-sm text-muted-foreground mt-1">
            ATS Score: <span className="font-semibold">{resume.matching_score}%</span>
          </p>
        )}
      </div>

      <div className="bg-white border rounded-lg p-8 shadow-sm print:shadow-none print:border-none">
        <div className="prose prose-slate max-w-none text-gray-900">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
      </div>
    </div>
  )
}


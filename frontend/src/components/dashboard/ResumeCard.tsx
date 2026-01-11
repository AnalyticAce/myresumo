import { Resume } from '@/types/resume'
import { ResumeStatus } from '@/types/enums'
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { StatusBadge } from './StatusBadge'
import { FileDown, Mail, Trash2, Sparkles } from 'lucide-react'
import { format } from 'date-fns'
import { useDownloadResume, useDownloadOriginalResume, useDownloadCoverLetter, useDeleteResume } from '@/hooks/useResumes'

interface ResumeCardProps {
  resume: Resume
  onStatusChange?: (resumeId: string, status: ResumeStatus) => void
}

export function ResumeCard({ resume, onStatusChange }: ResumeCardProps) {
  const downloadOptimized = useDownloadResume()
  const downloadOriginal = useDownloadOriginalResume()
  const downloadCoverLetter = useDownloadCoverLetter()
  const deleteResume = useDeleteResume()

  const handleDownloadOptimized = () => {
    downloadOptimized.mutate(resume.id)
  }

  const handleDownloadOriginal = () => {
    downloadOriginal.mutate(resume.id)
  }

  const handleDownloadCoverLetter = () => {
    if (resume.hasCoverLetter) {
      downloadCoverLetter.mutate(resume.id)
    }
  }

  const handleDelete = () => {
    if (globalThis.confirm('Are you sure you want to delete this resume?')) {
      deleteResume.mutate(resume.id)
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <h3 className="font-semibold text-lg">{resume.position}</h3>
            <p className="text-sm text-muted-foreground">{resume.company}</p>
          </div>
          {onStatusChange ? (
            <Select
              value={resume.status}
              onValueChange={(v) => onStatusChange(resume.id, v as ResumeStatus)}
            >
              <SelectTrigger className="w-[120px] h-7 text-xs">
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
          ) : (
            <StatusBadge status={resume.status} />
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">ATS Score:</span>
          <span className="font-semibold">
            {resume.isOptimized ? `${resume.atsScore}%` : 'Not optimized'}
          </span>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Source:</span>
          <span className="font-medium truncate ml-2">{resume.sourceName}</span>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Format:</span>
          <span className="uppercase">{resume.format}</span>
        </div>

        <div className="flex items-center gap-1 text-sm text-muted-foreground">
          Created {resume.createdAt ? format(new Date(resume.createdAt), 'MMM d, yyyy') : 'N/A'}
        </div>
      </CardContent>

      <CardFooter className="flex flex-col gap-2">
        <div className="flex gap-2 w-full">
          <Button
            size="sm"
            variant="outline"
            className="flex-1"
            onClick={handleDownloadOriginal}
            disabled={downloadOriginal.isPending}
            title="Download original uploaded file"
          >
            <FileDown className="mr-1 h-4 w-4" />
            Original
          </Button>

          <Button
            size="sm"
            variant={resume.isOptimized ? "default" : "outline"}
            className="flex-1"
            onClick={handleDownloadOptimized}
            disabled={!resume.isOptimized || downloadOptimized.isPending}
            title={resume.isOptimized ? 'Download optimized resume as PDF' : 'Resume must be optimized first'}
          >
            <Sparkles className="mr-1 h-4 w-4" />
            {resume.isOptimized ? 'Optimized' : 'Not ready'}
          </Button>
        </div>

        <div className="flex gap-2 w-full">
          <Button
            size="sm"
            variant="outline"
            className="flex-1"
            onClick={handleDownloadCoverLetter}
            disabled={!resume.hasCoverLetter || downloadCoverLetter.isPending}
          >
            <Mail className="mr-1 h-4 w-4" />
            Cover Letter
          </Button>

          <Button
            size="sm"
            variant="ghost"
            onClick={handleDelete}
            disabled={deleteResume.isPending}
            aria-label="Delete resume"
            className="text-destructive hover:text-destructive"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </CardFooter>
    </Card>
  )
}

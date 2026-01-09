import { Resume } from '@/types/resume'
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { StatusBadge } from './StatusBadge'
import { Download, Mail, Trash2 } from 'lucide-react'
import { format } from 'date-fns'
import { useDownloadResume, useDownloadCoverLetter, useDeleteResume } from '@/hooks/useResumes'

interface ResumeCardProps {
  resume: Resume
}

export function ResumeCard({ resume }: ResumeCardProps) {
  const downloadResume = useDownloadResume()
  const downloadCoverLetter = useDownloadCoverLetter()
  const deleteResume = useDeleteResume()

  const handleDownload = () => {
    downloadResume.mutate(resume.id)
  }

  const handleDownloadCoverLetter = () => {
    if (resume.hasCoverLetter) {
      downloadCoverLetter.mutate(resume.id)
    }
  }

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this resume?')) {
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
          <StatusBadge status={resume.status} />
        </div>
      </CardHeader>

      <CardContent className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">ATS Score:</span>
          <span className="font-semibold">{resume.atsScore}%</span>
        </div>
        
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Source:</span>
          <span className="font-medium truncate ml-2">{resume.sourceName}</span>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Format:</span>
          <span className="uppercase">{resume.format}</span>
        </div>

        <div className="text-xs text-muted-foreground">
          Created {format(new Date(resume.createdAt), 'MMM d, yyyy')}
        </div>
      </CardContent>

      <CardFooter className="flex gap-2">
        <Button
          size="sm"
          variant="outline"
          className="flex-1"
          onClick={handleDownload}
          disabled={downloadResume.isPending}
        >
          <Download className="mr-2 h-4 w-4" />
          Resume
        </Button>

        <Button
          size="sm"
          variant="outline"
          onClick={handleDownloadCoverLetter}
          disabled={!resume.hasCoverLetter || downloadCoverLetter.isPending}
          className={resume.hasCoverLetter ? '' : 'opacity-50 cursor-not-allowed'}
        >
          <Mail className="h-4 w-4" />
        </Button>

        <Button
          size="sm"
          variant="ghost"
          onClick={handleDelete}
          disabled={deleteResume.isPending}
          aria-label="Delete resume"
        >
          <Trash2 className="h-4 w-4 text-destructive" />
        </Button>
      </CardFooter>
    </Card>
  )
}

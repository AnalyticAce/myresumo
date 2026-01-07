import { Resume } from '@/types/resume'
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { StatusBadge } from './StatusBadge'
import { Download, Mail, Trash2 } from 'lucide-react'
import { format } from 'date-fns'

interface ResumeCardProps {
  resume: Resume
}

export function ResumeCard({ resume }: ResumeCardProps) {
  const handleDownload = () => {
    // TODO: Implement download functionality
    console.log('Download resume:', resume.id)
  }

  const handleDownloadCoverLetter = () => {
    // TODO: Implement cover letter download
    console.log('Download cover letter:', resume.id)
  }

  const handleDelete = () => {
    // TODO: Implement delete functionality
    console.log('Delete resume:', resume.id)
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
        >
          <Download className="mr-2 h-4 w-4" />
          Resume
        </Button>

        <Button
          size="sm"
          variant="outline"
          onClick={handleDownloadCoverLetter}
          disabled={!resume.hasCoverLetter}
          className={resume.hasCoverLetter ? '' : 'opacity-50 cursor-not-allowed'}
        >
          <Mail className="h-4 w-4" />
        </Button>

        <Button
          size="sm"
          variant="ghost"
          onClick={handleDelete}
        >
          <Trash2 className="h-4 w-4 text-destructive" />
        </Button>
      </CardFooter>
    </Card>
  )
}

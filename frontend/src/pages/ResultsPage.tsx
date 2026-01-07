import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ArrowLeft, Download, Eye, Share, FileText, Mail } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

// Mock result data
const mockResult = {
  resumeId: 'res_123',
  improvements: [
    'Added Kubernetes experience to match job requirements',
    'Quantified achievements with specific metrics',
    'Improved formatting for better ATS readability',
    'Optimized keyword density for better matching'
  ],
  optimizedResumeUrl: '/api/resumes/res_123/download',
  coverLetterUrl: '/api/resumes/res_123/cover-letter',
  analysisResult: {
    atsScore: 94,
    matchedSkills: ['React', 'TypeScript', 'Node.js', 'Python', 'AWS', 'Docker', 'Kubernetes'],
    missingSkills: [],
    recommendations: []
  }
}

export function ResultsPage() {
  const navigate = useNavigate()
  const [isDownloading, setIsDownloading] = useState<'resume' | 'cover' | null>(null)

  const handleDownloadResume = async () => {
    setIsDownloading('resume')
    try {
      // TODO: Implement actual download
      const response = await fetch(mockResult.optimizedResumeUrl)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'optimized_resume.pdf'
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Download failed:', error)
    } finally {
      setIsDownloading(null)
    }
  }

  const handleDownloadCoverLetter = async () => {
    setIsDownloading('cover')
    try {
      // TODO: Implement actual download
      const response = await fetch(mockResult.coverLetterUrl)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'cover_letter.pdf'
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Download failed:', error)
    } finally {
      setIsDownloading(null)
    }
  }

  const handlePreview = () => {
    // TODO: Implement preview functionality
    window.open(mockResult.optimizedResumeUrl, '_blank')
  }

  const handleShare = () => {
    // TODO: Implement share functionality
    if (navigator.share) {
      navigator.share({
        title: 'My Optimized Resume',
        text: 'Check out my newly optimized resume!',
        url: window.location.href
      })
    } else {
      navigator.clipboard.writeText(window.location.href)
    }
  }

  const handleBackToDashboard = () => {
    navigate('/dashboard')
  }

  const handleCreateNew = () => {
    navigate('/optimize')
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" onClick={() => navigate('/analysis')}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Optimization Complete!</h1>
          <p className="text-muted-foreground">Your resume has been successfully optimized</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Optimized Resume
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded-lg">
                <div>
                  <div className="text-sm font-medium text-green-800">ATS Score</div>
                  <div className="text-2xl font-bold text-green-900">
                    {mockResult.analysisResult.atsScore}%
                  </div>
                </div>
                <Badge variant="default" className="bg-green-500">
                  Excellent
                </Badge>
              </div>

              <div className="space-y-3">
                <h3 className="font-semibold">Improvements Made:</h3>
                <ul className="space-y-2">
                  {mockResult.improvements.map((improvement, index) => (
                    <li key={index} className="flex items-start gap-2 text-sm">
                      <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0" />
                      {improvement}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="flex gap-3 pt-4">
                <Button
                  onClick={handleDownloadResume}
                  disabled={isDownloading === 'resume'}
                  className="flex-1"
                >
                  <Download className="mr-2 h-4 w-4" />
                  {isDownloading === 'resume' ? 'Downloading...' : 'Download Resume'}
                </Button>
                <Button variant="outline" onClick={handlePreview}>
                  <Eye className="mr-2 h-4 w-4" />
                  Preview
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mail className="h-5 w-5" />
                Cover Letter
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                A personalized cover letter has been generated based on your resume and the job description.
              </p>
              <Button
                onClick={handleDownloadCoverLetter}
                disabled={isDownloading === 'cover'}
                variant="outline"
                className="w-full"
              >
                <Download className="mr-2 h-4 w-4" />
                {isDownloading === 'cover' ? 'Downloading...' : 'Download Cover Letter'}
              </Button>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button onClick={handleShare} variant="outline" className="w-full">
                <Share className="mr-2 h-4 w-4" />
                Share Results
              </Button>
              <Button onClick={handleCreateNew} variant="outline" className="w-full">
                <FileText className="mr-2 h-4 w-4" />
                Create New Resume
              </Button>
              <Button onClick={handleBackToDashboard} className="w-full">
                <FileText className="mr-2 h-4 w-4" />
                Back to Dashboard
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Skills Match</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="text-sm">
                <div className="flex justify-between mb-2">
                  <span>Matched Skills</span>
                  <Badge variant="default">
                    {mockResult.analysisResult.matchedSkills.length}
                  </Badge>
                </div>
                <div className="flex flex-wrap gap-1">
                  {mockResult.analysisResult.matchedSkills.map((skill) => (
                    <Badge key={skill} variant="secondary" className="text-xs">
                      {skill}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

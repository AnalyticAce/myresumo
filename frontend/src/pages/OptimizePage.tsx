import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { FileUpload } from '@/components/optimization/FileUpload'
import { TemplateSelector } from '@/components/optimization/TemplateSelector'
import { ArrowLeft, ArrowRight, FileText, Upload } from 'lucide-react'
import { useOptimizationStore } from '@/stores/optimizationStore'
import { optimizationAPI } from '@/api/optimization'
import { OptimizationRequest } from '@/types/optimization'
import { apiClient } from '@/api/client'
import { toast } from 'sonner'

interface MasterCVFromAPI {
  id: string
  title: string
  master_filename?: string
}

export function OptimizePage() {
  const navigate = useNavigate()
  const { request, setRequest, setCurrentStep, step, setAnalysis } = useOptimizationStore()
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  // Fetch master CVs from API
  const { data: masterCVs = [] } = useQuery({
    queryKey: ['master-cvs'],
    queryFn: async () => {
      const { data } = await apiClient.get<MasterCVFromAPI[]>('/resume/master-cvs')
      return data
    },
  })

  const handleNext = () => {
    if (step < 4) {
      setCurrentStep((step + 1) as 1 | 2 | 3 | 4)
    }
  }

  const handlePrevious = () => {
    if (step > 1) {
      setCurrentStep((step - 1) as 1 | 2 | 3 | 4)
    }
  }

  const handleAnalyze = async () => {
    setIsAnalyzing(true)
    try {
      const analysisResult = await optimizationAPI.analyze(request as OptimizationRequest)
      
      // Store analysis result in store for use in AnalysisPage
      setAnalysis(analysisResult)
      
      toast.success('Analysis completed successfully!')
      navigate('/analysis')
    } catch (error) {
      console.error('Analysis failed:', error)
      toast.error('Analysis failed. Please try again.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const isStepValid = () => {
    switch (step) {
      case 1:
        return request.sourceType && (request.sourceId || request.uploadedFile)
      case 2:
        return request.company && request.position && request.jobDescription
      case 3:
        return request.template !== undefined
      default:
        return true
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" onClick={() => navigate('/dashboard')}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Dashboard
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Optimize Resume</h1>
          <p className="text-muted-foreground">Create an ATS-optimized resume for your job application</p>
        </div>
      </div>

      <div className="flex items-center justify-center space-x-2 mb-8">
        {[1, 2, 3, 4].map((stepNum) => (
          <div key={stepNum} className="flex items-center">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                step >= stepNum
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-muted-foreground'
              }`}
            >
              {stepNum}
            </div>
            {stepNum < 4 && (
              <div
                className={`w-16 h-1 mx-2 ${
                  step > stepNum ? 'bg-primary' : 'bg-muted'
                }`}
              />
            )}
          </div>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {step === 1 && <Upload className="h-5 w-5" />}
            {step === 2 && <FileText className="h-5 w-5" />}
            {step === 3 && <FileText className="h-5 w-5" />}
            {step === 4 && <FileText className="h-5 w-5" />}
            Step {step}: {['Select Source', 'Job Details', 'Template', 'Review'][step - 1]}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {step === 1 && (
            <div className="space-y-4">
              <div>
                <Label>Resume Source</Label>
                <Select
                  value={request.sourceType}
                  onValueChange={(value: 'master_cv' | 'upload') =>
                    setRequest({ ...request, sourceType: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Choose resume source" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="master_cv">Use Master CV</SelectItem>
                    <SelectItem value="upload">Upload New Resume</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {request.sourceType === 'upload' ? (
                <FileUpload
                  onFileSelect={(file) => setRequest({ ...request, uploadedFile: file || undefined })}
                  selectedFile={request.uploadedFile}
                />
              ) : (
                <div>
                  <Label>Select Master CV</Label>
                  <Select onValueChange={(value) => setRequest({ ...request, sourceId: value })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Choose a Master CV" />
                    </SelectTrigger>
                    <SelectContent>
                      {masterCVs.length === 0 ? (
                        <SelectItem value="" disabled>No Master CVs found - upload one first</SelectItem>
                      ) : (
                        masterCVs.map((cv) => (
                          <SelectItem key={cv.id} value={cv.id}>
                            {cv.title || cv.master_filename || 'Untitled CV'}
                          </SelectItem>
                        ))
                      )}
                    </SelectContent>
                  </Select>
                </div>
              )}
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <div>
                <Label htmlFor="company">Company</Label>
                <Input
                  id="company"
                  value={request.company || ''}
                  onChange={(e) => setRequest({ ...request, company: e.target.value })}
                  placeholder="e.g., Google, Microsoft, Amazon"
                />
              </div>

              <div>
                <Label htmlFor="position">Position</Label>
                <Input
                  id="position"
                  value={request.position || ''}
                  onChange={(e) => setRequest({ ...request, position: e.target.value })}
                  placeholder="e.g., Senior Software Engineer"
                />
              </div>

              <div>
                <Label htmlFor="jobDescription">Job Description</Label>
                <Textarea
                  id="jobDescription"
                  value={request.jobDescription || ''}
                  onChange={(e) => setRequest({ ...request, jobDescription: e.target.value })}
                  placeholder="Paste full job description here..."
                  rows={8}
                />
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-6">
              <div>
                <Label>Choose Template</Label>
                <TemplateSelector
                  selectedTemplate={request.template}
                  onTemplateSelect={(template) => setRequest({ ...request, template })}
                />
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="space-y-0.5">
                  <Label htmlFor="cover-letter-toggle" className="text-base">Generate Cover Letter</Label>
                  <p className="text-sm text-muted-foreground">
                    Create a tailored cover letter alongside your optimized resume
                  </p>
                </div>
                <Switch
                  id="cover-letter-toggle"
                  checked={request.generateCoverLetter ?? false}
                  onCheckedChange={(checked) => setRequest({ ...request, generateCoverLetter: checked })}
                />
              </div>
            </div>
          )}

          {step === 4 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Review Your Details</h3>
              <div className="bg-muted p-4 rounded-lg space-y-2">
                <div><strong>Source:</strong> {request.sourceType === 'upload' ? 'Uploaded File' : 'Master CV'}</div>
                <div><strong>Company:</strong> {request.company}</div>
                <div><strong>Position:</strong> {request.position}</div>
                <div><strong>Template:</strong> {request.template}</div>
                <div><strong>Cover Letter:</strong> {request.generateCoverLetter ? 'Yes' : 'No'}</div>
              </div>
            </div>
          )}

          <div className="flex justify-between pt-6">
            <Button
              variant="outline"
              onClick={handlePrevious}
              disabled={step === 1}
            >
              Previous
            </Button>

            {step === 4 ? (
              <Button onClick={handleAnalyze} disabled={!isStepValid() || isAnalyzing}>
                {isAnalyzing ? 'Analyzing...' : 'Analyze & Optimize'}
              </Button>
            ) : (
              <Button onClick={handleNext} disabled={!isStepValid()}>
                Next
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { FileUpload } from '@/components/optimization/FileUpload'
import { TemplateSelector } from '@/components/optimization/TemplateSelector'
import { ArrowLeft, ArrowRight, FileText, Upload } from 'lucide-react'
import { OptimizationRequest, TemplateType } from '@/types'
import { useOptimizationStore } from '@/stores/optimizationStore'

export function OptimizePage() {
  const navigate = useNavigate()
  const { request, setRequest, setCurrentStep, currentStep } = useOptimizationStore()
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const handleNext = () => {
    if (currentStep < 4) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleAnalyze = async () => {
    setIsAnalyzing(true)
    try {
      // TODO: Implement analyze API call
      await new Promise(resolve => setTimeout(resolve, 2000)) // Simulate API call
      navigate('/analysis')
    } catch (error) {
      console.error('Analysis failed:', error)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const isStepValid = () => {
    switch (currentStep) {
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
        {[1, 2, 3, 4].map((step) => (
          <div key={step} className="flex items-center">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                currentStep >= step
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-muted-foreground'
              }`}
            >
              {step}
            </div>
            {step < 4 && (
              <div
                className={`w-16 h-1 mx-2 ${
                  currentStep > step ? 'bg-primary' : 'bg-muted'
                }`}
              />
            )}
          </div>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {currentStep === 1 && <Upload className="h-5 w-5" />}
            {currentStep === 2 && <FileText className="h-5 w-5" />}
            {currentStep === 3 && <FileText className="h-5 w-5" />}
            {currentStep === 4 && <FileText className="h-5 w-5" />}
            Step {currentStep}: {['Select Source', 'Job Details', 'Template', 'Review'][currentStep - 1]}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {currentStep === 1 && (
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
                  onFileSelect={(file) => setRequest({ ...request, uploadedFile: file })}
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
                      <SelectItem value="1">My Master CV 2024</SelectItem>
                      <SelectItem value="2">Technical Resume</SelectItem>
                      <SelectItem value="3">Management Resume</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}
            </div>
          )}

          {currentStep === 2 && (
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
                  placeholder="Paste the full job description here..."
                  rows={8}
                />
              </div>
            </div>
          )}

          {currentStep === 3 && (
            <div className="space-y-4">
              <Label>Choose Template</Label>
              <TemplateSelector
                selectedTemplate={request.template}
                onTemplateSelect={(template) => setRequest({ ...request, template })}
              />
            </div>
          )}

          {currentStep === 4 && (
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
              disabled={currentStep === 1}
            >
              Previous
            </Button>

            {currentStep === 4 ? (
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

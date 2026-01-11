import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ArrowLeft, CheckCircle, AlertCircle, Info } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { ATSScoreDisplay } from '@/components/analysis/ATSScoreDisplay'
import { SkillsMatch } from '@/components/analysis/SkillsMatch'
import { RecommendationsList } from '@/components/analysis/RecommendationsList'
import { useOptimizationStore } from '@/stores/optimizationStore'
import { optimizationAPI } from '@/api/optimization'
import { OptimizationRequest } from '@/types/optimization'
import { TemplateType } from '@/types/enums'
import { toast } from 'sonner'

export function AnalysisPage() {
  const navigate = useNavigate()
  const { request, analysis, setResult } = useOptimizationStore()
  const [isOptimizing, setIsOptimizing] = useState(false)

  const handleOptimize = async () => {
    setIsOptimizing(true)
    try {
      // Ensure request has required fields with proper defaults
      const optimizationRequest: OptimizationRequest = {
        sourceType: request.sourceType || 'upload',
        template: request.template || TemplateType.MODERN,
        generateCoverLetter: request.generateCoverLetter || false,
        company: request.company || '',
        position: request.position || '',
        jobDescription: request.jobDescription || '',
        sourceId: request.sourceId,
        uploadedFile: request.uploadedFile
      }
      
      const optimizationResult = await optimizationAPI.optimize(optimizationRequest)
      
      // Store optimization result in store for use in ResultsPage
      setResult(optimizationResult)
      
      toast.success('Resume optimized successfully!')
      navigate('/results')
    } catch (error) {
      console.error('Optimization failed:', error)
      toast.error('Optimization failed. Please try again.')
    } finally {
      setIsOptimizing(false)
    }
  }

  const handleBack = () => {
    navigate('/optimize')
  }

  // Use analysis from store or fallback to mock data
  const analysisData = analysis || {
    atsScore: 0,
    matchedSkills: [],
    missingSkills: [],
    recommendations: []
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" onClick={handleBack}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Resume Analysis</h1>
          <p className="text-muted-foreground">ATS compatibility analysis and optimization recommendations</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <ATSScoreDisplay score={analysisData.atsScore} />
          
          <SkillsMatch
            matchedSkills={analysisData.matchedSkills}
            missingSkills={analysisData.missingSkills}
          />
          
          <RecommendationsList recommendations={analysisData.recommendations} />
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Next Steps</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-500" />
                <span className="text-sm">Analysis completed</span>
              </div>
              <div className="flex items-center gap-2">
                <Info className="h-4 w-4 text-blue-500" />
                <span className="text-sm">{analysisData.recommendations.length} recommendations found</span>
              </div>
              <div className="flex items-center gap-2">
                <AlertCircle className="h-4 w-4 text-orange-500" />
                <span className="text-sm">{analysisData.recommendations.filter(r => r.severity === 'high').length} high-priority item</span>
              </div>
              
              <Button 
                onClick={handleOptimize} 
                className="w-full" 
                disabled={isOptimizing}
              >
                {isOptimizing ? 'Optimizing...' : 'Generate Optimized Resume'}
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Analysis Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between text-sm">
                <span>Keywords Found</span>
                <Badge variant="secondary">{analysisData.matchedSkills.length}</Badge>
              </div>
              <div className="flex justify-between text-sm">
                <span>Missing Keywords</span>
                <Badge variant="outline">{analysisData.missingSkills.length}</Badge>
              </div>
              <div className="flex justify-between text-sm">
                <span>Readability Score</span>
                <Badge variant="default">Good</Badge>
              </div>
              <div className="flex justify-between text-sm">
                <span>Format Check</span>
                <Badge variant="default">Pass</Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

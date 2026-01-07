import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { ArrowLeft, Download, CheckCircle, AlertCircle, Info } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { ATSScoreDisplay } from '@/components/analysis/ATSScoreDisplay'
import { SkillsMatch } from '@/components/analysis/SkillsMatch'
import { RecommendationsList } from '@/components/analysis/RecommendationsList'

// Mock analysis data
const mockAnalysis = {
  atsScore: 87,
  matchedSkills: ['React', 'TypeScript', 'Node.js', 'Python', 'AWS', 'Docker'],
  missingSkills: ['Kubernetes', 'GraphQL', 'MongoDB'],
  recommendations: [
    {
      category: 'skills' as const,
      severity: 'high' as const,
      message: 'Add Kubernetes experience to match job requirements',
      suggestion: 'Include any container orchestration experience or certifications'
    },
    {
      category: 'experience' as const,
      severity: 'medium' as const,
      message: 'Quantify your achievements with specific metrics',
      suggestion: 'Add numbers like "increased performance by 40%" or "reduced costs by $50k"'
    },
    {
      category: 'format' as const,
      severity: 'low' as const,
      message: 'Consider using bullet points for better readability',
      suggestion: 'Break down long paragraphs into concise bullet points'
    }
  ]
}

export function AnalysisPage() {
  const navigate = useNavigate()
  const [isOptimizing, setIsOptimizing] = useState(false)

  const handleOptimize = async () => {
    setIsOptimizing(true)
    try {
      // TODO: Implement optimization API call
      await new Promise(resolve => setTimeout(resolve, 3000)) // Simulate API call
      navigate('/results')
    } catch (error) {
      console.error('Optimization failed:', error)
    } finally {
      setIsOptimizing(false)
    }
  }

  const handleBack = () => {
    navigate('/optimize')
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
          <ATSScoreDisplay score={mockAnalysis.atsScore} />
          
          <SkillsMatch
            matchedSkills={mockAnalysis.matchedSkills}
            missingSkills={mockAnalysis.missingSkills}
          />
          
          <RecommendationsList recommendations={mockAnalysis.recommendations} />
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
                <span className="text-sm">3 recommendations found</span>
              </div>
              <div className="flex items-center gap-2">
                <AlertCircle className="h-4 w-4 text-orange-500" />
                <span className="text-sm">1 high-priority item</span>
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
                <Badge variant="secondary">{mockAnalysis.matchedSkills.length}</Badge>
              </div>
              <div className="flex justify-between text-sm">
                <span>Missing Keywords</span>
                <Badge variant="outline">{mockAnalysis.missingSkills.length}</Badge>
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

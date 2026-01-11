import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { AlertTriangle, Info, CheckCircle, AlertCircle } from 'lucide-react'
import { Recommendation } from '@/types/optimization'

interface RecommendationsListProps {
  recommendations: Recommendation[]
  className?: string
}

const getSeverityIcon = (severity: Recommendation['severity']) => {
  switch (severity) {
    case 'high':
      return <AlertTriangle className="h-4 w-4 text-red-500" />
    case 'medium':
      return <AlertCircle className="h-4 w-4 text-yellow-500" />
    case 'low':
      return <Info className="h-4 w-4 text-blue-500" />
  }
}

const getSeverityColor = (severity: Recommendation['severity']) => {
  switch (severity) {
    case 'high':
      return 'border-red-200 bg-red-50'
    case 'medium':
      return 'border-yellow-200 bg-yellow-50'
    case 'low':
      return 'border-blue-200 bg-blue-50'
  }
}

const getSeverityBadgeColor = (severity: Recommendation['severity']) => {
  switch (severity) {
    case 'high':
      return 'bg-red-100 text-red-800 border-red-200'
    case 'medium':
      return 'bg-yellow-100 text-yellow-800 border-yellow-200'
    case 'low':
      return 'bg-blue-100 text-blue-800 border-blue-200'
  }
}

const getCategoryIcon = (category: Recommendation['category']) => {
  switch (category) {
    case 'skills':
      return ''
    case 'experience':
      return ''
    case 'education':
      return ''
    case 'format':
      return ''
  }
}

export function RecommendationsList({ recommendations, className = '' }: RecommendationsListProps) {
  const groupedRecommendations = recommendations.reduce((acc, rec) => {
    if (!acc[rec.category]) {
      acc[rec.category] = []
    }
    acc[rec.category].push(rec)
    return acc
  }, {} as Record<Recommendation['category'], Recommendation[]>)

  const severityCount = recommendations.reduce((acc, rec) => {
    acc[rec.severity] = (acc[rec.severity] || 0) + 1
    return acc
  }, {} as Record<Recommendation['severity'], number>)

  if (recommendations.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-500" />
            Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Excellent!</h3>
            <p className="text-muted-foreground">
              Your resume is well-optimized with no critical recommendations.
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            Recommendations ({recommendations.length})
          </span>
          <div className="flex gap-2">
            {severityCount.high > 0 && (
              <Badge variant="destructive" className="text-xs">
                {severityCount.high} High
              </Badge>
            )}
            {severityCount.medium > 0 && (
              <Badge variant="secondary" className="text-xs">
                {severityCount.medium} Medium
              </Badge>
            )}
            {severityCount.low > 0 && (
              <Badge variant="outline" className="text-xs">
                {severityCount.low} Low
              </Badge>
            )}
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {Object.entries(groupedRecommendations).map(([category, recs]) => (
          <div key={category} className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="text-lg">{getCategoryIcon(category as Recommendation['category'])}</span>
              <h3 className="font-semibold capitalize">{category}</h3>
              <Badge variant="outline" className="text-xs">
                {recs.length}
              </Badge>
            </div>
            
            <div className="space-y-3">
              {recs.map((recommendation, index) => (
                <div
                  key={index}
                  className={`p-4 rounded-lg border ${getSeverityColor(recommendation.severity)}`}
                >
                  <div className="flex items-start gap-3">
                    {getSeverityIcon(recommendation.severity)}
                    <div className="flex-1 space-y-2">
                      <div className="flex items-center gap-2">
                        <Badge className={getSeverityBadgeColor(recommendation.severity)}>
                          {recommendation.severity}
                        </Badge>
                      </div>
                      <p className="font-medium">{recommendation.message}</p>
                      <p className="text-sm text-muted-foreground">
                         {recommendation.suggestion}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

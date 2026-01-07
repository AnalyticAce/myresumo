import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { getATSScoreColor, getATSScoreLabel, ATS_SCORE_THRESHOLDS } from '@/utils/constants'

interface ATSScoreDisplayProps {
  score: number
  previousScore?: number
  className?: string
}

export function ATSScoreDisplay({ score, previousScore, className = '' }: ATSScoreDisplayProps) {
  const scoreColor = getATSScoreColor(score)
  const scoreLabel = getATSScoreLabel(score)
  const scorePercentage = Math.min(score, 100)

  const getTrendIcon = () => {
    if (!previousScore) return null
    if (score > previousScore) return <TrendingUp className="h-4 w-4 text-green-500" />
    if (score < previousScore) return <TrendingDown className="h-4 w-4 text-red-500" />
    return <Minus className="h-4 w-4 text-gray-500" />
  }

  const getScoreMessage = () => {
    if (score >= ATS_SCORE_THRESHOLDS.EXCELLENT) {
      return "Excellent! Your resume is highly optimized for ATS systems."
    }
    if (score >= ATS_SCORE_THRESHOLDS.GOOD) {
      return "Good! Your resume is well-optimized with room for improvement."
    }
    if (score >= ATS_SCORE_THRESHOLDS.FAIR) {
      return "Fair. Consider optimizing key areas for better ATS compatibility."
    }
    return "Poor. Significant improvements needed for ATS compatibility."
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          ATS Compatibility Score
          {getTrendIcon()}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`text-3xl font-bold ${scoreColor}`}>
              {scorePercentage}%
            </div>
            <div>
              <Badge variant={score >= ATS_SCORE_THRESHOLDS.GOOD ? "default" : "destructive"}>
                {scoreLabel}
              </Badge>
              {previousScore && (
                <div className="text-sm text-muted-foreground mt-1">
                  Previous: {previousScore}%
                </div>
              )}
            </div>
          </div>
        </div>

        <Progress value={scorePercentage} className="h-3" />

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <div className="font-medium">Keyword Match</div>
            <div className="text-muted-foreground">85%</div>
          </div>
          <div>
            <div className="font-medium">Format Score</div>
            <div className="text-muted-foreground">92%</div>
          </div>
          <div>
            <div className="font-medium">Readability</div>
            <div className="text-muted-foreground">78%</div>
          </div>
          <div>
            <div className="font-medium">Structure</div>
            <div className="text-muted-foreground">88%</div>
          </div>
        </div>

        <div className="p-3 bg-muted rounded-lg">
          <p className="text-sm">{getScoreMessage()}</p>
        </div>
      </CardContent>
    </Card>
  )
}

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { CheckCircle, XCircle, Plus } from 'lucide-react'

interface SkillsMatchProps {
  matchedSkills: string[]
  missingSkills: string[]
  className?: string
}

export function SkillsMatch({ matchedSkills, missingSkills, className = '' }: SkillsMatchProps) {
  const matchPercentage = matchedSkills.length > 0 
    ? Math.round((matchedSkills.length / (matchedSkills.length + missingSkills.length)) * 100)
    : 0

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Skills Analysis</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="text-center">
          <div className="text-2xl font-bold text-primary mb-1">
            {matchPercentage}%
          </div>
          <p className="text-sm text-muted-foreground">
            Skills Match Rate
          </p>
        </div>

        <div className="space-y-4">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <h3 className="font-semibold text-green-700">
                Matched Skills ({matchedSkills.length})
              </h3>
            </div>
            <div className="flex flex-wrap gap-2">
              {matchedSkills.map((skill) => (
                <Badge key={skill} variant="default" className="bg-green-100 text-green-800 border-green-200">
                  {skill}
                </Badge>
              ))}
            </div>
          </div>

          {missingSkills.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <XCircle className="h-4 w-4 text-red-500" />
                <h3 className="font-semibold text-red-700">
                  Missing Skills ({missingSkills.length})
                </h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {missingSkills.map((skill) => (
                  <Badge key={skill} variant="outline" className="text-red-600 border-red-200">
                    <Plus className="h-3 w-3 mr-1" />
                    {skill}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="p-3 bg-muted rounded-lg">
          <div className="text-sm space-y-1">
            <div className="flex justify-between">
              <span>Total Skills Analyzed:</span>
              <span className="font-medium">{matchedSkills.length + missingSkills.length}</span>
            </div>
            <div className="flex justify-between">
              <span>Match Score:</span>
              <span className="font-medium">{matchPercentage}%</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

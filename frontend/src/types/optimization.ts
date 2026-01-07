import { TemplateType } from './enums'

export interface OptimizationRequest {
  sourceType: 'master_cv' | 'upload'
  sourceId?: string
  uploadedFile?: File
  company: string
  position: string
  jobDescription: string
  template: TemplateType
  generateCoverLetter: boolean
}

export interface AnalysisResult {
  atsScore: number
  matchedSkills: string[]
  missingSkills: string[]
  recommendations: Recommendation[]
}

export interface Recommendation {
  category: 'skills' | 'experience' | 'education' | 'format'
  severity: 'high' | 'medium' | 'low'
  message: string
  suggestion: string
}

export interface OptimizationResult {
  resumeId: string
  improvements: string[]
  optimizedResumeUrl: string
  coverLetterUrl?: string
  analysisResult: AnalysisResult
}

export interface OptimizationState {
  step: 1 | 2 | 3 | 4
  request: Partial<OptimizationRequest>
  analysis?: AnalysisResult
  result?: OptimizationResult
  isProcessing: boolean
  error?: string
}

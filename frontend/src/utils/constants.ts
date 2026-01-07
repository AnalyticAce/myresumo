export const API_ENDPOINTS = {
  RESUMES: '/resumes',
  MASTER_CVS: '/master-cvs',
  OPTIMIZATION: '/optimization',
  AUTH: '/auth',
} as const

export const FILE_TYPES = {
  PDF: 'application/pdf',
  DOCX: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  DOC: 'application/msword',
} as const

export const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

export const TEMPLATES = {
  MODERN: 'modern',
  CLASSIC: 'classic',
  PROFESSIONAL: 'professional',
  CREATIVE: 'creative',
  MINIMAL: 'minimal',
} as const

export const RESUME_STATUS = {
  NOT_APPLIED: 'not_applied',
  APPLIED: 'applied',
  ANSWERED: 'answered',
  REJECTED: 'rejected',
  INTERVIEW: 'interview',
} as const

export const ATS_SCORE_THRESHOLDS = {
  EXCELLENT: 90,
  GOOD: 75,
  FAIR: 60,
  POOR: 0,
} as const

export const getATSScoreColor = (score: number): string => {
  if (score >= ATS_SCORE_THRESHOLDS.EXCELLENT) return 'text-green-600'
  if (score >= ATS_SCORE_THRESHOLDS.GOOD) return 'text-blue-600'
  if (score >= ATS_SCORE_THRESHOLDS.FAIR) return 'text-yellow-600'
  return 'text-red-600'
}

export const getATSScoreLabel = (score: number): string => {
  if (score >= ATS_SCORE_THRESHOLDS.EXCELLENT) return 'Excellent'
  if (score >= ATS_SCORE_THRESHOLDS.GOOD) return 'Good'
  if (score >= ATS_SCORE_THRESHOLDS.FAIR) return 'Fair'
  return 'Poor'
}

import { apiClient } from './client'
import { OptimizationRequest, AnalysisResult, OptimizationResult, Recommendation } from '@/types/optimization'

// Backend response structure - keywords can be strings or objects
interface KeywordItem {
  keyword: string
  category?: string
  priority?: string
}

interface BackendAnalysisResponse {
  ats_score?: number
  keyword_analysis?: {
    matched_keywords?: Array<KeywordItem | string>
    missing_critical?: Array<KeywordItem | string>
  }
  recommendations?: string[]
  summary?: string
}

// Helper to get CV text from either uploaded file or Master CV
async function getCvText(request: OptimizationRequest): Promise<string> {
  // If user uploaded a file directly
  if (request.uploadedFile) {
    return await request.uploadedFile.text()
  }

  // If user selected a Master CV, fetch its content
  if (request.sourceType === 'master_cv' && request.sourceId) {
    const { data } = await apiClient.get<{ master_content?: string }>(`/resume/master-cv/${request.sourceId}`)
    return data.master_content || ''
  }

  return ''
}

// Helper to extract keyword string from various formats
function extractKeyword(item: KeywordItem | string): string {
  if (typeof item === 'string') return item
  if (item && typeof item === 'object' && 'keyword' in item) return item.keyword
  return String(item)
}

// Transform backend response to frontend format
function transformAnalysisResponse(data: BackendAnalysisResponse): AnalysisResult {
  const matchedKeywords = data.keyword_analysis?.matched_keywords || []
  const missingKeywords = data.keyword_analysis?.missing_critical || []
  const rawRecommendations = data.recommendations || []

  // Transform recommendations to proper format
  const recommendations: Recommendation[] = rawRecommendations.map((rec, index) => {
    let severity: 'high' | 'medium' | 'low' = 'low'
    if (index === 0) severity = 'high'
    else if (index < 3) severity = 'medium'

    return {
      category: 'skills' as const,
      severity,
      message: typeof rec === 'string' ? rec : String(rec),
      suggestion: ''
    }
  })

  return {
    atsScore: data.ats_score || 0,
    matchedSkills: matchedKeywords.map(extractKeyword),
    missingSkills: missingKeywords.map(extractKeyword),
    recommendations
  }
}

// Transform backend optimization response to frontend format
function transformOptimizationResponse(data: any): OptimizationResult {
  return {
    resumeId: data.resume_id || data.resumeId,
    improvements: data.improvements,
    optimizedResumeUrl: data.optimizedResumeUrl,
    coverLetterUrl: data.coverLetterUrl,
    coverLetter: data.cover_letter || data.coverLetter,
    ats_score: data.ats_score,
    matching_skills: data.matching_skills,
    missing_skills: data.missing_skills,
    analysisResult: data.analysisResult,
    analysis: data.analysis
  }
}

export const optimizationAPI = {
  analyze: async (request: OptimizationRequest) => {
    const cvText = await getCvText(request)
    // Map template enum to actual template path
    const templateMap: Record<string, string> = {
      'modern': 'modern.typ',
      'classic': 'resume.typ',
      'professional': 'brilliant-cv/cv.typ',
      'creative': 'awesome-cv/cv.tex',
      'minimal': 'simple-xd-resume/cv.typ'
    }
    const templatePath = templateMap[request.template] || 'resume.typ'

    const payload = {
      cv_text: cvText,
      jd_text: request.jobDescription,
      generate_cover_letter: false,
      template: templatePath
    }

    const { data } = await apiClient.post<BackendAnalysisResponse>(
      '/v2/analyze',
      payload
    )
    return transformAnalysisResponse(data)
  },

  optimize: async (request: OptimizationRequest) => {
    const cvText = await getCvText(request)
    // Map template enum to actual template path
    const templateMap: Record<string, string> = {
      'modern': 'modern.typ',
      'classic': 'resume.typ',
      'professional': 'brilliant-cv/cv.typ',
      'creative': 'awesome-cv/cv.tex',
      'minimal': 'simple-xd-resume/cv.typ'
    }
    const templatePath = templateMap[request.template] || 'resume.typ'

    const payload = {
      cv_text: cvText,
      jd_text: request.jobDescription,
      generate_cover_letter: request.generateCoverLetter,
      template: templatePath
    }

    const { data } = await apiClient.post(
      '/v2/optimize',
      payload
    )
    return transformOptimizationResponse(data)
  },

  getComprehensiveOptimization: async (request: OptimizationRequest) => {
    const cvText = await getCvText(request)
    // Map template enum to actual template path
    const templateMap: Record<string, string> = {
      'modern': 'modern.typ',
      'classic': 'resume.typ',
      'professional': 'brilliant-cv/cv.typ',
      'creative': 'awesome-cv/cv.tex',
      'minimal': 'simple-xd-resume/cv.typ'
    }
    const templatePath = templateMap[request.template] || 'resume.typ'

    const payload = {
      cv_text: cvText,
      jd_text: request.jobDescription,
      generate_cover_letter: request.generateCoverLetter,
      template: templatePath
    }

    const { data } = await apiClient.post<Record<string, unknown>>(
      '/comprehensive-optimize',
      payload
    )
    return data
  },
}

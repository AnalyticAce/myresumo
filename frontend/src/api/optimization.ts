import { apiClient } from './client'
import { OptimizationRequest, AnalysisResult, OptimizationResult } from '@/types/optimization'

export const optimizationAPI = {
  analyze: async (request: OptimizationRequest) => {
    const cvText = request.uploadedFile ? await request.uploadedFile.text() : ''
    const payload = {
      cv_text: cvText,
      jd_text: request.jobDescription,
      generate_cover_letter: false,
      template: 'resume.typ'
    }

    const { data } = await apiClient.post<AnalysisResult>(
      '/optimize',
      payload
    )
    return data
  },

  optimize: async (request: OptimizationRequest) => {
    const cvText = request.uploadedFile ? await request.uploadedFile.text() : ''
    const payload = {
      cv_text: cvText,
      jd_text: request.jobDescription,
      generate_cover_letter: request.generateCoverLetter,
      template: request.template
    }

    const { data } = await apiClient.post<OptimizationResult>(
      '/optimize',
      payload
    )
    return data
  },

  getComprehensiveOptimization: async (request: OptimizationRequest) => {
    const cvText = request.uploadedFile ? await request.uploadedFile.text() : ''
    const payload = {
      cv_text: cvText,
      jd_text: request.jobDescription,
      generate_cover_letter: request.generateCoverLetter,
      template: request.template
    }

    const { data } = await apiClient.post<Record<string, unknown>>(
      '/api/comprehensive-optimize',
      payload
    )
    return data
  },
}

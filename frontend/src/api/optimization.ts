import { apiClient } from './client'
import { OptimizationRequest, AnalysisResult, OptimizationResult } from '@/types/optimization'
import { ApiResponse } from '@/types/api'

export const optimizationAPI = {
  analyze: async (request: OptimizationRequest) => {
    const formData = new FormData()
    
    if (request.uploadedFile) {
      formData.append('file', request.uploadedFile)
    } else if (request.sourceId) {
      formData.append('masterCvId', request.sourceId)
    }
    
    formData.append('company', request.company)
    formData.append('position', request.position)
    formData.append('jobDescription', request.jobDescription)

    const { data } = await apiClient.post<ApiResponse<AnalysisResult>>(
      '/optimization/analyze',
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    )
    return data.data!
  },

  optimize: async (request: OptimizationRequest) => {
    const formData = new FormData()
    
    if (request.uploadedFile) {
      formData.append('file', request.uploadedFile)
    } else if (request.sourceId) {
      formData.append('masterCvId', request.sourceId)
    }
    
    formData.append('company', request.company)
    formData.append('position', request.position)
    formData.append('jobDescription', request.jobDescription)
    formData.append('template', request.template)
    formData.append('generateCoverLetter', String(request.generateCoverLetter))

    const { data } = await apiClient.post<ApiResponse<OptimizationResult>>(
      '/optimization/optimize',
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    )
    return data.data!
  },
}

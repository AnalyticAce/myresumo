import { apiClient } from './client'
import { Resume, DashboardFilters } from '@/types/resume'
import { ApiResponse, PaginatedResponse } from '@/types/api'

export const resumesAPI = {
  getResumes: async (filters: DashboardFilters, page = 1, pageSize = 20) => {
    const { data } = await apiClient.get<PaginatedResponse<Resume>>('/resumes', {
      params: { ...filters, page, pageSize },
    })
    return data
  },

  getResume: async (id: string) => {
    const { data } = await apiClient.get<ApiResponse<Resume>>(`/resumes/${id}`)
    return data.data!
  },

  updateStatus: async (id: string, status: string) => {
    const { data } = await apiClient.patch<ApiResponse<Resume>>(
      `/resumes/${id}/status`,
      { status }
    )
    return data.data!
  },

  deleteResume: async (id: string) => {
    await apiClient.delete(`/resumes/${id}`)
  },

  downloadResume: async (id: string) => {
    const { data } = await apiClient.get<Blob>(`/resumes/${id}/download`, {
      responseType: 'blob',
    })
    return data
  },

  downloadCoverLetter: async (id: string) => {
    const { data } = await apiClient.get<Blob>(`/resumes/${id}/cover-letter`, {
      responseType: 'blob',
    })
    return data
  },
}

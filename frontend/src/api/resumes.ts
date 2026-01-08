import { apiClient } from './client'
import { Resume, DashboardFilters } from '@/types/resume'
import { PaginatedResponse } from '@/types/api'

export const resumesAPI = {
  getResumes: async (_filters: DashboardFilters, page = 1, pageSize = 20) => {
    const { data } = await apiClient.get<PaginatedResponse<Resume>>('/resume/user/demo-user', {
      params: { page, pageSize },
    })
    return data
  },

  getResume: async (id: string) => {
    const { data } = await apiClient.get<Resume>(`/resume/${id}`)
    return data
  },

  updateStatus: async (id: string, status: string) => {
    const { data } = await apiClient.put<Record<string, unknown>>(
      `/resume/${id}/status/${status}`
    )
    return data
  },

  deleteResume: async (id: string) => {
    await apiClient.delete(`/resume/${id}`)
  },

  downloadResume: async (id: string) => {
    const { data } = await apiClient.get<Blob>(`/resume/${id}/download`, {
      responseType: 'blob',
    })
    return data
  },

  downloadCoverLetter: async (id: string) => {
    const { data } = await apiClient.get<Blob>(`/resume/${id}/cover-letter`, {
      responseType: 'blob',
    })
    return data
  },

  createResume: async (formData: FormData) => {
    const { data } = await apiClient.post<Record<string, string>>('/resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return data
  },

  optimizeResume: async (id: string, jobDescription: string, targetCompany?: string, targetRole?: string) => {
    const { data } = await apiClient.post<Record<string, unknown>>(`/resume/${id}/optimize`, {
      job_description: jobDescription,
      target_company: targetCompany,
      target_role: targetRole,
    })
    return data
  },

  scoreResume: async (id: string, jobDescription: string) => {
    const { data } = await apiClient.post<Record<string, unknown>>(`/resume/${id}/score`, {
      job_description: jobDescription,
    })
    return data
  },

  getTemplates: async () => {
    const { data } = await apiClient.get<Array<Record<string, unknown>>>('/resume/templates')
    return data
  },
}

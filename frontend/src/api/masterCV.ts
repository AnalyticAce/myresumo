import { apiClient } from './client'
import { MasterCV } from '@/types/resume'

export const masterCVAPI = {
  getAll: async () => {
    const { data } = await apiClient.get<MasterCV[]>('/resume/master-cvs')
    return data
  },

  upload: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)

    const { data } = await apiClient.post<Record<string, string>>(
      '/resume/master-cv',
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    )
    return data
  },

  delete: async (id: string) => {
    await apiClient.delete(`/resume/master-cv/${id}`)
  },

  getById: async (id: string) => {
    const { data } = await apiClient.get<MasterCV>(`/resume/master-cv/${id}`)
    return data
  },

  download: async (id: string) => {
    const { data } = await apiClient.get<Blob>(`/resume/master-cv/${id}/download`, {
      responseType: 'blob',
    })
    return data
  },
}
